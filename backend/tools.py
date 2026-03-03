"""
Strands tool definitions for the SRE agent.

Thread-local storage is used to share the SSE event queue with the tool
implementations — this lets each tool emit structured progress events back
to the streaming endpoint without any global state.
"""

import json
import os
import threading

import boto3
from strands import tool

LOGS_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "cloudwatch_logs.json")
FUNCTION_NAME = "payments-processor-prod"

# Thread-local queue: set by the SSE endpoint before spawning the agent thread.
_ctx = threading.local()


def set_event_queue(q):
    """Attach a queue to the current thread so tools can emit SSE events."""
    _ctx.queue = q


def _emit(event: dict):
    # Silent no-op when called outside a request context (e.g. unit tests).
    q = getattr(_ctx, "queue", None)
    if q is not None:
        q.put(event)


# ---------------------------------------------------------------------------
# Tool: analyze_logs
# ---------------------------------------------------------------------------

@tool
def analyze_logs() -> str:
    """
    Read all CloudWatch log events for the payments-processor-prod Lambda function
    and return the raw JSON log data for root cause analysis.
    """
    _emit({"type": "tool_executing", "tool": "analyze_logs", "message": "Reading CloudWatch log events..."})

    if not os.path.exists(LOGS_PATH):
        raise FileNotFoundError(
            f"Log file not found at {LOGS_PATH}. "
            "Run: python scripts/generate_logs.py"
        )

    # Return full raw JSON so the agent has complete log context before reasoning,
    # mirroring a real CloudWatch Insights query response.
    with open(LOGS_PATH, "r") as f:
        logs = json.load(f)

    event_count = len(logs.get("events", []))
    _emit({
        "type": "tool_result",
        "tool": "analyze_logs",
        "summary": f"Loaded {event_count} log events spanning {logs.get('windowStart', '')} → {logs.get('windowEnd', '')}",
    })

    return json.dumps(logs, indent=2)


# ---------------------------------------------------------------------------
# Tool: increase_lambda_concurrency
# ---------------------------------------------------------------------------

@tool
def increase_lambda_concurrency() -> str:
    """
    Increase reserved concurrency of payments-processor-prod toward 20 via the AWS Lambda API.
    Queries account headroom first and caps the target at the safe maximum if needed.
    """
    region = os.environ.get("AWS_REGION", "us-east-1")

    _emit({
        "type": "tool_executing",
        "tool": "increase_lambda_concurrency",
        "message": f"Querying account concurrency limits for {FUNCTION_NAME}...",
    })

    client = boto3.client(
        "lambda",
        region_name=region,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.environ.get("AWS_SESSION_TOKEN"),
    )

    # Get current reserved concurrency for this function
    try:
        current_reserved = client.get_function_concurrency(
            FunctionName=FUNCTION_NAME
        ).get("ReservedConcurrentExecutions", 0) or 0
    except client.exceptions.ResourceNotFoundException:
        current_reserved = 0

    # Get account-level unreserved headroom
    unreserved = client.get_account_settings()["AccountLimit"]["UnreservedConcurrentExecutions"]

    # AWS enforces a floor of 10 unreserved. Net delta = target - current_reserved.
    # Need: unreserved - (target - current_reserved) >= 10
    # → target <= current_reserved + unreserved - 10
    DESIRED = 20
    safe_max = current_reserved + unreserved - 10
    # Capped target degrades gracefully when account quota is tight.
    # cappedByAccountQuota in the result tells the model if it fell short of DESIRED.
    effective_target = min(DESIRED, safe_max)

    if effective_target <= current_reserved:
        raise ValueError(
            f"Insufficient account concurrency headroom: unreserved={unreserved}, "
            f"current_reserved={current_reserved}. Cannot increase concurrency."
        )

    response = client.put_function_concurrency(
        FunctionName=FUNCTION_NAME,
        ReservedConcurrentExecutions=effective_target,
    )
    new_concurrency = response["ReservedConcurrentExecutions"]
    capped = new_concurrency < DESIRED

    result = {
        "status": "success",
        "functionName": FUNCTION_NAME,
        "region": region,
        "previousReservedConcurrency": current_reserved,
        "newReservedConcurrency": new_concurrency,
        "desiredConcurrency": DESIRED,
        "cappedByAccountQuota": capped,
        "accountUnreservedBefore": unreserved,
    }

    suffix = " (capped by account quota)" if capped else ""
    _emit({
        "type": "tool_result",
        "tool": "increase_lambda_concurrency",
        "summary": f"Reserved concurrency set to {new_concurrency}{suffix}",
        "detail": result,
    })

    return json.dumps(result, indent=2)
