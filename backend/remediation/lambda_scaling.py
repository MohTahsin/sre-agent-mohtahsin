"""
Reserved concurrency recommendation for AWS Lambda throttling remediation.

The recommendation applies a 25% safety buffer over the observed average RPS
and never drops below ``MIN_RESERVED_CONCURRENCY`` so that brief idle periods
do not leave the function unable to absorb a spike.
"""

import math

MIN_RESERVED_CONCURRENCY = 10
SAFETY_BUFFER = 1.25


def calculate_reserved_concurrency(current_throttles, avg_rps):
    if avg_rps < 0:
        raise ValueError("avg_rps must be non-negative")
    if current_throttles < 0:
        raise ValueError("current_throttles must be non-negative")

    buffered = math.ceil(avg_rps * SAFETY_BUFFER)
    return max(MIN_RESERVED_CONCURRENCY, buffered)
