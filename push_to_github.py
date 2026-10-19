# -*- coding: utf-8 -*-
"""
push_to_github.py — Automatic deployment script for perdiemo-fintechers-hackathon-2026.

Synchronizes all starter template files and tags the baseline commit as 'hackathon-start'.

Usage:
    python hackathon_starter/push_to_github.py [GITHUB_TOKEN]
"""
import os
import sys
import json
import base64
import urllib.request
import urllib.error
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent
REPO = "dataquo/perdiemo-fintechers-hackathon-2026"
BRANCH = "main"

def get_token():
    if len(sys.argv) > 1:
        return sys.argv[1].strip()
    
    # Try reading from root .env
    env_file = ROOT_DIR.parent / ".env"
    if env_file.exists():
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() in ("GH_TOKEN", "GITHUB_TOKEN", "GITHUB_DATAQUO_TOKEN_PERDIEMOEU", "GITHUB_BOT_TOKEN"):
                        os.environ[k.strip()] = v.strip()

    return (
        os.environ.get("GH_TOKEN") or
        os.environ.get("GITHUB_TOKEN") or
        os.environ.get("GITHUB_BOT_TOKEN") or
        os.environ.get("GITHUB_DATAQUO_TOKEN_PERDIEMOEU")
    )

TOKEN = get_token()

def github_api(endpoint, method="GET", data=None):
    url = f"https://api.github.com/{endpoint.lstrip('/')}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {TOKEN}",
        "User-Agent": "PerDiemo-Hackathon-Uploader/1.0"
    }
    payload = None
    if data is not None:
        payload = json.dumps(data).encode('utf-8')
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8')
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8')
        print(f"  [API ERROR] {e.code} on {method} {url}: {err_msg}")
        raise

def get_file_sha(path):
    try:
        data = github_api(f"repos/{REPO}/contents/{path}?ref={BRANCH}")
        return data.get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise

def put_file(local_path, repo_path, message):
    with open(local_path, "r", encoding="utf-8") as f:
        content_str = f.read()

    sha = get_file_sha(repo_path)
    encoded = base64.b64encode(content_str.encode('utf-8')).decode('utf-8')
    payload = {
        "message": message,
        "content": encoded,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha
        print(f"  [UPDATE] Updating '{repo_path}'...")
    else:
        print(f"  [CREATE] Creating '{repo_path}'...")

    github_api(f"repos/{REPO}/contents/{repo_path}", method="PUT", data=payload)
    print(f"  [SUCCESS] '{repo_path}' pushed.")

def tag_hackathon_start():
    print("\nTagging baseline commit with 'hackathon-start'...")
    try:
        ref = github_api(f"repos/{REPO}/git/ref/heads/{BRANCH}")
        commit_sha = ref.get("object", {}).get("sha")
        if not commit_sha:
            print("  [ERROR] Could not resolve HEAD commit SHA.")
            return

        tag_payload = {
            "ref": "refs/tags/hackathon-start",
            "sha": commit_sha
        }
        github_api(f"repos/{REPO}/git/refs", method="POST", data=tag_payload)
        print("  [SUCCESS] Tag 'hackathon-start' successfully created on GitHub!")
    except urllib.error.HTTPError as e:
        if e.code == 422:
            print("  [INFO] Tag 'hackathon-start' already exists.")
        else:
            print(f"  [WARN] Failed to create tag: {e}")

def main():
    if not TOKEN:
        print("[ERROR] No GitHub token provided. Please run:")
        print("    python hackathon_starter/push_to_github.py <YOUR_GITHUB_TOKEN>")
        sys.exit(1)

    print(f"Target repository: {REPO} (branch: {BRANCH})")
    
    # Verify permissions
    try:
        repo_data = github_api(f"repos/{REPO}")
        print(f"Repository verified: {repo_data.get('full_name')} (Private: {repo_data.get('private')})")
    except Exception as e:
        print(f"[ERROR] Cannot access {REPO}. Ensure token has 'repo' or 'contents:write' permissions: {e}")
        sys.exit(1)

    files_to_push = [
        ("README.md", "README.md", "docs: initialize hackathon project overview and team onboarding guide"),
        ("requirements.txt", "requirements.txt", "build: add core dependencies (requests, boto3, streamlit)"),
        (".env.example", ".env.example", "config: add environment variable template for AWS Bedrock"),
        ("perdiemo_client.py", "perdiemo_client.py", "feat: add drop-in PerDiemo REST API client SDK"),
        ("agent_intake.py", "agent_intake.py", "feat: add AWS Bedrock multimodal travel intake agent"),
        ("backoffice_auditor.py", "backoffice_auditor.py", "feat: add Komerční banka back-office compliance rules"),
        ("app.py", "app.py", "feat: add interactive Streamlit demo dashboard"),
        ("sample_data/sample_itinerary.json", "sample_data/sample_itinerary.json", "test: add sample statutory itinerary test data"),
        ("sample_data/sample_hotel_folio.json", "sample_data/sample_hotel_folio.json", "test: add sample hotel folio test data"),
    ]

    for local_rel, repo_path, msg in files_to_push:
        local_full = ROOT_DIR / local_rel
        if local_full.exists():
            put_file(local_full, repo_path, msg)
        else:
            print(f"  [SKIP] Local file {local_rel} not found.")

    tag_hackathon_start()
    print(f"\n[DONE] Repository {REPO} is 100% prepared and ready for the team!")

if __name__ == "__main__":
    main()
