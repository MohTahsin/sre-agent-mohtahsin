# Documentation Update Summary

Documentation reconciled against the merged `backend/remediation/lambda_scaling.py`,
where `calculate_reserved_concurrency` replaced the buggy `return avg_rps * 0.5`
with the production logic (floor of `10`, `1.25` safety buffer, integer ceiling, input validation).

- **Verified existing examples are still correct.** `calculate_reserved_concurrency(120, 40.0) -> 50`, the `10` floor, the `1.25` multiplier, the integer return, and the "never below current load" guarantee already match the merged code, so they were left unchanged.
- **Documented the new input validation in `docs/lambda-throttling.md`.** Added a note that negative `avg_rps`/`current_throttles` raise `ValueError` and that the return value is always an `int` — behaviour the buggy branch lacked and that the reference previously omitted.
- **Added an input-validation rule to `docs/remediation-playbooks.md`.** The "Recommendation logic" list now records that negative inputs raise `ValueError`, keeping the runbook's enforced-rules section faithful to the merged function.
- **Left `README.md` untouched.** Its Lambda references describe the demo scenario and the separate `increase_lambda_concurrency` tool (10 → 20 narrative), none of which are affected by this change.
- **Did not modify the account-level safety section** in `docs/lambda-throttling.md`, as it documents `increase_lambda_concurrency`, not the changed function.
- **Preserved existing style and section structure**, making only additive, minimal edits to reflect the merged behaviour.
