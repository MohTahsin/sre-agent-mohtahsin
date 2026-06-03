# Documentation Update Summary

## Overview
Updated operational and reference documentation to reflect changes merged to the Lambda throttling remediation logic in `backend/remediation/lambda_scaling.py`.

## Changes Made

### 1. Safety Buffer Multiplier: 1.10 → 1.25
- **Impact**: `calculate_reserved_concurrency()` now applies a larger safety margin over observed average RPS.
- **Rationale**: The increased buffer better accommodates short-term traffic bursts beyond 1.1x average, improving remediation robustness.
- **Files Updated**: 
  - `docs/lambda-throttling.md`: Updated worked example from 44 → 50 concurrency for avg_rps=40
  - `docs/remediation-playbooks.md`: Updated from "1.10 safety multiplier" to "1.25 safety multiplier"
  - `AGENTS.md`: Added explicit constant values to the contract documentation

### 2. Minimum Reserved Concurrency Floor: 5 → 10
- **Impact**: The function never recommends below 10 concurrent executions, even during zero or very-low traffic windows.
- **Rationale**: The higher floor provides increased safety headroom for unexpected traffic spikes and improves incident response time.
- **Files Updated**:
  - `docs/lambda-throttling.md`: Updated explanation and renamed section from "floor of 5" to "floor of 10"
  - `docs/remediation-playbooks.md`: Updated from "minimum floor of 5" to "minimum floor of 10"
  - `AGENTS.md`: Added explicit constant value (10) to the contract documentation

## Documentation Style Preserved
All updates maintain:
- Existing section structure and hierarchy
- Technical accuracy and operational guidance tone
- Consistency with code comments and test assertions in the merged PR

## Files Modified
1. `docs/lambda-throttling.md` (reference documentation)
2. `docs/remediation-playbooks.md` (operational playbook)
3. `AGENTS.md` (remediation contract and coding guidelines)
4. `DEMO.md` (demonstration guide file map)

## Verification
- All referenced constants match values in `backend/remediation/lambda_scaling.py`
- Test assertions in `tests/test_lambda_scaling.py` confirm behavior
- No unrelated documentation was modified
