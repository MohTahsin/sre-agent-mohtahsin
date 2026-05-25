# Documentation Update Summary

Triggered by recent changes under `backend/` that finalised the corrected
`calculate_reserved_concurrency` implementation in
`backend/remediation/lambda_scaling.py`.

- Verified `docs/lambda-throttling.md` against the merged code: the worked
  example (`avg_rps=40.0 → 50`), the `ceil(avg_rps * 1.25)` formula, the
  floor-of-10 rationale, and the `cappedByAccountQuota` account-safety note
  all already match the implementation, so no edits were required there.
- Verified `README.md`: it does not reference `calculate_reserved_concurrency`
  directly, and its "reserved concurrency from `10` to `20`" description still
  matches `backend/tools.py` (`DESIRED = 20`), so no edits were required.
- Updated `docs/remediation-playbooks.md` "Recommendation logic" section to
  call out that the integer return is produced via `math.ceil` and that
  negative `avg_rps` / `current_throttles` now raise `ValueError`, which
  reflects the validation guards in the merged function.
- Left `DEMO.md` unchanged: its `return avg_rps * 0.5` snippet is the
  intentionally-buggy reference for the demo narrative, not a description of
  current behaviour.
- No changes were needed to operational guidance ("What to monitor after
  remediation", playbook steps, failure modes) — the merged behaviour matches
  the existing wording.
