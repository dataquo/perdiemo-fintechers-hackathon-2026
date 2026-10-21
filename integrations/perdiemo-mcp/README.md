# PerDiemo MCP — Standalone v0.2

An independent Python Model Context Protocol (MCP) server that exposes **PerDiemo's existing REST API** to MCP-compatible tools and AI agents. This adapter does **not** implement Czech statutory allowance formulas, match card transactions, approve reimbursements, or execute payments.

**Status (19 October 2026):** The owner reported **30/30 Python tests passing**, both offline MCP acceptance flows passing, and a **successful live MCP → PerDiemo REST calculation** using synthetic data. The sample trip returned `1,226.61 CZK` and a verification signature. This establishes live API connectivity, **not** independent legal correctness, payment authorization, or integration with the team's matching/payment agent.

## Architecture and scope

```text
Transaction matching / trip candidates (teammate; optional upstream)
                       |
          Confirm / complete trip input
                       |
     AI Agent / MCP Client / MCP Inspector
                       |
        PerDiemo MCP Server (this project)
           |          |          |
       validation   parsing   calculation
                       |          |
                PerDiemo REST API (LIVE mode)
                       |
           Deterministic PerDiemo engine
                       |
            Structured calculation response
```

The MCP server operates **independently** of matching: any caller may supply correctly structured and confirmed PerDiemo trip JSON. The adapter must not turn tentative transaction evidence into confirmed travel times, border crossings, or free-meal facts.

## Requirements

- **Python 3.11+** (Python 3.12 recommended). On macOS, `python3` might still resolve to Python 3.10.
- Internet access for the initial Python package installation; network access to PerDiemo in **live** mode.
- **Optional for graphical demos:** Node.js/npm, for the official MCP Inspector.
- **Optional for a conversational LLM demo:** an MCP-compatible AI application with its own model access (e.g. Claude Desktop). This server itself does not require AWS credentials or an LLM key to calculate allowances.

### macOS / Linux — install and run all offline acceptance tests

```bash
cd perdiemo-mcp
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
./run-acceptance.sh
```

If your virtual environment is named `environment` rather than `.venv`, activate it with `source environment/bin/activate` instead. Creating a new `.venv` with Python 3.12 is recommended.

`./run-acceptance.sh` runs Python tests, an offline Mock MCP client/server test, and an MCP-to-local-fake-REST round trip. **It does not contact Render, AWS, or other public services.** Expected terminal lines include:

```text
.............................. [100%]
PASS: OFFLINE MOCK MCP discovery, status, validation, calculation and parse
PASS: MCP tool discovery, input validation, local REST round-trip, parse confirmation
```

### Windows 10/11 — install and run acceptance tests (PowerShell)

Use **PowerShell** for the commands below (not Command Prompt); install **Python 3.12** and optionally Node.js 22+ for the graphical Inspector. Check Python with `py -3.12 --version`. If the Python Launcher (`py`) is not installed, use your Python 3.12 executable instead. Run these inside the extracted `perdiemo-mcp` folder, which contains `server.py` and `pyproject.toml`.

```powershell
cd "C:\path\to\perdiemo-mcp"
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"

# Native Windows equivalent of run-acceptance.sh:
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe scripts_e2e_mock.py
.\.venv\Scripts\python.exe scripts_e2e_local.py
```

Expected: **30 Python tests pass** and both local MCP protocol tests print `PASS`. No Render or cloud API request is made. `run-acceptance.sh` is a Unix shell script; on Windows **run the three Python commands above instead**. You do not need to activate the virtual environment because all commands explicitly use its Python interpreter. If you want activation, `.\.venv\Scripts\Activate.ps1` is optional, but may be blocked by your organization's PowerShell execution policy; do not change system-wide policy just to run these tests.

To run the **optional production-API synthetic E2E** (separate from offline acceptance, and only when authorized):

```powershell
.\.venv\Scripts\python.exe scripts_e2e_live.py --confirm-production
```

This sends a synthetic request to the **actual** Render production endpoint, not a staging API. Never use personal/customer trip data.

## Start and switch the backend mode

From the project folder, with your virtual environment activated:

| Command | Purpose |
| --- | --- |
| `./start.sh mock` | Entirely offline; returns clearly labelled synthetic fixtures. |
| `./start.sh live` | Calls the existing PerDiemo **production** Render REST API. Send synthetic demo data only. |
| `./start.sh staging http://127.0.0.1:8000` | Calls a locally running PerDiemo REST instance. |
| `./start.sh staging https://your-staging.example` | Calls an approved staging backend. |

