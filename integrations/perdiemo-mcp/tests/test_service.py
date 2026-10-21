import json
from pathlib import Path
from conftest import example
from perdiemo_mcp.adapter import BackendError, ConfigurationError, get_base_url
from perdiemo_mcp.service import calculate_allowance, parse_itinerary


class StubAdapter:
    def __init__(self):
        self.calls = []

    def calculate(self, payload):
        self.calls.append(payload)
        return {"metadata": {"total_stravne_czk": 1226.61, "verification_signature": "abc"}, "trip_reports": []}

    def parse(self, text):
        return {"itinerary": [], "model_used": "test-stub"}


def test_valid_calculation_calls_adapter_once():
    adapter = StubAdapter()
    result = calculate_allowance(example(), lambda: adapter)
    assert result["ok"] is True
    assert result["calculation"]["metadata"]["total_stravne_czk"] == 1226.61
    assert len(adapter.calls) == 1
    assert adapter.calls[0]["year"] == 2025


def test_invalid_input_never_calls_adapter():
    def must_not_call():
        raise AssertionError("should not construct HTTP adapter")
    assert calculate_allowance({"trips": []}, must_not_call)["ok"] is False


def test_unconfigured_fails_closed(monkeypatch):
    monkeypatch.delenv("PERDIEMO_API_URL", raising=False)
    result = calculate_allowance(example())
    assert result["ok"] is False
    assert result["error"]["code"] == "BACKEND_NOT_CONFIGURED"


def test_production_blocked_by_default(monkeypatch):
    monkeypatch.setenv("PERDIEMO_API_URL", "https://perdiemo-backend-production.onrender.com")
    monkeypatch.delenv("PERDIEMO_ALLOW_PRODUCTION", raising=False)
    result = calculate_allowance(example())
    assert result["error"]["code"] == "BACKEND_NOT_CONFIGURED"


def test_local_url_allowed(monkeypatch):
    monkeypatch.setenv("PERDIEMO_API_URL", "http://127.0.0.1:8000")
    assert get_base_url() == "http://127.0.0.1:8000"


def test_insecure_remote_blocked(monkeypatch):
    monkeypatch.setenv("PERDIEMO_API_URL", "http://public.example:8080")
    monkeypatch.delenv("PERDIEMO_ALLOW_INSECURE_HTTP", raising=False)
    try:
        get_base_url()
    except ConfigurationError:
        pass
    else:
        raise AssertionError("remote HTTP must be blocked")


def test_upstream_error_is_structured():
    class BrokenAdapter:
        def calculate(self, payload):
            raise BackendError("UPSTREAM_TIMEOUT", "request timed out")
    result = calculate_allowance(example(), lambda: BrokenAdapter())
    assert result["ok"] is False
    assert result["error"]["code"] == "UPSTREAM_TIMEOUT"


def test_parse_is_explicitly_unverified():
    result = parse_itinerary("Prague to Vienna", lambda: StubAdapter())
    assert result["ok"] is True
    assert result["requires_confirmation"] is True


def test_parse_empty_rejected_without_http():
    assert parse_itinerary(" ")["error"]["code"] == "INVALID_TEXT"


def test_malformed_backend_calculation_is_not_success():
    class MalformedAdapter:
        def calculate(self, payload):
            return {"error": "bad"}
    r = calculate_allowance(example(), lambda: MalformedAdapter())
    assert not r["ok"]
    assert r["error"]["code"] == "BAD_BACKEND_RESPONSE"


def test_malformed_parse_result_is_not_success():
    class MalformedAdapter:
        def parse(self, text):
            return {"error": "bad"}
    r = parse_itinerary("Paris business trip", lambda: MalformedAdapter())
    assert not r["ok"]
    assert r["error"]["code"] == "BAD_BACKEND_RESPONSE"
