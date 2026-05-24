"""
Reserved concurrency recommendation for AWS Lambda throttling remediation.

Used by the SRE agent to suggest a safe new reserved concurrency value when
recommending a fix for the payments-processor-prod throttling incident.
"""

import math

MIN_RESERVED_CONCURRENCY = 10
SAFETY_BUFFER = 1.25


def calculate_reserved_concurrency(current_throttles: int, avg_rps: float) -> int:
    """
    Recommend a reserved concurrency setting for a throttled Lambda.

    Returns an integer >= MIN_RESERVED_CONCURRENCY, sized to absorb the observed
    average RPS plus a safety buffer for traffic variance.
    """
    if avg_rps < 0:
        raise ValueError("avg_rps must be non-negative")
    if current_throttles < 0:
        raise ValueError("current_throttles must be non-negative")

    target = math.ceil(avg_rps * SAFETY_BUFFER)
    return max(MIN_RESERVED_CONCURRENCY, target)
