# PerDiemo MCP v0.2 — Test Report

## Verified in the build environment

- `python -m pytest -q`: **30 passed** (schema, adapter, service, mode switching, no silent fallback).
- `python scripts_smoke.py`: **PASS** (offline native schema smoke test).
- `python -m compileall -q .`: **PASS** (syntax).
- `sh -n start.sh` and `sh -n run-acceptance.sh`: **PASS** (shell syntax).
- Output ZIP: file integrity and membership verified.

## Requires the user's Mac (MCP SDK already installed there)

- `./run-acceptance.sh` (includes MCP Client ↔ mock and MCP Client ↔ local fake REST).
- `python scripts_e2e_live.py --confirm-production` (requires explicit authorization/consent and public API availability; performs a real POST of synthetic 2025 itinerary to the production Render endpoint).

Not verified: actual PerDiemo legal calculation correctness, remote production response, external AgentCore integration, matching-team contract, payment workflow, SHA-256 signature verification. Passing mock/local tests does not establish any of these.
