# Documentation Update Summary

Source change reviewed: `backend/remediation/lambda_scaling.py` (merged to `main`).

- **The merged change is behavior-preserving.** Compared to the previous `main`
  baseline, the diff only renames the constant `SAFETY_BUFFER_MULTIPLIER` →
  `SAFETY_BUFFER`, removes the function docstring, rewords the validation error
  messages ("must be non-negative" → "must not be negative"), and reorders the
  arguments to `max(...)` (which yields an identical result).
- **Observable behavior of `calculate_reserved_concurrency` is unchanged:** a
  `1.25` safety buffer over `avg_rps`, a minimum floor of `10`, an integer return
  via `math.ceil`, and a `ValueError` raised for negative `avg_rps` or
  `current_throttles`.
- **The documented worked example still holds:**
  `calculate_reserved_concurrency(current_throttles=120, avg_rps=40.0)` returns
  `50` (`max(10, ceil(40 * 1.25))`), exactly as shown in
  `docs/lambda-throttling.md`.
- **No documentation content was affected.** `docs/lambda-throttling.md` and
  `docs/remediation-playbooks.md` describe the buffer, floor, integer return
  type, and validation behavior generically; none of them reference the renamed
  constant, the removed docstring, or the literal error-message strings.
- **`README.md` and `DEMO.md` are also unaffected** — they cover the demo
  application flow and the CI/CD remediation walkthrough, not the internal
  recommendation logic, so they remain accurate.
- **Result: no edits were made to existing documentation**, consistent with the
  guidance to only modify docs that are actually affected by the change.
