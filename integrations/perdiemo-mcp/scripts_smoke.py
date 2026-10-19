"""Offline smoke test; does not import MCP SDK or access any backend."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from perdiemo_mcp.schema import validate_request

payload = json.loads((Path(__file__).parent / "examples/native_calculate.json").read_text())
result = validate_request(payload)
print("PASS: native trip validation" if result["ok"] else result)
raise SystemExit(0 if result["ok"] else 1)
