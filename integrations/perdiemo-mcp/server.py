"""Entrypoint for the official MCP Python SDK v2 CLI.

Run after `pip install -e .`:
    python server.py                              # streamable-http :8001/mcp
    PERDIEMO_MCP_TRANSPORT=stdio python server.py # stdio

No AWS credentials, payment endpoints, or production URL are required for
registration/discovery of tools. Backend calls fail safely if mode is not explicitly configured.
"""
from __future__ import annotations

import os
from typing import Any

from mcp.server import MCPServer

from perdiemo_mcp.schema import Trip, validate_request
from perdiemo_mcp.modes import describe_backend
from perdiemo_mcp.service import calculate_allowance, parse_itinerary

mcp = MCPServer("PerDiemo Statutory Travel Allowance")


@mcp.tool()
def get_backend_status() -> dict[str, Any]:
    """Identify mock/live mode and effective backend without sending network requests."""
    return describe_backend()


@mcp.tool()
def validate_trip_input(year: int, trips: list[dict[str, Any]], include_routes: bool = True) -> dict[str, Any]:
    """Validate PerDiemo trip JSON offline, without calling a backend.

    Requires confirmed event timestamps (including border crossing times when
    applicable), vehicle classification and country codes. Does not infer trips
    from card transactions. Use BEFORE calculate_trip_allowance.
    """
    return validate_request({"year": year, "trips": trips, "include_routes": include_routes})


@mcp.tool()
def calculate_trip_allowance(year: int, trips: list[Trip], include_routes: bool = True) -> dict[str, Any]:
    """Calculate Czech statutory travel allowances using PerDiemo REST.

    `trips` uses native /api/calculate `itinerar`, `id_cesty`, `vlastnictvi_vozidla`,
    `bezplatna_strava` schema. Only submit CONFIRMED trip information; transaction
    matches alone cannot determine statutory eligibility or meal reductions.
    This tool NEVER executes a payment or returns an approved reimbursement.
    """
    return calculate_allowance({"year": year, "trips": [t.model_dump(exclude_none=True) for t in trips], "include_routes": include_routes})


@mcp.tool()
def parse_trip_itinerary(text: str) -> dict[str, Any]:
    """Optionally parse free-text travel notes through existing PerDiemo REST.

    Result is unverified; `itinerary` and `typ_vozidla` must be mapped into
    `itinerar` and `vlastnictvi_vozidla`, and missing details confirmed, before
    calling calculate_trip_allowance. May consume LLM tokens on the backend.
    """
    return parse_itinerary(text)


if __name__ == "__main__":
    transport = os.environ.get("PERDIEMO_MCP_TRANSPORT", "streamable-http")
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "streamable-http":
        mcp.run(
            transport="streamable-http",
            host=os.environ.get("PERDIEMO_MCP_HOST", "127.0.0.1"),
            port=int(os.environ.get("PERDIEMO_MCP_PORT", "8001")),
        )
    else:
        raise SystemExit("PERDIEMO_MCP_TRANSPORT must be stdio or streamable-http")
