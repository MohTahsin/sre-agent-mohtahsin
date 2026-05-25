"""
Reserved concurrency recommendation for AWS Lambda throttling remediation.
"""


def calculate_reserved_concurrency(current_throttles, avg_rps):
    return avg_rps * 0.5
