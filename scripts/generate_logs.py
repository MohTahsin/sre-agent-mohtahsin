"""
Generates emulated CloudWatch logs for the payments-processor-prod throttling incident.
Output: logs/cloudwatch_logs.json (~200 events over 30 minutes)

Log pattern:
  - Minutes 0-10:  normal operation (low error rate)
  - Minutes 10-30: throttling escalates as traffic spikes (up to 65% error rate)
"""

import json
import os
import random
import uuid
from datetime import datetime, timedelta, timezone

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "cloudwatch_logs.json")
FUNCTION_NAME = "payments-processor-prod"
REGION = "us-east-1"
LOG_GROUP = f"/aws/lambda/{FUNCTION_NAME}"


def ts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def stream_name(dt: datetime) -> str:
    return f"{dt.strftime('%Y/%m/%d')}/[$LATEST]{random.randint(10000, 99999):05d}"


def generate_logs():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    start = now - timedelta(minutes=30)

    events = []
    payment_ids = [f"PAY-{random.randint(100000, 999999)}" for _ in range(60)]

    for i in range(200):
        t = start + timedelta(seconds=i * 9)
        minutes_elapsed = (t - start).total_seconds() / 60

        # Linear ramp: 0% throttle errors before minute 10, rising to 65% by minute 30.
        # This gives the agent a clear time-series escalation pattern to identify.
        throttle_prob = 0.0 if minutes_elapsed < 10 else min(0.65, (minutes_elapsed - 10) / 20 * 0.65)
        # Slow calls (gateway latency) occur at a constant background rate.
        slow_prob = 0.12

        r = random.random()
        payment_id = random.choice(payment_ids)
        request_id = str(uuid.uuid4())[:8]

        if r < throttle_prob:
            # Throttling error
            events.append({
                "timestamp": ts(t),
                "logStreamName": stream_name(t),
                "level": "ERROR",
                "requestId": request_id,
                "message": (
                    f"[ERROR] {t.strftime('%H:%M:%S')} RequestId: {request_id} "
                    f"TooManyRequestsException: Rate exceeded for function {FUNCTION_NAME}. "
                    f"Reserved concurrency limit reached (10/10). Request for payment "
                    f"{payment_id} has been throttled."
                ),
                "errorCode": "TooManyRequestsException",
                "functionName": FUNCTION_NAME,
                "concurrentExecutions": 10,
                "reservedConcurrencyLimit": 10,
                "paymentId": payment_id,
                "retryAttempt": random.randint(1, 3),
            })

        elif r < throttle_prob + slow_prob:
            # Slow invocation (downstream gateway latency)
            duration_ms = random.uniform(9000, 27000)
            gateway_ms = random.uniform(7000, 25000)
            events.append({
                "timestamp": ts(t),
                "logStreamName": stream_name(t),
                "level": "WARN",
                "requestId": request_id,
                "message": (
                    f"[WARN] {t.strftime('%H:%M:%S')} RequestId: {request_id} "
                    f"High latency: {FUNCTION_NAME} invocation took {duration_ms:.0f}ms. "
                    f"Payment gateway response time: {gateway_ms:.0f}ms. "
                    f"PaymentId: {payment_id}"
                ),
                "functionName": FUNCTION_NAME,
                "durationMs": round(duration_ms, 1),
                "gatewayResponseMs": round(gateway_ms, 1),
                "paymentId": payment_id,
            })

        else:
            # Successful payment
            duration_ms = random.uniform(80, 900)
            amount = round(random.uniform(10.0, 5000.0), 2)
            events.append({
                "timestamp": ts(t),
                "logStreamName": stream_name(t),
                "level": "INFO",
                "requestId": request_id,
                "message": (
                    f"[INFO] {t.strftime('%H:%M:%S')} RequestId: {request_id} "
                    f"Payment processed: {payment_id} amount=${amount:.2f} "
                    f"duration={duration_ms:.0f}ms status=SUCCESS"
                ),
                "functionName": FUNCTION_NAME,
                "durationMs": round(duration_ms, 1),
                "paymentId": payment_id,
                "amount": amount,
                "status": "SUCCESS",
            })

    # Pre-computed summary appended as the final event. Lets the model verify
    # error-rate figures without re-counting individual events itself.
    error_count = sum(1 for e in events if e["level"] == "ERROR")
    warn_count = sum(1 for e in events if e["level"] == "WARN")
    info_count = sum(1 for e in events if e["level"] == "INFO")
    durations = [e["durationMs"] for e in events if "durationMs" in e]
    avg_duration = round(sum(durations) / len(durations), 1) if durations else 0

    events.append({
        "timestamp": ts(now),
        "logStreamName": "METRIC_SUMMARY",
        "level": "METRIC",
        "type": "METRIC_SUMMARY",
        "message": f"[METRIC] 30-minute summary for {FUNCTION_NAME}",
        "functionName": FUNCTION_NAME,
        "windowMinutes": 30,
        "totalInvocations": len(events),
        "throttledInvocations": error_count,
        "slowInvocations": warn_count,
        "successfulInvocations": info_count,
        "errorRatePct": round(error_count / len(events) * 100, 1),
        "currentReservedConcurrency": 10,
        "peakConcurrentExecutions": 10,
        "avgDurationMs": avg_duration,
        "region": REGION,
    })

    output = {
        "logGroup": LOG_GROUP,
        "region": REGION,
        "functionName": FUNCTION_NAME,
        "generatedAt": ts(now),
        "windowStart": ts(start),
        "windowEnd": ts(now),
        "events": events,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Generated {len(events)} log events -> {os.path.abspath(OUTPUT_PATH)}")
    print(f"  Throttle errors:  {error_count} ({round(error_count/len(events)*100,1)}%)")
    print(f"  Slow invocations: {warn_count}")
    print(f"  Successful:       {info_count}")
    print(f"  Avg duration:     {avg_duration}ms")


if __name__ == "__main__":
    generate_logs()
