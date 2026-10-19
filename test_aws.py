# -*- coding: utf-8 -*-
"""
test_aws.py — Diagnostic & Verification Script for Hackathon AWS Setup.

Verifies:
1. Active AWS Identity (Account ID: 532132111066, Role: ai-hackathon-TeamAdmin)
2. S3 Read Access to Shared Datasets (s3://ai-hackathon-datasets-422928733782/)
3. Amazon Bedrock Runtime in Frankfurt (eu-central-1) using Claude Sonnet 4.5
4. AWS Cost Explorer API in us-east-1 (Budget check)

Works with boto3 (if installed) or falls back to AWS CLI seamlessly.
"""
import os
import sys
import json
import shutil
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure AWS CLI is in PATH
aws_default_path = r"C:\Program Files\Amazon\AWSCLIV2"
if os.path.isdir(aws_default_path) and aws_default_path not in os.environ.get("PATH", ""):
    os.environ["PATH"] = aws_default_path + os.pathsep + os.environ.get("PATH", "")

# Load .env without requiring external dependencies
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

REGION = os.environ.get("AWS_REGION", "eu-central-1")
PROFILE = os.environ.get("AWS_PROFILE", "martin-hackathon")
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "eu.anthropic.claude-sonnet-4-5-20250929-v1:0")
DATASETS_S3_BUCKET = "ai-hackathon-datasets-422928733782"

def run_cli_cmd(args):
    try:
        res = subprocess.run(
            ["aws"] + args,
            capture_output=True,
            text=True,
            check=False
        )
        return res.returncode, res.stdout, res.stderr
    except FileNotFoundError:
        return 1, "", "AWS CLI executable not found in PATH."

def test_sts():
    print("\n--- 1. Testing AWS Identity (STS) ---")
    # Try boto3 first
    try:
        import boto3
        session = boto3.Session(profile_name=PROFILE)
        sts = session.client("sts", region_name=REGION)
        caller = sts.get_caller_identity()
        arn = caller.get("Arn", "")
        account = caller.get("Account", "")
        print(f"✅ Success! Connected to AWS Account: {account}")
        print(f"   Identity ARN: {arn}")
        if "ai-hackathon-TeamAdmin" in arn:
            print("   Role confirmed: ai-hackathon-TeamAdmin (Full team admin privileges)")
        return account
    except ImportError:
        pass
    except Exception as e:
        print(f"   (boto3: {e}) Trying AWS CLI...")

    # Fallback to CLI
    code, stdout, stderr = run_cli_cmd(["sts", "get-caller-identity", "--profile", PROFILE, "--output", "json"])
    if code == 0:
        data = json.loads(stdout)
        print(f"✅ Success! Connected to AWS Account: {data.get('Account')}")
        print(f"   Identity ARN: {data.get('Arn')}")
        if "ai-hackathon-TeamAdmin" in data.get("Arn", ""):
            print("   Role confirmed: ai-hackathon-TeamAdmin (Full team admin privileges)")
        return data.get("Account")
    else:
        print(f"❌ Failed to get caller identity:\n{stderr}")
        return None

def test_s3_datasets():
    print("\n--- 2. Testing Shared Datasets S3 Access ---")
    try:
        import boto3
        session = boto3.Session(profile_name=PROFILE)
        s3 = session.client("s3", region_name=REGION)
        res = s3.list_objects_v2(Bucket=DATASETS_S3_BUCKET, MaxKeys=5)
        contents = res.get("Contents", [])
        if contents:
            print(f"✅ Success! Bucket 's3://{DATASETS_S3_BUCKET}/' is accessible.")
            for item in contents[:4]:
                print(f"   - {item['Key']} ({item['Size']:,} bytes)")
            return
    except (ImportError, Exception):
        pass

    # CLI fallback
    code, stdout, stderr = run_cli_cmd(["s3", "ls", f"s3://{DATASETS_S3_BUCKET}/", "--region", REGION, "--profile", PROFILE])
    if code == 0:
        print(f"✅ Success! Bucket 's3://{DATASETS_S3_BUCKET}/' is accessible.")
        for line in stdout.strip().splitlines()[:5]:
            print(f"   {line}")
    else:
        print(f"❌ Failed to list shared datasets:\n{stderr}")

def test_bedrock_converse():
    print("\n--- 3. Testing Amazon Bedrock Runtime (Frankfurt eu-central-1) ---")
    print(f"   Target Model: {MODEL_ID}")
    prompt_text = "Reply in exactly 5 words: Confirm Bedrock is working for PerDiemo."
    try:
        import boto3
        session = boto3.Session(profile_name=PROFILE)
        bedrock = session.client("bedrock-runtime", region_name=REGION)
        response = bedrock.converse(
            modelId=MODEL_ID,
            messages=[{"role": "user", "content": [{"text": prompt_text}]}],
            inferenceConfig={"maxTokens": 50, "temperature": 0.0}
        )
        reply = response["output"]["message"]["content"][0]["text"]
        usage = response.get("usage", {})
        print(f"✅ Success! Bedrock responded:")
        print(f"   \"{reply}\"")
        print(f"   Tokens: In={usage.get('inputTokens', 0)}, Out={usage.get('outputTokens', 0)}")
        return
    except (ImportError, Exception):
        pass

    # CLI fallback
    msg = json.dumps([{"role": "user", "content": [{"text": prompt_text}]}])
    cfg = json.dumps({"maxTokens": 50})
    code, stdout, stderr = run_cli_cmd([
        "bedrock-runtime", "converse",
        "--region", REGION,
        "--profile", PROFILE,
        "--model-id", MODEL_ID,
        "--messages", msg,
        "--inference-config", cfg,
        "--output", "json"
    ])
    if code == 0:
        data = json.loads(stdout)
        reply = data["output"]["message"]["content"][0]["text"]
        usage = data.get("usage", {})
        print(f"✅ Success! Bedrock responded:")
        print(f"   \"{reply}\"")
        print(f"   Tokens: In={usage.get('inputTokens', 0)}, Out={usage.get('outputTokens', 0)}")
    else:
        print(f"❌ Bedrock test failed:\n{stderr}")

def test_cost_explorer():
    print("\n--- 4. Testing AWS Spend / Cost Explorer (us-east-1) ---")
    code, stdout, stderr = run_cli_cmd([
        "ce", "get-cost-and-usage",
        "--region", "us-east-1",
        "--profile", PROFILE,
        "--time-period", "Start=2026-10-01,End=2026-10-21",
        "--granularity", "MONTHLY",
        "--metrics", "UnblendedCost",
        "--query", "ResultsByTime[0].Total.UnblendedCost.Amount",
        "--output", "text"
    ])
    if code == 0:
        try:
            val = float(stdout.strip())
            print(f"✅ Success! Current Total Spend: ${val:.4f} USD (Team Budget: $800.00)")
        except ValueError:
            print(f"✅ Cost Explorer returned: {stdout.strip()}")
    else:
        print(f"ℹ️ Cost Explorer query returned:\n{stderr}")

if __name__ == "__main__":
    print("=======================================================")
    print("   PerDiemo Copilot — AWS Hackathon Verification Tool  ")
    print("=======================================================")
    print(f"Active Profile : {PROFILE}")
    print(f"Target Region  : {REGION}")
    acct = test_sts()
    if acct:
        test_s3_datasets()
        test_bedrock_converse()
        test_cost_explorer()
    print("\n=======================================================\n")
