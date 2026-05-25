# Documentation Update Summary

- The merge of `backend/remediation/lambda_scaling.py` introduced the production implementation of `calculate_reserved_concurrency`, replacing a placeholder that returned `avg_rps * 0.5`. Documentation needed to confirm the now-active recommendation rules.
- `docs/lambda-throttling.md` and `docs/remediation-playbooks.md` already described the `1.25` safety multiplier, floor of `10`, and integer return type, so those sections were left untouched to avoid churn.
- Added a new "Input validation" subsection to `docs/lambda-throttling.md` documenting that `calculate_reserved_concurrency` now raises `ValueError` for negative `avg_rps` or `current_throttles`, since this fail-fast behavior is part of the merged code and was previously undocumented.
- Updated the "Recommendation logic" enforcement list in `docs/remediation-playbooks.md` to include the same input-validation guarantee and to call out that the integer return is produced via `math.ceil`, matching the merged implementation.
- `README.md` was reviewed but not modified: it discusses the demo scenario at a higher level and does not reference the internal recommendation rules that changed.
- The merged `pytest-output.txt` is a captured failing-run artifact for the demo and does not describe runtime behavior, so no documentation references it.
