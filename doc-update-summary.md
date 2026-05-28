# Documentation Update Summary

Triggered by the merge of `backend/remediation/lambda_scaling.py` (and `pytest-output.txt`) to `main`.

- **The merged change to `calculate_reserved_concurrency` was a non-behavioral refactor.** Comparing the merged code against the previous `main` baseline, the recommendation logic is identical: `max(ceil(avg_rps * 1.25), 10)`, returning an integer and raising `ValueError` on negative inputs.
- **Verified the documented contract still holds.** `calculate_reserved_concurrency(current_throttles=120, avg_rps=40.0)` still returns `50` (an `int`), the floor of `10` and the `1.25` safety buffer are unchanged, and negative `avg_rps`/`current_throttles` still raise `ValueError`. No example outputs, return-type notes, or operational guidance in `README.md`, `docs/lambda-throttling.md`, or `docs/remediation-playbooks.md` needed correcting.
- **Aligned the derivation note in `docs/lambda-throttling.md`** from `max(10, ceil(40 * 1.25))` to `max(ceil(40 * 1.25), 10)` so it mirrors the new source ordering (`max(recommended, MIN_RESERVED_CONCURRENCY)`). The computed result is unchanged.
- **No constant or error-message references required updates.** The renamed constant (`SAFETY_BUFFER_MULTIPLIER` → `SAFETY_BUFFER`), the reworded `ValueError` messages, and the removed docstring are not surfaced in any documentation, which describes the behavior conceptually ("1.25 safety buffer", "floor of 10", "integer return").
- **Style and structure preserved.** Only the single derivation comment was touched; all section headings, examples, and prose remain in their existing format.