Stop the listener with `Ctrl+C` before switching modes. The MCP listener defaults to **`http://127.0.0.1:8001/mcp`**. This is separate from the upstream PerDiemo REST base URL. `127.0.0.1` is accessible only on your own computer.

`live` is real PerDiemo calculation, but **not an isolated staging backend**. The service does not silently switch to Mock if its upstream request fails. Live mode requires explicit configuration and production opt-in. Never use customer information in a hackathon demo.

The same configuration without the helper script:

```bash
# Mock
PERDIEMO_API_MODE=mock python server.py

# Live — invokes the real production REST API
PERDIEMO_API_MODE=live \
PERDIEMO_API_URL=https://perdiemo-backend-production.onrender.com \
PERDIEMO_ALLOW_PRODUCTION=true \
python server.py
```

The `.env.example` file is reference documentation; variables are **not automatically loaded**. Omitting mode/backend configuration causes safe `BACKEND_NOT_CONFIGURED` errors rather than a default production call.

### Windows PowerShell — start Mock, Live, or Staging (no Bash required)

The existing `start.sh` works on macOS/Linux. On **Windows**, run `server.py` directly with the equivalent environment variables. Open **PowerShell** in `perdiemo-mcp` and keep the window running. The HTTP MCP endpoint is `http://127.0.0.1:8001/mcp`. Before changing modes, press `Ctrl+C` and start again.

**Offline Mock:**

```powershell
$env:PERDIEMO_MCP_TRANSPORT = "streamable-http"
$env:PERDIEMO_API_MODE = "mock"
Remove-Item Env:PERDIEMO_API_URL -ErrorAction SilentlyContinue
Remove-Item Env:PERDIEMO_ALLOW_PRODUCTION -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe server.py
```

**Live Render API (synthetic demonstration data only, with permission):**

```powershell
$env:PERDIEMO_MCP_TRANSPORT = "streamable-http"
$env:PERDIEMO_API_MODE = "live"
$env:PERDIEMO_API_URL = "https://perdiemo-backend-production.onrender.com"
$env:PERDIEMO_ALLOW_PRODUCTION = "true"
.\.venv\Scripts\python.exe server.py
```

**Approved staging or locally hosted PerDiemo REST backend:**

```powershell
$env:PERDIEMO_MCP_TRANSPORT = "streamable-http"
$env:PERDIEMO_API_MODE = "live"
$env:PERDIEMO_API_URL = "http://127.0.0.1:8000"  # replace with your actual test REST URL
Remove-Item Env:PERDIEMO_ALLOW_PRODUCTION -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe server.py
```

`PERDIEMO_API_MODE=live` with a *staging* URL means genuine REST requests to that chosen backend, not the Mock fixture. The `.env.example` file is **not auto-loaded**. PowerShell environment variables persist in the **current window** until changed/cleared; restart the terminal or explicitly switch modes to prevent accidental production calls.

### Repeat the verified one-shot live API test

```bash
python scripts_e2e_live.py --confirm-production
```

This discovers the real MCP tools, validates a **synthetic** 2025 trip, then calls the live `/api/calculate` endpoint through MCP. No payments are made, and the natural-language parser is not invoked. Use `--confirm-production` only if sending this synthetic request to PerDiemo's real backend is permitted.

## Available MCP tools

| Tool | Input | Result |
| --- | --- | --- |
| `get_backend_status` | None | Backend mode and destination; no external request. |
| `validate_trip_input` | `year`, `trips`, optional `include_routes` | Offline validation errors or success. |
| `calculate_trip_allowance` | `year`, `trips`, optional `include_routes` | PerDiemo allowance calculation plus mode/source metadata. |
| `parse_trip_itinerary` | `text` | Unverified natural-language extraction through PerDiemo's existing parser; may consume upstream LLM tokens in Live mode. |

Example calculation request: `examples/native_calculate.json`. **Pass the entire object**, not just its `trips` array, when an MCP client offers an **Edit as JSON** panel for the entire tool's arguments:

```json
{
  "year": 2025,
  "include_routes": true,
  "trips": [
    {
      "id_cesty": "DEMO-001",
      "vlastnictvi_vozidla": "SLUZEBNI",
      "itinerar": [
        {"typ": "ODJEZD", "datum": "2025-06-10T07:00", "misto": "Prague", "country_code": "CZE"},
        {"typ": "PRIJEZD", "datum": "2025-06-10T11:00", "misto": "Vienna", "country_code": "AUT"},
        {"typ": "NÁVRAT_ODJEZD", "datum": "2025-06-11T16:00", "misto": "Vienna", "country_code": "AUT"},
        {"typ": "KREUZ_NAVRAT", "datum": "2025-06-11T20:00", "misto": "Prague", "country_code": "CZE"}
      ]
    }
  ]
}
```

