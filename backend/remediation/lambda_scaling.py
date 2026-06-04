"""
Reserved concurrency recommendation for AWS Lambda throttling remediation.
"""

import math

# Raise the safety buffer over observed RPS from 1.10 to 1.25.
SAFETY_BUFFER_MULTIPLIER = 1.25
MIN_RESERVED_CONCURRENCY = 10


def calculate_reserved_concurrency(current_throttles, avg_rps):
    """Recommend a reserved concurrency ceiling using a 1.25 safety buffer
    over observed average RPS, with a minimum floor of 10."""
    if avg_rps < 0:
        raise ValueError("avg_rps must be non-negative")
    if current_throttles < 0:
        raise ValueError("current_throttles must be non-negative")

    # Calculate: avg_rps * safety buffer, then ceiling to get integer
    recommendation = math.ceil(avg_rps * SAFETY_BUFFER_MULTIPLIER)
    
    # Enforce minimum floor
    return max(recommendation, MIN_RESERVED_CONCURRENCY)
