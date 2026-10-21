"""Real MCP -> public PerDiemo REST E2E, opt-in ONLY, synthetic inputs.

Usage: python scripts_e2e_live.py --confirm-production
NOTE: this sends a synthetic test POST to the PRODUCTION backend, not staging.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import subprocess
import sys

from mcp import Client
from scripts_e2e_local import PAYLOAD, ROOT, available_port, wait_for_port

PRODUCTION_URL = "https://perdiemo-backend-production.onrender.com"


async def check(port: int) -> None:
    async with Client(f"http://127.0.0.1:{port}/mcp") as client:
        tools = await client.list_tools()
        names = {t.name for t in tools.tools}
        required = {"get_backend_status", "validate_trip_input", "calculate_trip_allowance"}
        assert required <= names, f"Missing MCP tools: {required - names}"
        status_call = await client.call_tool("get_backend_status", {})
        assert not status_call.is_error
        status = status_call.structured_content
        assert status and status["ok"] and status["mode"] == "live"
        assert status["backend"] == PRODUCTION_URL
        validated = await client.call_tool("validate_trip_input", PAYLOAD)
        assert not validated.is_error and validated.structured_content["ok"]
        actual = await client.call_tool("calculate_trip_allowance", PAYLOAD)
        if actual.is_error:
            raise RuntimeError(f"MCP protocol returned error: {actual.content}")
        data = actual.structured_content or {}
        if not data.get("ok"):
            raise RuntimeError(f"PerDiemo LIVE API failed: {data.get('error')}. No MOCK fallback was used.")
        assert data["mode"] == "live" and data["synthetic"] is False
        calculation = data["calculation"]
        metadata = calculation["metadata"]
        print("PASS: MCP -> LIVE PerDiemo REST (synthetic input); no mock fallback")
        print("Backend:", PRODUCTION_URL)
        print("Calculation metadata:", {
            "year": metadata.get("year"),
            "total_trips": metadata.get("total_trips"),
            "total_stravne_czk": metadata.get("total_stravne_czk"),
            "verification_signature": metadata.get("verification_signature"),
        })
        print("Note: API calculation is NOT approval to reimburse or pay anyone.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-production", action="store_true",
                        help="Explicitly consent to sending the synthetic test itinerary to PerDiemo PRODUCTION")
    args = parser.parse_args()
    if not args.confirm_production:
        parser.error("Required: --confirm-production (this performs a real POST to PRODUCTION)")
    port = available_port()
    env = os.environ.copy()
    env.update({"PERDIEMO_API_MODE": "live", "PERDIEMO_API_URL": PRODUCTION_URL,
                "PERDIEMO_ALLOW_PRODUCTION": "true", "PERDIEMO_MCP_PORT": str(port),
                "PERDIEMO_MCP_HOST": "127.0.0.1", "PERDIEMO_MCP_TRANSPORT": "streamable-http"})
    proc = subprocess.Popen([sys.executable, str(ROOT / "server.py")], cwd=ROOT,
                            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        wait_for_port(port, proc)
        asyncio.run(check(port))
    finally:
        proc.terminate()
        try:
            proc.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()


if __name__ == "__main__":
    main()
