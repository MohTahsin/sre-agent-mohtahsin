# Documentation Update Summary

## Changes Made

The following documentation updates reflect the merged Lambda remediation logic improvements:

1. **Safety buffer increased from 1.10x to 1.25x** — Production traffic bursts now up to 1.25x average RPS are accommodated without throttling. Updated example calculations and rationale in `docs/lambda-throttling.md` and `docs/remediation-playbooks.md`.

2. **Minimum reserved concurrency floor increased from 5 to 10** — Stronger baseline protection against sudden load spikes during low-traffic windows. Updated floor descriptions and example outputs across documentation.

3. **Integer enforcement and ceiling math** — The merged code now properly uses `math.ceil()` to round up fractional concurrency values and enforces minimum floor via `max()`, ensuring AWS API compatibility and contract correctness.

4. **Updated documentation files:**
   - `docs/lambda-throttling.md`: Example output (44→50), buffer rationale (1.10→1.25), floor rationale (5→10)
   - `docs/remediation-playbooks.md`: Minimum floor (5→10), safety multiplier (1.10→1.25)

5. **No changes to README.md** — The README's architectural overview and demo scenario remain unaffected; example concurrency limits mentioned are still valid.

## Affected Sections

- `docs/lambda-throttling.md`: "Recommendation: reserved concurrency", "Why a 1.25 safety buffer?", "Why a floor of 10?"
- `docs/remediation-playbooks.md`: "Recommendation logic" subsection under the Lambda Reserved Concurrency Increase playbook
