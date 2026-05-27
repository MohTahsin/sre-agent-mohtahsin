# Documentation update summary

Triggered by the merge of `backend/remediation/lambda_scaling.py` and `pytest-output.txt` to `main`.

- The merge replaced the buggy `calculate_reserved_concurrency` body (`return avg_rps * 0.5`) with the correct implementation: `max(MIN_RESERVED_CONCURRENCY, math.ceil(avg_rps * SAFETY_BUFFER))`, restoring integer return type, the floor of `10`, and the `1.25` safety buffer.
- The fixed implementation also adds **input validation** that raises `ValueError` for negative `avg_rps` or `current_throttles`; this behaviour was not previously described in any doc, so it was added explicitly.
- `docs/lambda-throttling.md` got a new "Input validation" sub-section under the reserved-concurrency reference, framed in the same operational tone as the surrounding "Why a 1.25 safety buffer?" / "Why a floor of 10?" explainers, so the why-rationale style is preserved.
- `docs/remediation-playbooks.md` had its "Recommendation logic" enforcement list extended with the validation rule and clarified that the integer guarantee comes from `math.ceil`; constants are now named (`MIN_RESERVED_CONCURRENCY`, `SAFETY_BUFFER`) to match the source.
- `README.md` was reviewed but **not modified**: it only references `increase_lambda_concurrency` and the hard-coded `10 → 20` demo path, neither of which was affected by this change.
- The committed `pytest-output.txt` reflects the pre-fix failing state and is intentionally left untouched — it is a demo artefact referenced by `DEMO.md` to illustrate the broken-then-fixed flow, not live test output.
