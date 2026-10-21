"""Real MCP protocol E2E with the explicit offline MOCK backend mode."""
from __future__ import annotations

import asyncio
import os
import subprocess
import sys

from mcp import Client
from scripts_e2e_local import PAYLOAD, ROOT, available_port, wait_for_port


async def check(port: int) -> None:
    async with Client(f"http://127.0.0.1:{port}/mcp") as client:
        tools = await client.list_tools()
        names = {t.name for t in tools.tools}
        assert {"get_backend_status", "validate_trip_input", "calculate_trip_allowance", "parse_trip_itinerary"} <= names
        status = (await client.call_tool("get_backend_status", {})).structured_content
        assert status and status["mode"] == "mock" and status["synthetic"] is True
        result = (await client.call_tool("validate_trip_input", PAYLOAD)).structured_content
        assert result and result["ok"] is True
        result = (await client.call_tool("calculate_trip_allowance", PAYLOAD)).structured_content
        assert result and result["ok"] is True and result["synthetic"] is True
        assert result["calculation"]["metadata"]["total_stravne_czk"] == 123.45
        parsed = (await client.call_tool("parse_trip_itinerary", {"text": "Synthetic example"})).structured_content
        assert parsed and parsed["mode"] == "mock" and parsed["requires_confirmation"]
    print("PASS: OFFLINE MOCK MCP discovery, status, validation, calculation and parse")


def main() -> None:
    port = available_port()
    env = os.environ.copy()
    env.update({"PERDIEMO_API_MODE": "mock", "PERDIEMO_MCP_PORT": str(port),
                "PERDIEMO_MCP_HOST": "127.0.0.1", "PERDIEMO_MCP_TRANSPORT": "streamable-http"})
    env.pop("PERDIEMO_API_URL", None)
    env.pop("PERDIEMO_ALLOW_PRODUCTION", None)
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
