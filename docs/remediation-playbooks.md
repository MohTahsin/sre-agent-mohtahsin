# SRE Remediation Playbooks

Operational playbooks executed by the Grok SRE Agent during P1 incident response.

## Playbook: Lambda Reserved Concurrency Increase

**Trigger:** AWS Lambda function showing sustained throttling (`Rate exceeded`) errors and an error rate above ~10% during steady-state traffic.

**Owner:** SRE Agent (autonomous) with human approval gate.

### Steps

1. Read CloudWatch logs via `analyze_logs` tool.
2. Generate prioritised hypotheses for the throttling root cause.
3. If reserved concurrency is the most likely cause, compute a recommendation using `calculate_reserved_concurrency(current_throttles, avg_rps)`.
4. Wait for human approval at the `ApprovalGate`.
5. On approval, call `increase_lambda_concurrency` to apply the new value via `lambda.put_function_concurrency()`.
6. Monitor `Throttles` and `Errors` metrics for 5 minutes to confirm recovery.

### Recommendation logic

`calculate_reserved_concurrency` enforces:

- Integer return value (AWS API requires integer concurrency values).
- A minimum floor of `10` so that traffic spikes never drop the function below a baseline buffer.
- A `1.25` safety multiplier over observed average RPS to absorb traffic variance.
- Input validation: a negative `avg_rps` or `current_throttles` raises `ValueError` rather than producing a nonsensical recommendation.

These rules ensure the agent never recommends a value below current production load, and never recommends a sub-baseline value during low-traffic windows.

### Failure modes to watch for

- **Recommendation below current RPS** — would guarantee continued throttling.
- **Float return value** — would be rejected by `boto3` / AWS API.
- **Account-level concurrency exhaustion** — `increase_lambda_concurrency` caps at safe headroom and surfaces `cappedByAccountQuota: true`.

## Playbook: General Triage

1. Page on-call via PagerDuty.
2. Open the SRE Agent dashboard at `http://localhost:5173`.
3. Click **Start Incident** to launch the analysis agent.
4. Review the streamed hypotheses; if confidence is below `Medium`, escalate to a human SRE.
5. Approve or reject the proposed remediation at the gate.
