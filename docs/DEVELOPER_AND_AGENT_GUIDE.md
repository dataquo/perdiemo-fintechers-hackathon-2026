# PerDiemo Copilot — Developer & AI Agent Operations Guide (v1.1.15)

> **Release Version:** `v1.1.15`  
> **Date:** October 20, 2026  
> **Event:** The FinTechers Hackathon 2026 (Prague) — Track 06 (Back-Office AI) & Track 01  
> **Target Audience:** Core Developers, AI Coding Assistants (Antigravity, Cursor, Kiro, Claude Code)

---

## 1. Executive Summary & Architecture Baseline

PerDiemo Copilot is an autonomous agentic system automating business travel expense auditing, Czech Labour Code compliance (§§ 151–189 ZP), foreign exchange fixing (ČNB), and corporate card reconciliation for **Komerční banka** and enterprise back-offices.

```
                           +---------------------------------------------------+
                           |               DEVELOPMENT LAYER                   |
                           |  Lead: Antigravity / Cursor IDE                   |
                           |  Fallback / Teammates: Kiro Desktop IDE (Free)    |
                           |  In-IDE Bedrock Agent: Roo Code / Cline           |
                           +-------------------------+-------------------------+
                                                     |
                                                     v
+----------------------------------------------------------------------------------------------------+
|                                    PERDIEMO APPLICATION RUNTIME                                    |
|                                                                                                    |
|   +----------------------+        +------------------------+        +--------------------------+   |
|   |   Streamlit Front    |  --->  |    agent_intake.py     |  --->  |     Amazon Bedrock       |   |
|   |       (app.py)       |        | (Multimodal Extractor) |        | (eu-central-1 Frankfurt) |   |
|   +----------------------+        +-----------+------------+        | Claude Sonnet 4.5        |   |
|                                               |                     +--------------------------+   |
|                                               v                                                    |
|                                   +------------------------+                                       |
|                                   |   perdiemo_client.py   |  --->  PerDiemo Cloud Engine          |
|                                   |  (Deterministic ZP)    |        (https://perdiemo-backend...   |
|                                   +-----------+------------+        SHA-256 Audit Seal)            |
|                                               |                                                    |
|                                               v                                                    |
|   +--------------------------+    +------------------------+                                       |
|   | document_package_auditor | -> |  backoffice_auditor.py |  <---  TSYS / KB Card Feeds           |
|   | (Completeness & Checks)  |    | (Fraud & Anomaly Rules)|        (Double-dipping, Weekend trips)|
|   +--------------------------+    +------------------------+                                       |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Key Architectural Decisions (ADR v1.1.2)

### Decision 1: AI Developer Tooling Strategy (Antigravity vs. Kiro vs. Bedrock)
* **Finding:** AWS Kiro (kiro.dev) was evaluated as the primary IDE for the hackathon team. Investigation of the Hackathon IAM Identity Center (`https://d-c3676ff6eb.awsapps.com/start`) confirmed:
  1. The sign-in directory lives in **Stockholm (`eu-north-1`)**, while resources/Bedrock live in **Frankfurt (`eu-central-1`)**.
  2. The hackathon organizers (AWS x Deloitte) provisioned **AWS Cloud Infrastructure accounts with a USD 800 Amazon Bedrock budget**.
  3. The organizers **did not** provision Kiro Enterprise SaaS licenses in IAM Identity Center (resulting in: *"Your organization administrator has not granted you access to any Kiro profile"*).
* **Decision:**
  - **Primary:** Development proceeds primarily in **Google Antigravity / Cursor** under the team lead while credits are active.
  - **Contingency / Teammates:** If Antigravity credits are exhausted, developers use **Kiro Desktop IDE** logged in via personal **AWS Builder ID** (Free Tier, 50 requests/month) for spec-driven workflows (`/spec`, `requirements.md`, `tasks.md`).
  - **In-IDE Bedrock Extension:** To leverage the USD 800 hackathon Bedrock budget for unlimited in-editor coding, developers install **Roo Code** or **Cline** inside Kiro/VS Code configured to AWS Bedrock (`profile: hackathon`, `region: eu-central-1`, `model: eu.anthropic.claude-sonnet-4-5-20250929-v1:0`).

