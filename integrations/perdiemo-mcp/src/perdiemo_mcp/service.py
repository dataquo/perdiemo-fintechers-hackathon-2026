"""Purely defined service boundary, independent of MCP SDK and matching agent."""
from __future__ import annotations

from typing import Any, Callable

from .adapter import BackendError, ConfigurationError, RESTAdapter
from .schema import validate_request
from .modes import make_adapter


def _failure(exc: BackendError | ConfigurationError) -> dict[str, Any]:
    if isinstance(exc, ConfigurationError):
        return {"ok": False, "error": {"code": "BACKEND_NOT_CONFIGURED", "message": str(exc)}}
    error: dict[str, Any] = {"code": exc.code, "message": str(exc)}
    if exc.http_status is not None:
        error["http_status"] = exc.http_status
    return {"ok": False, "error": error}


def calculate_allowance(
    payload: dict[str, Any], adapter_factory: Callable[[], RESTAdapter] = make_adapter
) -> dict[str, Any]:
    checked = validate_request(payload)
    if not checked["ok"]:
        return checked
    try:
        adapter = adapter_factory()
        result = adapter.calculate(checked["payload"])
    except (BackendError, ConfigurationError) as exc:
        return _failure(exc)
    if not isinstance(result.get("metadata"), dict) or not isinstance(result.get("trip_reports"), list):
        return {"ok": False, "error": {"code": "BAD_BACKEND_RESPONSE",
                "message": "PerDiemo calculation response lacks documented metadata/trip_reports."}}
    # Backend outputs are passed through unchanged; not reinterpreted as net
    # payment obligations or re-calculated by an LLM / middleware.
    mode = getattr(adapter, "mode", "test-or-custom")
    return {"ok": True, "calculation": result,
            "mode": mode, "synthetic": mode == "mock",
            "may_be_used_for_payment": False,
            "source": "Offline synthetic fixture" if mode == "mock" else "PerDiemo REST /api/calculate"}


def parse_itinerary(
    text: str, adapter_factory: Callable[[], RESTAdapter] = make_adapter
) -> dict[str, Any]:
    if not isinstance(text, str) or not text.strip() or len(text) > 15000:
        return {"ok": False, "error": {"code": "INVALID_TEXT", "message":
                "Provide nonempty itinerary text up to 15,000 characters."}}
    try:
        adapter = adapter_factory()
        result = adapter.parse(text)
    except (BackendError, ConfigurationError) as exc:
        return _failure(exc)
    if not isinstance(result.get("itinerary"), list):
        return {"ok": False, "error": {"code": "BAD_BACKEND_RESPONSE",
                "message": "PerDiemo parser response lacks documented itinerary list."}}
    mode = getattr(adapter, "mode", "test-or-custom")
    return {
        "ok": True,
        "mode": mode, "synthetic": mode == "mock",
        "parsed": result,
        "requires_confirmation": True,
        "warning": "AI-extracted itinerary is unverified. Confirm required details before calculation.",
        "source": "Offline synthetic fixture" if mode == "mock" else "PerDiemo REST /api/parse-itinerary",
    }
