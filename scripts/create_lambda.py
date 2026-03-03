"""
Creates payments-processor-prod Lambda on AWS with reserved concurrency=10
to simulate the throttling condition used in the SRE demo.
"""

import io
import json
import os
import time
import zipfile

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

FUNCTION_NAME = "payments-processor-prod"
REGION = os.environ.get("AWS_REGION", "us-east-1")
ROLE_NAME = "payments-processor-lambda-role"
RESERVED_CONCURRENCY = 10

HANDLER_CODE = '''import json
import random
import time

def handler(event, context):
    """Simulates payment processing with realistic latency."""
    processing_time = random.uniform(0.1, 2.0)
    time.sleep(processing_time)

    payment_id = event.get("payment_id", "PAY-UNKNOWN")
    amount = event.get("amount", 0)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "payment_id": payment_id,
            "status": "processed",
            "amount": amount,
            "processing_time_ms": int(processing_time * 1000),
        }),
    }
'''


def get_or_create_role(iam) -> str:
    try:
        role = iam.get_role(RoleName=ROLE_NAME)
        arn = role["Role"]["Arn"]
        print(f"  Using existing IAM role: {arn}")
        return arn
    except ClientError as e:
        if e.response["Error"]["Code"] != "NoSuchEntity":
            raise

    print(f"  Creating IAM role: {ROLE_NAME}")
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }
    role = iam.create_role(
        RoleName=ROLE_NAME,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description="Execution role for payments-processor-prod (SRE demo)",
    )
    iam.attach_role_policy(
        RoleName=ROLE_NAME,
        PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    )
    arn = role["Role"]["Arn"]
    print(f"  Created role: {arn}")
    print("  Waiting 15s for IAM role propagation...")
    time.sleep(15)
    return arn


def build_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("handler.py", HANDLER_CODE)
    return buf.getvalue()


def main():
    print(f"Setting up Lambda function: {FUNCTION_NAME} in {REGION}\n")

    iam = boto3.client("iam", region_name=REGION)
    client = boto3.client("lambda", region_name=REGION)

    role_arn = get_or_create_role(iam)
    zip_bytes = build_zip()

    try:
        client.get_function(FunctionName=FUNCTION_NAME)
        print(f"  Updating existing function code...")
        client.update_function_code(FunctionName=FUNCTION_NAME, ZipFile=zip_bytes)
        waiter = client.get_waiter("function_updated")
        waiter.wait(FunctionName=FUNCTION_NAME)
    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceNotFoundException":
            raise
        print(f"  Creating function: {FUNCTION_NAME}")
        client.create_function(
            FunctionName=FUNCTION_NAME,
            Runtime="python3.12",
            Role=role_arn,
            Handler="handler.handler",
            Code={"ZipFile": zip_bytes},
            Description="Payment processing function — SRE throttling demo",
            Timeout=30,
            MemorySize=256,
        )
        waiter = client.get_waiter("function_active")
        waiter.wait(FunctionName=FUNCTION_NAME)

    # Note: reserved concurrency is intentionally not set here.
    # The throttling scenario is simulated via generated CloudWatch logs.
    # The agent's increase_lambda_concurrency tool will make the real AWS call
    # during the demo remediation step.

    print(f"\nDone!")
    print(f"  Function:             {FUNCTION_NAME}")
    print(f"  Region:               {REGION}")
    print(f"  Reserved concurrency: unrestricted (throttling simulated via logs)")
    print(f"\nNext: python scripts/generate_logs.py")


if __name__ == "__main__":
    main()