The short snippet illustrates **structure only**: for a reliable cross-border calculation, use the full verified example with explicit border events and other required information.

### Response semantics and safeguards

- `mode: "mock"`, `synthetic: true`: synthetic fixture; mock amount `123.45 CZK` has **no legal meaning** and no verification signature.
- `mode: "live"`, `synthetic: false`: a real backend calculation occurred; the *submitted trip input may still be entirely synthetic*.
- `may_be_used_for_payment: false`: this tool **never** grants approval to pay, whether Live or Mock.
- `calculation`: contains the PerDiemo REST response; upstream errors return structured failures instead of a mock fallback.
- PerDiemo's `verification_signature` is returned as evidence; this MCP server does **not independently cryptographically verify** it.
- `parse_trip_itinerary` produces **unverified** output: parser fields such as `itinerary` and `typ_vozidla` must be mapped to the calculator's `itinerar` and `vlastnictvi_vozidla`, and mandatory missing details must be confirmed.

## Graphical MCP demo — MCP Inspector

The **MCP Inspector** is an interactive GUI for discovering and invoking MCP tools. It is an **MCP client, not an LLM/agent**. Use this demo to show genuine protocol integration without creating a custom frontend.

### 1. Start the PerDiemo MCP server

In **Terminal A**:

```bash
cd /absolute/path/to/perdiemo-mcp
source .venv/bin/activate
./start.sh live
```

For an entirely offline rehearsal, use `./start.sh mock` instead. Keep Terminal A open.

### 2. Start MCP Inspector

In **Terminal B**:

```bash
node --version
npx -y @modelcontextprotocol/inspector
```

Use a Node.js version supported by the installed Inspector release. Open the URL printed by the CLI (commonly `http://localhost:6274`, possibly with a local authentication token). Do not publish the Inspector's token or expose its local proxy port to the internet.

In Inspector, choose **Add Server** if shown, then:

| Field | Value |
| --- | --- |
| Name | `PerDiemo MCP` |
| Transport | **Streamable HTTP** |
| Server URL | `http://127.0.0.1:8001/mcp` |
| Authentication | None (**localhost demo only**) |

Click **Connect**; open **Tools** and **List Tools** if necessary. The four tools above should appear.

### Windows PowerShell — graphical Inspector demo

The same Inspector UI works on Windows. Use **two PowerShell windows**:

1. **Window A:** start `server.py` using the **Windows Mock or Live** instructions above. Leave it running.
2. **Window B:** check Node.js/npm and launch Inspector:

```powershell
node --version
npm.cmd --version
npx.cmd -y @modelcontextprotocol/inspector
```

Open the **full** local Inspector URL printed in Window B (it may include an access token). Choose **Add Server → Streamable HTTP → `http://127.0.0.1:8001/mcp` → Connect → Tools**. Authentication is **None only for this loopback demo**. If PowerShell blocks `npx.ps1`, using `npx.cmd` as above avoids needing to change the execution policy.

To copy the **complete tool arguments** as JSON on Windows (equivalent to macOS `pbcopy`):

```powershell
Get-Content -Raw -Encoding UTF8 .\examples\native_calculate.json | Set-Clipboard
```

Paste into **Edit as JSON for the entire `calculate_trip_allowance` tool arguments**. If the editor is specifically for the `trips` field (and expects a JSON array, not an object), copy only that field:

```powershell
$payload = Get-Content -Raw -Encoding UTF8 .\examples\native_calculate.json | ConvertFrom-Json
$payload.trips | ConvertTo-Json -Depth 20 | Set-Clipboard
```

If you can discover tools but clicking **Execute** stays disabled, verify whether the editor expects the full `{ "year": ..., "trips": [...] }` object or just the `[...]` array. Do **not** try to run `calculate_trip_allowance` with an unconfirmed inferred trip. When finished, press `Ctrl+C` in both windows.

### 3. Present the demo (2–3 minutes)

**A — Check connection.** Run `get_backend_status` without arguments. Confirm `mode: "live"` and `backend: "https://perdiemo-backend-production.onrender.com"`. In Mock mode, it will instead identify the offline fixture.

