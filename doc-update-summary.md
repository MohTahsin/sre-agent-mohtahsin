# Documentation Update Summary

Reviewed `README.md`, `docs/lambda-throttling.md`, `docs/remediation-playbooks.md`,
and `DEMO.md` against the merged `backend/remediation/lambda_scaling.py`.

- **No behavioral change to document.** The merged `calculate_reserved_concurrency`
  preserves the exact behavior the docs already describe: a `MIN_RESERVED_CONCURRENCY`
  floor of `10`, a `SAFETY_BUFFER` of `1.25`, an integer result via `math.ceil`, and
  `ValueError` on negative `avg_rps` or `current_throttles`.
- **Documented example remains correct.** `calculate_reserved_concurrency(current_throttles=120, avg_rps=40.0)`
  still returns `50` (`max(10, ceil(40 * 1.25))`), so the snippet in
  `docs/lambda-throttling.md` needs no change. Verified by running the function.
- **Return-type note still accurate.** The function continues to return an `int`, so the
  "Integer return value" guidance in `docs/remediation-playbooks.md` and the
  `test_returns_integer` contract both still hold.
- **The merge was a non-behavioral refactor.** Compared to the pre-merge baseline, only
  cosmetic items changed: constant renamed `SAFETY_BUFFER_MULTIPLIER` → `SAFETY_BUFFER`,
  the function docstring and type hints were dropped, and the error-message wording shifted
  from "must be non-negative" to "must not be negative" — none of which the docs reference.
- **No edits made to existing docs.** Per the directive to touch only documentation actually
  affected by the change, `README.md` and the `docs/` playbooks were left unchanged because
  their examples, descriptions, return-type notes, and operational guidance already match
  the merged code.
- **`DEMO.md` intentionally left as-is.** It narrates the demo storyline (a deliberately
  buggy branch fixed on `main`) and does not describe current `main` behavior, so altering
  it would misrepresent the demo flow.
