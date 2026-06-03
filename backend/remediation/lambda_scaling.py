"""
Reserved concurrency recommendation for AWS Lambda throttling remediation.
"""

import math

MIN_RESERVED_CONCURRENCY = 10
SAFETY_BUFFER = 1.25


def calculate_reserved_concurrency(current_throttles, avg_rps):
    if avg_rps < 0:
        raise ValueError("avg_rps must not be negative")
    if current_throttles < 0:
        raise ValueError("current_throttles must not be negative")

    buffered = math.ceil(avg_rps * SAFETY_BUFFER)
    return max(buffered, MIN_RESERVED_CONCURRENCY)