**B — Validate a trip.** Choose `validate_trip_input`. Pass `year = 2025`, `include_routes = true`, and the array under `trips` in the example file. Demonstrate that a missing `datum` for one leg is rejected. If the client offers **Edit as JSON for all tool arguments**, paste the **entire** `examples/native_calculate.json` object instead.

**C — Calculate for real.** Choose `calculate_trip_allowance`. Paste the same valid example. On macOS, the fastest way to copy the entire Tool Arguments object is:

```bash
pbcopy < examples/native_calculate.json
```

Then use **Edit as JSON** for the **whole tool call** → Select All → Paste → **Run Tool / Execute**. If Inspector opens a JSON editor **only for `trips`**, paste just the `trips` array instead:

```bash
python -c 'import json; print(json.dumps(json.load(open("examples/native_calculate.json"))["trips"], ensure_ascii=False))' | pbcopy
```

You should see a structured `calculation.metadata` response. In the owner's verified 2025 synthetic sample, `total_stravne_czk` was **`1226.61`** and `verification_signature` was a nonempty SHA-256 hex string. A recalculation may produce different values if upstream rate data or implementation changes.

**D — Optional natural-language parsing.** Run `parse_trip_itinerary` with a synthetic English or Czech travel description. Explain that this feature is provided by the **existing PerDiemo backend** and may invoke its own LLM; the output requires human confirmation. Skip this step if conserving upstream LLM usage or if a parse quota is unknown.

**Troubleshooting:** If Connect fails, check Terminal A, `/mcp` path, `Streamable HTTP` transport, local port 8001, and browser/proxy console messages. If **Execute** is disabled after pasting JSON, check whether the editor expects the **entire Tool Arguments object `{...}`** or the **`trips` array `[...]`**. Switching between those is a common UI input error; no server code change is needed.

### Suggested 45-second presentation script

> This is our standalone PerDiemo MCP adapter. An MCP client can discover the tools, validate confirmed travel input, and call the existing PerDiemo calculation engine. Here is the backend mode and tool list; now I'll run a synthetic trip through the real REST API. The returned statutory allowance and verification signature come from PerDiemo, not from an LLM. The matching teammate can supply trip candidates, while a human or coordinating agent confirms the missing facts before this calculation tool is called. The adapter never initiates payments.

## Connect it to an actual LLM/agent

**Important distinction:** MCP Inspector calls tools manually. An MCP-compatible **AI host/client** is needed if you want an LLM to decide when to call `validate_trip_input` or `calculate_trip_allowance`. The MCP server itself is **not** an LLM, and it does **not** automatically switch PerDiemo's existing AI parser to AWS Bedrock.

### Option A — Claude Desktop on macOS (stdio)

If Claude Desktop is installed and its version supports local MCP servers, open its MCP server configuration (on macOS, commonly `~/Library/Application Support/Claude/claude_desktop_config.json`). Add a server entry similar to the following, replacing **both absolute paths** with your own. Merge it into any existing `mcpServers` object; don't overwrite unrelated servers:

```json
{
  "mcpServers": {
    "perdiemo": {
      "command": "/ABSOLUTE/PATH/perdiemo-mcp/.venv/bin/python",
      "args": ["/ABSOLUTE/PATH/perdiemo-mcp/server.py"],
      "env": {
        "PERDIEMO_MCP_TRANSPORT": "stdio",
        "PERDIEMO_API_MODE": "live",
        "PERDIEMO_API_URL": "https://perdiemo-backend-production.onrender.com",
        "PERDIEMO_ALLOW_PRODUCTION": "true"
      }
    }
  }
}
```

Restart Claude Desktop to reload its MCP configuration. You **do not** need to run `./start.sh live` simultaneously for a stdio client: Claude Desktop launches its own MCP subprocess. To rehearse without network access, set `PERDIEMO_API_MODE` to `mock` and remove the live-backend/production variables.

Ask the AI host something like:

> Discover the PerDiemo tools. First check backend status, then validate this synthetic Prague–Vienna business trip. If it is structurally valid, invoke the calculation tool and explain the result. Do not guess any missing travel timestamps, do not initiate a payment, and show the verification signature returned by PerDiemo.

The LLM's responses and tool-use permissions depend on the host. The LLM may ask to approve tool calls. **No LLM API key needs to be injected into the PerDiemo MCP server** for these calculations; the AI host supplies its own model access.

### Option A2 — Claude Desktop on Windows (stdio; optional LLM demo)

