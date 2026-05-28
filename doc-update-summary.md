# Documentation Update Summary

- The merge to `main` restored the correct `calculate_reserved_concurrency` logic in `backend/remediation/lambda_scaling.py`, replacing the buggy `avg_rps * 0.5` stub.
- The integer return value, the minimum floor of `10`, and the `1.25` safety buffer were already documented correctly in `docs/lambda-throttling.md` and `docs/remediation-playbooks.md`, and the worked example (`120` throttles / `40.0` RPS → `50`) remains accurate, so those sections were left unchanged.
- The one newly introduced behaviour not previously documented is input validation: the function now raises `ValueError` for a negative `avg_rps` or `current_throttles`.
- Added an "Input validation" subsection to `docs/lambda-throttling.md` explaining that malformed (negative) metric inputs fail fast rather than yielding a bad concurrency ceiling.
- Added a matching bullet to the "Recommendation logic" enforcement list in `docs/remediation-playbooks.md` to keep the two docs consistent.
- `README.md` only references the demo throttling scenario (not the function contract), so no README changes were required.
