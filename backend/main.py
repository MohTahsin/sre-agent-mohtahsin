"""
FastAPI backend for the SRE Agent demo.

Endpoints:
  POST /api/start-incident     — SSE stream: runs analyze_logs agent
  POST /api/approve-remediation — SSE stream: runs increase_lambda_concurrency agent
  GET  /api/health

SSE event schema (JSON):
  { "type": "tool_start",      "tool": str, "message": str }
  { "type": "tool_executing",  "tool": str, "message": str }
  { "type": "tool_result",     "tool": str, "summary": str, "detail"?: obj }
  { "type": "text_chunk",      "content": str }
  { "type": "analysis_complete", "text": str, "hypotheses"?: obj }
  { "type": "remediation_complete", "text": str }
  { "type": "error",           "message": str }
"""

import asyncio
import json
import os
import queue
import threading

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from agent import HypothesisReport, create_analysis_agent, create_remediation_agent
from tools import set_event_queue

app = FastAPI(title="SRE Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


def _make_callback(event_queue: queue.Queue):
    """
    Returns a Strands-compatible callback_handler that forwards streaming
    text chunks and tool-use events to the SSE queue.

    Strands calls this synchronously from the agent thread on each event:
      data             — streaming text chunk from the model
      current_tool_use — dict populated when the model selects a tool
    """
    def callback_handler(**kwargs):
        # Streaming text from the model
        chunk = kwargs.get("data", "")
        if chunk:
            event_queue.put({"type": "text_chunk", "content": chunk})

        # Tool invocation signal (Strands passes current_tool_use when a tool is selected)
        tool_use = kwargs.get("current_tool_use")
        if isinstance(tool_use, dict) and tool_use.get("name"):
            event_queue.put({
                "type": "tool_start",
                "tool": tool_use["name"],
                "message": f"Invoking tool: {tool_use['name']}",
            })

    return callback_handler


async def _stream_agent(agent_runner) -> StreamingResponse:
    """
    Runs agent_runner in a background thread and streams its events as SSE.

    Agent.__call__ is blocking/synchronous. Running it in a thread and bridging
    via run_in_executor keeps FastAPI's async event loop unblocked while the
    agent works, allowing other requests to be served concurrently.
    """
    event_queue: queue.Queue = queue.Queue()

    thread = threading.Thread(target=agent_runner, args=(event_queue,), daemon=True)
    thread.start()

    loop = asyncio.get_event_loop()

    async def generator():
        while True:
            event = await loop.run_in_executor(None, event_queue.get)
            if event is None:
                break
            yield _sse(event)
        thread.join(timeout=5)

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ---------------------------------------------------------------------------
# Agent runners (executed in threads)
# ---------------------------------------------------------------------------

def _run_analysis(event_queue: queue.Queue):
    set_event_queue(event_queue)
    try:
        callback = _make_callback(event_queue)
        agent = create_analysis_agent(callback_handler=callback)

        result = agent(
            "An active P1 incident is underway. Call analyze_logs to read all available "
            "CloudWatch log data, then produce your prioritised hypotheses for the root cause "
            "of the throttling."
        )

        raw = str(result)
        try:
            # Safety net: re-parse the raw string against the schema. Grok's
            # structured output should already be valid, but this fallback to
            # hypotheses=None prevents a hard crash reaching the UI.
            report = HypothesisReport.model_validate_json(raw)
            hypotheses = report.model_dump()
        except Exception:
            hypotheses = None

        try:
            acc = result.metrics.accumulated_usage
            usage = {"inputTokens": acc.get("inputTokens", 0), "outputTokens": acc.get("outputTokens", 0)}
        except Exception:
            usage = {}

        event_queue.put({
            "type": "analysis_complete",
            "text": raw,
            "hypotheses": hypotheses,
            "usage": usage,
        })
    except Exception as exc:
        event_queue.put({"type": "error", "message": str(exc)})
    finally:
        event_queue.put(None)  # sentinel — signals generator to stop


def _run_remediation(event_queue: queue.Queue):
    set_event_queue(event_queue)
    try:
        callback = _make_callback(event_queue)
        agent = create_remediation_agent(callback_handler=callback)

        result = agent(
            "Human approval has been granted. Execute the remediation: call "
            "increase_lambda_concurrency to raise reserved concurrency from 10 to 20. "
            "After the tool call completes, explain what was done and what to monitor."
        )

        try:
            acc = result.metrics.accumulated_usage
            usage = {"inputTokens": acc.get("inputTokens", 0), "outputTokens": acc.get("outputTokens", 0)}
        except Exception:
            usage = {}

        event_queue.put({
            "type": "remediation_complete",
            "text": str(result),
            "usage": usage,
        })
    except Exception as exc:
        event_queue.put({"type": "error", "message": str(exc)})
    finally:
        event_queue.put(None)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/api/start-incident")
async def start_incident():
    return await _stream_agent(_run_analysis)


@app.post("/api/approve-remediation")
async def approve_remediation():
    return await _stream_agent(_run_remediation)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
