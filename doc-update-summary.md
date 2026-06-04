# Documentation Update Summary

## Overview
Updated SRE agent documentation to reflect code changes in the Lambda reserved-concurrency calculation logic merged to main branch.

## Changes Made

- **Increased Safety Buffer Multiplier**: Updated from `1.10` to `1.25`
  - Provides more generous headroom for traffic bursts and transient spikes
  - Reflects production experience that bursts to ~1.25x average are common during peak periods

- **Raised Minimum Floor**: Updated from `5` to `10`
  - Ensures a more robust baseline for production stability
  - Maintains adequate safety buffer even during very low-traffic windows

## Files Updated

1. **docs/lambda-throttling.md**
   - Updated example calculation: `ceil(40 * 1.10)` → `ceil(40 * 1.25)` (output: 44 → 50)
   - Revised explanation for 1.25 safety buffer rationale
   - Updated floor-of-10 explanation with emphasis on production robustness

2. **docs/remediation-playbooks.md**
   - Updated minimum floor value from 5 to 10
   - Updated safety multiplier from 1.10 to 1.25
   - Enhanced descriptions to clarify production stability benefits

## Related Code Changes

- **Commit**: `1eecf22` — "feat: raise reserved-concurrency safety buffer to 1.25 and floor to 10"
- **Modified files**: 
  - `backend/remediation/lambda_scaling.py` (constants `SAFETY_BUFFER_MULTIPLIER`, `MIN_RESERVED_CONCURRENCY`)
  - `tests/test_lambda_scaling.py` (test expectations updated to match new behavior)

## Impact

These documentation updates ensure operators understand the current recommendation logic and rationale behind the increased safety margins, reducing risk of misalignment between documented and actual behavior.