### Decision 2: Model Selection & Regional Constraints
* **Finding:** According to the official AWS Participant Guide, Claude 5 / Sonnet 5.5 has no capacity in `eu-central-1` and returns `AccessDeniedException`.
* **Decision:** Standardize model IDs strictly to EU cross-region inference profiles:
  - **Primary LLM:** `eu.anthropic.claude-sonnet-4-5-20250929-v1:0` (Sonnet 4.5)
  - **Fallback / Batch LLM:** `eu.amazon.nova-2-lite-v1:0` or `qwen.qwen3-coder-30b-a3b-v1:0`
  - **Region:** `eu-central-1` (Frankfurt) for all computation, S3 storage, and Bedrock calls.

### Decision 3: Two-Tier Deterministic Statutory Pipeline
* **Rule:** LLMs must **NEVER** calculate statutory per diems, meal deductions (70%/35%/25%), or ČNB foreign exchange rates directly in prompt completions.
* **Implementation:** All math is delegated to `perdiemo_client.PerDiemoClient` which invokes the verified PerDiemo Cloud API (`/api/calculate`), yielding a legally defensible SHA-256 cryptographic seal compliant with Supreme Administrative Court ruling **NSS 3 Afs 97/2025 - 71**.

### Decision 4: Human-in-the-Loop Safe Agentic Payments
* **Decision:** Autonomous calculations and proactive trip clusterings are gated behind a human authorization checkpoint prior to executing money movement on the MoroSystems Payments Sandbox.

### Decision 5: Strict Non-Inference from Raw Bank Feeds
* **Decision:** POS terminal descriptors (TSYS feeds) cannot prove complimentary hotel breakfast. Raw card spend defaults to room-only (0% meal reduction) to prevent unlawful deduction under § 163 ZP.

*(For full ADR details and formal schemas, see [AGENTS.md](../AGENTS.md).)*

---

## 3. Developer & Agent Workflow Guide

### 3.1 Initial Environment Setup
```powershell
# 1. Clone repository & enter workspace
cd d:\_DOCUMENTS\_SCRIPTS\PERDIEMO-FTH

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment template
cp .env.example .env
```

### 3.2 AWS SSO Authentication (Bedrock Access)
```powershell
# First time setup (or if profile missing):
.\setup_aws_sso.ps1
# Inputs:
# - SSO start URL: https://d-c3676ff6eb.awsapps.com/start
# - SSO region: eu-north-1
# - Role: ai-hackathon-TeamAdmin
# - Client region: eu-central-1
# - Profile: hackathon

# Routine daily login:
.\aws_login.ps1

# Full verification suite:
uv run python test_aws.py             # Bedrock & Cloud Engine
uv run python test_document_parser.py # Multimodal OCR & Demo Documents (6/6 checks)
uv run pytest tests                   # Core smoke tests
```

### 3.3 Running the Application
```powershell
# Launch interactive Streamlit demo
streamlit run app.py
```
Open browser at `http://localhost:8501`.

---

## 4. Guidelines for AI Coding Agents Operating in this Repo

When automated AI agents (Antigravity, Cursor, Kiro, Roo Code) modify code in this repository, they must adhere to the following rules:

1. **Preserve Fallbacks:** Always maintain offline / mock fallbacks in `agent_intake.py` so the UI and testing suite run even if AWS SSO tokens expire.
2. **Preserve Encoding:** All Python files must use `# -*- coding: utf-8 -*-` and configure stdout/stderr for UTF-8 compatibility on Windows systems.
3. **No Direct Tax Calculations in Prompts:** Ensure travel itineraries extracted from receipts are passed into `perdiemo_client.py` and audited through `backoffice_auditor.py`.
4. **Audit Immutability:** Never bypass the SHA-256 audit seal calculation in `perdiemo_client.py`.
5. **Spend Efficiency:** Avoid excessive iterative Bedrock calls. Prompt caching should be used when sending large document payloads.
