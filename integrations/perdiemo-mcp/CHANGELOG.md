# Changelog

## v0.2 — explicit Mock/Live API switch

- New `PERDIEMO_API_MODE=mock|live` and `./start.sh mock|live|staging <url>`.
- `get_backend_status` tool reports effective mode/configuration with no network calls.
- Mock adapter for offline demos, unmistakably fictitious output; no statutory result or hash impersonation.
- Real REST mode to original PerDiemo API; production access requires explicit opt-in.
- No automatic fallback to mock on live HTTP/timeouts/schema failures.
- Added mock-vs-live tests and opt-in MCP protocol → real REST smoke script.
- Existing three MCP tool names and native input schemas retained.
- No modifications to Hackathon repo, matching, Auditor, Bedrock, payment, or PerDiemo's calculation logic.
