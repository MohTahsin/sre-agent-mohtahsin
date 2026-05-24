import math

import pytest

from backend.remediation.lambda_scaling import calculate_reserved_concurrency

MIN_RESERVED_CONCURRENCY = 10


def test_returns_integer():
    result = calculate_reserved_concurrency(current_throttles=5, avg_rps=40.0)
    assert isinstance(result, int), "Reserved concurrency must be an integer (AWS API requirement)"


def test_enforces_minimum_floor_for_low_traffic():
    result = calculate_reserved_concurrency(current_throttles=0, avg_rps=1.0)
    assert result >= MIN_RESERVED_CONCURRENCY, (
        f"Reserved concurrency must never drop below {MIN_RESERVED_CONCURRENCY} "
        "to maintain a safety buffer for traffic spikes"
    )


def test_enforces_minimum_floor_at_zero_traffic():
    result = calculate_reserved_concurrency(current_throttles=0, avg_rps=0.0)
    assert result == MIN_RESERVED_CONCURRENCY


def test_applies_safety_buffer_above_observed_rps():
    avg_rps = 40.0
    result = calculate_reserved_concurrency(current_throttles=12, avg_rps=avg_rps)
    assert result >= math.ceil(avg_rps * 1.25), (
        "Recommendation must add a safety buffer over observed RPS, "
        "otherwise the function will keep throttling at peak"
    )


def test_does_not_recommend_below_observed_load():
    avg_rps = 80.0
    result = calculate_reserved_concurrency(current_throttles=20, avg_rps=avg_rps)
    assert result >= avg_rps, (
        "Recommendation must never be below current average RPS — "
        "doing so would guarantee continued throttling"
    )


@pytest.mark.parametrize(
    "avg_rps,expected_min",
    [
        (10.0, 13),    # 10 * 1.25 = 12.5 → ceil 13
        (50.0, 63),    # 50 * 1.25 = 62.5 → ceil 63
        (100.0, 125),  # 100 * 1.25 = 125
        (250.0, 313),  # 250 * 1.25 = 312.5 → ceil 313
    ],
)
def test_recommendation_for_realistic_loads(avg_rps, expected_min):
    result = calculate_reserved_concurrency(current_throttles=10, avg_rps=avg_rps)
    assert result >= expected_min


def test_rejects_negative_rps():
    with pytest.raises(ValueError):
        calculate_reserved_concurrency(current_throttles=0, avg_rps=-1.0)


def test_rejects_negative_throttles():
    with pytest.raises(ValueError):
        calculate_reserved_concurrency(current_throttles=-1, avg_rps=10.0)
