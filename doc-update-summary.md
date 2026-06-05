# Documentation Update Summary

## Overview
Updated documentation to reflect code changes in the Lambda reserved concurrency remediation logic, specifically the increased safety buffer and minimum floor values.

## Changes Made

- **Safety Buffer Multiplier**: Increased from `1.10` to `1.25` in `docs/lambda-throttling.md` and `docs/remediation-playbooks.md`. This change reflects a more conservative approach to handle typical production traffic bursts that can reach 1.25x average RPS.

- **Minimum Reserved Concurrency Floor**: Increased from `5` to `10` in `docs/lambda-throttling.md` and `docs/remediation-playbooks.md`. This ensures the function maintains a more robust baseline capacity to absorb traffic spikes and unexpected load surges.

- **Example Calculation**: Updated the example in `docs/lambda-throttling.md` from `calculate_reserved_concurrency(current_throttles=120, avg_rps=40.0) -> 44 (max(5, ceil(40 * 1.10)))` to `calculate_reserved_concurrency(current_throttles=120, avg_rps=40.0) -> 50 (max(10, ceil(40 * 1.25)))` to demonstrate the new behavior.

- **Rationale Sections**: Updated explanatory text in "Why a 1.25 safety buffer?" and "Why a floor of 10?" sections to justify the conservative approach for improved resilience and reliability during peak traffic periods and scaling scenarios.

## Files Modified

- `docs/lambda-throttling.md` (lines 21-31)
- `docs/remediation-playbooks.md` (lines 23-28)

## Impact

These documentation updates ensure operators and developers understand the improved safety parameters that protect against throttling incidents with a more conservative buffer and higher baseline concurrency reservation.