On **Windows**, the Claude Desktop config is commonly located at `%APPDATA%\Claude\claude_desktop_config.json` (typically `C:\Users\YOUR_USER\AppData\Roaming\Claude\claude_desktop_config.json`). You can locate the directory from PowerShell:

```powershell
Join-Path $env:APPDATA 'Claude\claude_desktop_config.json'
```

Merge this into the existing JSON config; **replace both paths** with the absolute paths to your Windows MCP project and its Python virtual environment. JSON requires doubled `\` in Windows file paths:

```json
{
  "mcpServers": {
    "perdiemo": {
      "command": "C:\\Users\\YOUR_USER\\Projects\\perdiemo-mcp\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\YOUR_USER\\Projects\\perdiemo-mcp\\server.py"],
      "env": {
        "PERDIEMO_MCP_TRANSPORT": "stdio",
        "PERDIEMO_API_MODE": "mock"
      }
    }
  }
}
```

Restart Claude Desktop. This is a **Mock LLM tool-use rehearsal**; to use the real PerDiemo REST calculation, explicitly replace `"mock"` with `"live"` and add `"PERDIEMO_API_URL": "https://perdiemo-backend-production.onrender.com"` and `"PERDIEMO_ALLOW_PRODUCTION": "true"` in `env`, then restart again. Only send synthetic data. Claude Desktop launches the server itself in **stdio** mode; **do not** start the separate HTTP server for this connection. The AI app provides its own LLM access; no Bedrock or Claude key is needed inside this MCP server.

### Option B — An AI host with native Streamable HTTP MCP

Start the MCP HTTP server in Live mode (`./start.sh live` on macOS/Linux; the **Windows PowerShell Live** command above on Windows), then configure the AI host's custom MCP connector with:

```text
Transport: Streamable HTTP
URL:       http://127.0.0.1:8001/mcp
```

This works only if the **host itself runs on the same computer** or can reach that address. A cloud-hosted agent cannot reach your computer's localhost. Remote deployments need an authenticated HTTPS MCP endpoint (e.g. managed platform or protected network). Clients that support only stdio may use their normal local subprocess configuration; `mcp-remote` is only a bridge for remote HTTP MCP endpoints, not a required package to build this Python MCP server.

### Can the server itself call an LLM?

Only the existing `parse_trip_itinerary(text)` tool indirectly: in Live mode it forwards to PerDiemo's `/api/parse-itinerary`, whose backend documentation describes GenAI parsing. `calculate_trip_allowance` instead calls the deterministic REST calculator. This MCP release contains **no standalone Bedrock/Gemini/Claude client** or embedded agent loop.

## Team handoff / private repository integration

Keep this folder self-contained as `integrations/perdiemo-mcp/` in the team repository. Do **not** modify the existing Streamlit app, matching pipeline, payment logic, or statutory calculation rules as part of the MCP handoff.

Before committing:

1. Confirm the owner has granted access to the **correct private repository** and that your branch is based on current `main`.
2. Exclude local virtual environments (`.venv/`, `environment/`), `.env`, session/auth tokens, and caches. Review `git status` and the staged diff before pushing.
3. Run `./run-acceptance.sh` on macOS/Linux, or the three PowerShell Python tests in the Windows section. Record the live E2E result separately: `python scripts_e2e_live.py --confirm-production` only when the owner approves hitting the existing production API with synthetic inputs.
4. Open a feature branch and PR rather than pushing straight to `main`, unless the owner explicitly requests otherwise.
5. Include the MCP endpoint, transport, four Tool names, required trip schema, and instructions for testing in the PR description.

**Remote deployment warning:** Localhost has no MCP authentication. Never expose `0.0.0.0:8001` publicly without a suitable protected ingress, access control, and HTTPS. An upstream REST API without a token does not mean a newly published MCP endpoint should be unauthenticated.

## Limitations and sources

- Native request schema and upstream REST endpoints: [PerDiemo API.md](https://github.com/dataquo/PerDiemoEU/blob/main/API.md).
- Protocol and server runtime: [official MCP Python SDK](https://py.sdk.modelcontextprotocol.io/).
- Graphical testing: [MCP Inspector](https://github.com/modelcontextprotocol/inspector).
- No independent verification of Czech legal calculations, hash authenticity, meal eligibility, travel approval, payment settlement, or agent transaction matching.
- No AWS, Apify, npm, or team-agent deployment is included in **v0.2**. Those are separate distribution/integration steps and should not be represented as passed acceptance tests.
