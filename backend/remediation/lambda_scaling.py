"""
Reserved concurrency recommendation for AWS Lambda throttling remediation.
"""

import math

# Raise the safety buffer over observed RPS from 1.10 to 1.25.
SAFETY_BUFFER_MULTIPLIER = 1.25

# AWS reserved concurrency must be an integer, and we never drop below this
# floor so a sudden traffic spike still has headroom before throttling.
MIN_RESERVED_CONCURRENCY = 10


def calculate_reserved_concurrency(current_throttles, avg_rps):
    """Recommend a reserved concurrency ceiling using a 1.25 safety buffer
    over observed average RPS, with a minimum floor of 10."""
    if avg_rps < 0:
        raise ValueError("avg_rps must be non-negative")
    if current_throttles < 0:
        raise ValueError("current_throttles must be non-negative")

    recommended = math.ceil(avg_rps * SAFETY_BUFFER_MULTIPLIER)
    return max(recommended, MIN_RESERVED_CONCURRENCY)
