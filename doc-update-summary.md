# Documentation Update Summary

Updated documentation to reflect code changes merged in commit e1f32dd (Merge pull request #34).

## Changes Made

- **Safety Buffer Increase**: Updated `docs/lambda-throttling.md` and `docs/remediation-playbooks.md` to reflect the `SAFETY_BUFFER_MULTIPLIER` increase from `1.10` to `1.25`. The new 25% safety buffer provides better headroom for burst traffic patterns.

- **Minimum Floor Increase**: Updated both documentation files to reflect the `MIN_RESERVED_CONCURRENCY` increase from `5` to `10`. The higher floor ensures more robust baseline protection for traffic spikes during low-traffic windows.

- **Updated Worked Example**: Changed the example in `docs/lambda-throttling.md` from `calculate_reserved_concurrency(120, 40.0)` → `44` to the new behavior `→ 50`, demonstrating the impact of the 1.25x multiplier and floor of 10.

- **Rationale Documentation**: Rewrote the "Why a 1.25 safety buffer?" and "Why a floor of 10?" sections in `docs/lambda-throttling.md` to explain the operational benefits of the increased values for production resilience.

- **Playbook Logic Update**: Updated the "Recommendation logic" section in `docs/remediation-playbooks.md` to clearly state the new 1.25 multiplier and floor of 10, ensuring operators understand the current algorithm constraints.

## Files Modified

- `docs/lambda-throttling.md` — Reserved concurrency recommendation reference
- `docs/remediation-playbooks.md` — SRE operational playbooks

All changes preserve the existing documentation style and structure while ensuring accuracy with the merged code behavior.
