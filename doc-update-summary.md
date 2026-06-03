# Documentation Update Summary

- **What changed:** `calculate_reserved_concurrency` in `backend/remediation/lambda_scaling.py` raised the safety buffer over observed average RPS from `1.10` to `1.25` (`SAFETY_BUFFER_MULTIPLIER = 1.25`) and the minimum floor from `5` to `10` (`MIN_RESERVED_CONCURRENCY = 10`).
- **Why:** A larger buffer and higher floor give the throttled `payments-processor-prod` Lambda more headroom for traffic spikes, reducing the risk of continued throttling at peak; the new `tests/test_lambda_scaling.py` contract codifies these values.
- **`docs/lambda-throttling.md`:** Updated the worked example output from `44 (max(5, ceil(40 * 1.10)))` to `50 (max(10, ceil(40 * 1.25)))`, and retitled/rewrote the "Why a 1.10 safety buffer?" and "Why a floor of 5?" sections to `1.25` and `10` respectively.
- **`docs/remediation-playbooks.md`:** Updated the "Recommendation logic" rules to state the `1.25` safety multiplier and the minimum floor of `10`.
- **Return type unchanged:** The function still returns an integer (`math.ceil` + `max`), so the existing "integer return value" guidance in the playbook remains accurate and needed no edit.
- **Not modified:** README references to reserved concurrency `10` and the `10 → 20` example describe the demo Lambda's provisioned configuration, not the buffer/floor logic, so they were left untouched.
