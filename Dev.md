# Developer Setup

Quick start guide for PerDiemo Copilot development.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) — fast Python package manager
- [Task](https://taskfile.dev/) — task runner (optional but recommended)
- AWS credentials configured for Bedrock access

## Quick Start

```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd perdiemo

# 2. Copy environment config
cp .env.example .env
# Edit .env with your AWS profile/credentials

# 3. Setup Python environment
task setup          # or: uv venv && uv sync --all-extras

# 4. Verify AWS access
task aws:check      # or: uv run python test_aws.py

# 5. Start the demo
task dev            # or: uv run streamlit run app.py
```

## Available Tasks

Run `task` to see all available commands:

| Command | Description |
|---------|-------------|
| `task setup` | Create venv and install all dependencies |
| `task dev` | Start Streamlit dashboard (headless) |
| `task dev:open` | Start Streamlit and open browser |
| `task test` | Run pytest |
| `task lint` | Run ruff linter |
| `task format` | Auto-format code |
| `task aws:check` | Verify AWS/Bedrock credentials |
| `task add -- <pkg>` | Add a new dependency |

## AWS Configuration

The app uses AWS Bedrock for document extraction. Configure via:

1. **AWS SSO (recommended):** Set `AWS_PROFILE=hackathon` in `.env`, then run `aws sso login`
2. **Environment variables:** Set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`

See `.env.example` for all configuration options.

## Project Structure

```
├── app.py                       # Streamlit dashboard entry point
├── agent_intake.py              # Bedrock document extraction & conversational agent
├── backoffice_auditor.py        # KB compliance & net settlement engine
├── document_package_auditor.py  # Document package completeness & fraud validator
├── perdiemo_client.py           # PerDiemo cloud statutory API client
├── morosystems_client.py        # MoroSystems payments sandbox client
├── demo_documents/              # Synthetic PDFs for 1-click hackathon demos
├── datasets/                    # Sample CNB & MerchantKYB documents
└── tests/                       # pytest test suite
```
