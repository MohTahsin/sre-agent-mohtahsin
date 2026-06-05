# Documentation Update Summary

## Changes Made

- **Safety buffer increased from 1.10 to 1.25** (`docs/lambda-throttling.md`, `docs/remediation-playbooks.md`): Updated all references to reflect the more conservative multiplier that provides better headroom for sustained traffic spikes and load ramps.

- **Minimum reserved concurrency floor increased from 5 to 10** (`docs/lambda-throttling.md`, `docs/remediation-playbooks.md`): Updated floor rationale to explain that the higher baseline ensures meaningful traffic absorption even during low-traffic windows while maintaining economic efficiency.

- **Code example updated** (`docs/lambda-throttling.md`): Changed the worked example from `max(5, ceil(40 * 1.10)) -> 44` to `max(10, ceil(40 * 1.25)) -> 50` to reflect the new algorithm behavior.

- **Rationale sections expanded** (`docs/lambda-throttling.md`): Enhanced explanations for why 1.25 and 10 are appropriate thresholds, clarifying that bursts to 1.25x average are normal and that the floor prevents under-provisioning during traffic ramps.

- **Operational guidance aligned** (`docs/remediation-playbooks.md`): Ensured the "Recommendation logic" section lists the current multiplier and floor values that the implementation enforces.

## Why

These changes document the behavioral improvements merged in [feat/lambda-scaling-recommendation](https://github.com/MohTahsin/sre-agent-mohtahsin/pull/32), which raised both the safety margin and floor to better handle real-world traffic patterns while maintaining clearer safety guarantees in the Lambda throttling remediation playbook.
