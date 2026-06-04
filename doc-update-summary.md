# Documentation Update Summary

## Changes to Reflect Lambda Scaling Remediation Logic Update

- **Safety Buffer Increased (1.10 → 1.25):** Updated documentation to reflect the new 1.25x safety multiplier over observed average RPS, which provides better headroom for realistic traffic bursts and demand spikes compared to the previous 1.10x multiplier.

- **Minimum Floor Raised (5 → 10):** Increased the reserved concurrency floor from 5 to 10 concurrency units, establishing a more conservative baseline safety buffer to handle meaningful traffic spikes even during low-traffic windows.

- **Example Calculation Updated:** Changed the code example in `docs/lambda-throttling.md` from `max(5, ceil(40 * 1.10)) = 44` to `max(10, ceil(40 * 1.25)) = 50` to accurately reflect the new recommendation logic.

- **Rationale Descriptions Refined:** Updated explanatory text in both documentation files to clarify why the 1.25x multiplier reflects "realistic traffic variance" and why a floor of 10 maintains "conservative baseline safety buffer" — more precise language aligned with operational impact.

- **Files Updated:** `docs/lambda-throttling.md` and `docs/remediation-playbooks.md` — no changes required to README.md or other documentation files.

## Impact

These changes result in higher but safer recommended reserved concurrency values for Lambda functions experiencing throttling, reducing the likelihood of continued throttling incidents while maintaining reasonable resource utilization.
