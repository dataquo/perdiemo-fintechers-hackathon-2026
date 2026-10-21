"""Explicit backend mode selection. No implicit production or mock fallback."""
from __future__ import annotations

import os
from typing import Any

from .adapter import ConfigurationError, RESTAdapter, get_base_url

SUPPORTED_MODES = ("mock", "live")


def current_mode() -> str:
    mode = os.getenv("PERDIEMO_API_MODE", "").strip().lower()
    if not mode:
        raise ConfigurationError(
            "PERDIEMO_API_MODE is not set. Choose mock or live explicitly, e.g. ./start.sh mock."
        )
    if mode not in SUPPORTED_MODES:
        raise ConfigurationError("PERDIEMO_API_MODE must be mock or live.")
    return mode


class MockAdapter:
    """Clearly synthetic demo responses, not a statutory calculator.

    Deliberately does not emulate legal calculation rules. The SDK/JSON transport
    can be tested without network calls; mock totals must never be paid out.
    """
    mode = "mock"

    def calculate(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "metadata": {
                "year": payload["year"],
                "total_trips": len(payload["trips"]),
                "total_stravne_czk": 123.45,
                "verification_signature": None,
            },
            "trip_reports": [],
            "_mock_notice": "SYNTHETIC FIXTURE ONLY — 123.45 CZK is not a statutory result, no audit signature exists.",
        }

    def parse(self, text: str) -> dict[str, Any]:
        return {
            "ucel_cesty": "Synthetic demo trip — not extracted from the input text",
            "typ_vozidla": "SLUZEBNI",
            "itinerary": [],
            "bezplatna_strava": {},
            "model_used": "offline-mock-no-llm",
            "_mock_notice": "SYNTHETIC FIXTURE ONLY — no AI parsing occurred.",
        }


def make_adapter() -> MockAdapter | RESTAdapter:
    mode = current_mode()
    if mode == "mock":
        return MockAdapter()
    # RESTAdapter without explicit URL validates URL + prod opt-in every time.
    return RESTAdapter(get_base_url())


def describe_backend() -> dict[str, Any]:
    """No network access, no secret values, explicit mode visibility."""
    try:
        mode = current_mode()
        if mode == "mock":
            return {"ok": True, "mode": "mock", "synthetic": True,
                    "backend": "offline fixture", "may_be_used_for_payment": False}
        url = get_base_url()
        return {"ok": True, "mode": "live", "synthetic": False,
                "backend": url, "may_be_used_for_payment": False,
                "warning": "Live API calculations are not payment approvals; use synthetic test inputs."}
    except ConfigurationError as exc:
        return {"ok": False, "mode": "disabled", "error": {
            "code": "BACKEND_NOT_CONFIGURED", "message": str(exc)}}
