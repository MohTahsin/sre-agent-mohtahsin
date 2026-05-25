"""
Reserved concurrency recommendation for AWS Lambda throttling remediation.
"""

import math

MIN_RESERVED_CONCURRENCY = 10
SAFETY_BUFFER_MULTIPLIER = 1.25


def calculate_reserved_concurrency(current_throttles, avg_rps):
    """Recommend a reserved concurrency ceiling for a throttled Lambda.

    The recommendation applies a safety buffer over the observed average RPS
    and is clamped to a documented minimum floor so that low-traffic windows
    still leave headroom for bursts. AWS requires an integer value, so the
    return value is always coerced via ``math.ceil``.
    """
    if avg_rps < 0:
        raise ValueError("avg_rps must be non-negative")
    if current_throttles < 0:
        raise ValueError("current_throttles must be non-negative")

    buffered = math.ceil(avg_rps * SAFETY_BUFFER_MULTIPLIER)
    return max(MIN_RESERVED_CONCURRENCY, buffered)
