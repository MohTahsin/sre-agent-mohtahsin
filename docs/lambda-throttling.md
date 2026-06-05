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
# -> 50  (max(10, ceil(40 * 1.25)))
```

### Why a 1.25 safety buffer?

Production traffic rarely sits exactly at its average RPS — bursts to ~1.25x average are normal and often persist during sustained load changes. Sizing the ceiling to `ceil(avg_rps * 1.25)` keeps sufficient headroom for traffic variance and transient spikes without provisioning for worst-case peak capacity.

### Why a floor of 10?

A floor of 10 guarantees the function can absorb meaningful traffic spikes even during very low-traffic windows, ensuring the service remains responsive. This baseline prevents under-provisioning during traffic ramps while still being economical for idle or near-idle periods.

## Account-level safety

`increase_lambda_concurrency` queries `lambda.get_account_settings()` and caps the recommendation at `current_reserved + unreserved - 10` so it never drives unreserved executions below the AWS-enforced floor of 10. If the cap kicks in, the response includes `cappedByAccountQuota: true`.

## What to monitor after remediation

- `AWS/Lambda Throttles` returns to zero.
- `AWS/Lambda Errors` rate falls below 1%.
- `ConcurrentExecutions` settles below the new ceiling.
- Downstream payment success rate recovers in application metrics.
