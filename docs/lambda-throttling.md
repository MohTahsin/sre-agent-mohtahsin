# Lambda Throttling — Reference

How the Grok SRE Agent reasons about and remediates AWS Lambda throttling for `payments-processor-prod`.

## Throttling signals

CloudWatch indicators surfaced by `analyze_logs`:

- `Rate exceeded` errors against the Lambda invocation API.
- Sustained `Throttles` metric > 0.
- Error rate spike (45% in the demo scenario).
- Concurrent execution count pinned at the configured reserved concurrency ceiling.

## Recommendation: reserved concurrency

The agent uses `backend.remediation.lambda_scaling.calculate_reserved_concurrency` to size a new ceiling.

```python
from backend.remediation.lambda_scaling import calculate_reserved_concurrency

calculate_reserved_concurrency(current_throttles=120, avg_rps=40.0)
# -> 44  (max(5, ceil(40 * 1.10)))
```

### Why a 1.10 safety buffer?

Production traffic rarely sits exactly at its average RPS — short bursts to ~1.1x average are normal. Sizing the ceiling to `ceil(avg_rps * 1.10)` keeps headroom for those bursts without provisioning for worst-case peak.

### Why a floor of 5?

A floor of 5 guarantees the function can absorb a small traffic spike even during very low-traffic windows, reserving a sane baseline without provisioning idle capacity.

## Account-level safety

`increase_lambda_concurrency` queries `lambda.get_account_settings()` and caps the recommendation at `current_reserved + unreserved - 10` so it never drives unreserved executions below the AWS-enforced floor of 10. If the cap kicks in, the response includes `cappedByAccountQuota: true`.

## What to monitor after remediation

- `AWS/Lambda Throttles` returns to zero.
- `AWS/Lambda Errors` rate falls below 1%.
- `ConcurrentExecutions` settles below the new ceiling.
- Downstream payment success rate recovers in application metrics.
