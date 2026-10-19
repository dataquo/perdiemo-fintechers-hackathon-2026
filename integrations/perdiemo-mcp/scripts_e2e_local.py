"""End-to-end MCP protocol acceptance with ONLY a local synthetic REST fixture.

Requires installed MCP Python SDK v2. Runs both servers locally and makes zero
network calls to production or AWS. This is a contract/wiring test, not a
validation of Czech statutory calculation accuracy.
"""
from __future__ import annotations

import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time

from mcp import Client

ROOT = Path(__file__).resolve().parent
PAYLOAD = json.loads((ROOT / "examples/native_calculate.json").read_text(encoding="utf-8"))


class FakePerDiemoAPI(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        data = json.loads(body)
        if self.path == "/api/calculate":
            assert data["trips"][0]["id_cesty"] == "HACKATHON-DEMO-001"
            result = {
                "metadata": {"year": data["year"], "total_stravne_czk": 123.45,
                             "verification_signature": "a" * 64},
                "trip_reports": [],
            }
        elif self.path == "/api/parse-itinerary":
            result = {"itinerary": [], "model_used": "synthetic-fixture"}
        else:
            self.send_error(404)
            return
        output = json.dumps(result).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(output)))
        self.end_headers()
        self.wfile.write(output)


def available_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_for_port(port: int, process: subprocess.Popen, timeout: float = 15) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"MCP subprocess exited unexpectedly with {process.returncode}")
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=.25):
                return
        except OSError:
            time.sleep(.15)
    raise TimeoutError("MCP HTTP server did not listen within 15 seconds")


async def protocol_check(port: int):
    async with Client(f"http://127.0.0.1:{port}/mcp") as client:
        tools = await client.list_tools()
        tool_names = {t.name for t in tools.tools}
        required = {"validate_trip_input", "calculate_trip_allowance", "parse_trip_itinerary", "get_backend_status"}
        assert required.issubset(tool_names), f"MCP missing tools: {required - tool_names}"
        status = (await client.call_tool("get_backend_status", {})).structured_content
        assert status and status["mode"] == "live" and status["ok"] is True
        result = await client.call_tool("validate_trip_input", PAYLOAD)
        assert result.is_error is False, result.content
        content = result.structured_content
        assert content and content.get("ok") is True, content
        result = await client.call_tool("calculate_trip_allowance", PAYLOAD)
        assert result.is_error is False, result.content
        content = result.structured_content
        assert content and content.get("ok") is True, content
        assert content.get("mode") == "live" and content.get("synthetic") is False
        assert content["calculation"]["metadata"]["total_stravne_czk"] == 123.45
        result = await client.call_tool("parse_trip_itinerary", {"text": "Trip note"})
        assert result.is_error is False, result.content
        content = result.structured_content
        assert content and content.get("requires_confirmation") is True
        print("PASS: MCP tool discovery, input validation, local REST round-trip, parse confirmation")


def main():
    fixture = ThreadingHTTPServer(("127.0.0.1", 0), FakePerDiemoAPI)
    thread = threading.Thread(target=fixture.serve_forever, daemon=True)
    thread.start()
    port = available_port()
    env = os.environ.copy()
    env.update({
        "PERDIEMO_API_URL": f"http://127.0.0.1:{fixture.server_address[1]}",
        "PERDIEMO_API_MODE": "live",
        "PERDIEMO_MCP_PORT": str(port),
        "PERDIEMO_MCP_HOST": "127.0.0.1",
        "PERDIEMO_MCP_TRANSPORT": "streamable-http",
    })
    proc = subprocess.Popen(
        [sys.executable, str(ROOT / "server.py")],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    try:
        wait_for_port(port, proc)
        asyncio.run(protocol_check(port))
    finally:
        proc.terminate()
        try:
            proc.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
        fixture.shutdown()
        fixture.server_close()


if __name__ == "__main__":
    main()
