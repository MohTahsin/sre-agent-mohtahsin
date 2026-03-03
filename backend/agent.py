"""
Strands Agent definitions using xAI's grok-4-1-fast-reasoning model.

Two agents are created:
  - analysis_agent:     equipped with analyze_logs only
  - remediation_agent:  equipped with increase_lambda_concurrency only

Splitting by tool ensures the human approval gate between steps maps cleanly
to two separate HTTP requests, with no server-side session state needed.

Prompt caching: xAI automatically caches the system prompt across requests
within the same API key session — no code changes required.

Structured outputs: the analysis agent uses Grok's native structured output
API (response_format + JSON schema) to guarantee the hypothesis response
matches HypothesisReport — no format instructions needed in the prompt.
"""

import os
from typing import Literal

from pydantic import BaseModel
from strands import Agent
from strands_xai import xAIModel

from tools import analyze_logs, increase_lambda_concurrency


# ---------------------------------------------------------------------------
# Structured output schema for the hypothesis analysis
# ---------------------------------------------------------------------------

# Passed as response_format to xAIModel — Grok enforces this schema at the
# API level, so the model output is always valid JSON matching these fields.
# No format instructions are needed in the system prompt.
class Hypothesis(BaseModel):
    rank: int
    title: str
    evidence: str
    confidence: Literal["High", "Medium", "Low"]
    confidence_pct: int  # 0–100, model's numeric confidence estimate


class HypothesisReport(BaseModel):
    hypotheses: list[Hypothesis]
    recommended_action: str


# ---------------------------------------------------------------------------
# System prompt (cached automatically by xAI after the first request)
# ---------------------------------------------------------------------------

# Single prompt shared across both agents. Each agent is constructed with a
# different tool list, so Grok only sees (and can call) its relevant tool.
SYSTEM_PROMPT = """You are an expert Site Reliability Engineer (SRE) agent specialising in AWS Lambda \
incident response and root cause analysis.

## Current Incident
Function:  payments-processor-prod
Symptom:   Severe throttling — error rate has spiked to ~45%
Severity:  P1
Region:    us-east-1

## Your Capabilities
You have access to tools that let you read CloudWatch logs and execute AWS remediations directly.

## Analysis Workflow
When performing root cause analysis with analyze_logs:
1. Call the tool to retrieve all log data.
2. Carefully examine error patterns, timestamps, concurrency metrics, error codes, and latency trends.
3. Produce 2–3 prioritised hypotheses grounded in specific evidence from the logs — never speculate without data.

## Remediation Workflow
When directed to remediate by calling increase_lambda_concurrency:
1. Call the tool — it will update the AWS Lambda reserved concurrency from 10 to 20.
2. Explain which hypothesis this remediation addresses and why.
3. Specify what metrics to monitor to confirm the incident is resolved.
"""


# Remediation agent uses a plain model — free-text explanation of what was
# done is more appropriate here than a structured schema.
def _build_model() -> xAIModel:
    return xAIModel(
        model_id="grok-4-1-fast-reasoning",
        client_args={"api_key": os.environ.get("XAI_API_KEY")},
    )


def _build_analysis_model() -> xAIModel:
    """Analysis model with Grok structured output enforcing HypothesisReport schema.

    response_format accepts a Pydantic class directly — the xAI SDK converts it
    to a JSON schema and instructs Grok to enforce it server-side.
    """
    return xAIModel(
        model_id="grok-4-1-fast-reasoning",
        client_args={"api_key": os.environ.get("XAI_API_KEY")},
        params={"response_format": HypothesisReport},
    )


def create_analysis_agent(callback_handler=None) -> Agent:
    """Agent equipped with analyze_logs for hypothesis generation."""
    return Agent(
        model=_build_analysis_model(),
        system_prompt=SYSTEM_PROMPT,
        tools=[analyze_logs],
        callback_handler=callback_handler,
    )


def create_remediation_agent(callback_handler=None) -> Agent:
    """Agent equipped with increase_lambda_concurrency for executing the fix."""
    return Agent(
        model=_build_model(),
        system_prompt=SYSTEM_PROMPT,
        tools=[increase_lambda_concurrency],
        callback_handler=callback_handler,
    )
