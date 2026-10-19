"""Explicit mode boundary and production opt-in tests; completely offline."""
import pytest

from conftest import example
from perdiemo_mcp.adapter import ConfigurationError
from perdiemo_mcp.modes import MockAdapter, current_mode, describe_backend, make_adapter
from perdiemo_mcp.service import calculate_allowance, parse_itinerary


def test_absent_mode_fails_closed(monkeypatch):
    monkeypatch.delenv("PERDIEMO_API_MODE", raising=False)
    assert describe_backend()["ok"] is False
    with pytest.raises(ConfigurationError):
        current_mode()


def test_invalid_mode_fails_closed(monkeypatch):
    monkeypatch.setenv("PERDIEMO_API_MODE", "automatic")
    with pytest.raises(ConfigurationError, match="mock or live"):
        make_adapter()


def test_mock_does_not_need_url_or_hit_network(monkeypatch):
    monkeypatch.setenv("PERDIEMO_API_MODE", "mock")
    monkeypatch.setenv("PERDIEMO_API_URL", "https://perdiemo-backend-production.onrender.com")
    monkeypatch.delenv("PERDIEMO_ALLOW_PRODUCTION", raising=False)
    assert isinstance(make_adapter(), MockAdapter)
    result = calculate_allowance(example())
    assert result["ok"] is True
    assert result["mode"] == "mock"
    assert result["synthetic"] is True
    assert result["may_be_used_for_payment"] is False
    assert "SYNTHETIC" in result["calculation"]["_mock_notice"]
    assert result["calculation"]["metadata"]["verification_signature"] is None
    assert describe_backend()["mode"] == "mock"


def test_mock_parse_is_not_fake_llm_claim(monkeypatch):
    monkeypatch.setenv("PERDIEMO_API_MODE", "mock")
    parsed = parse_itinerary("Prague to Vienna")
    assert parsed["ok"] and parsed["mode"] == "mock"
    assert parsed["parsed"]["model_used"] == "offline-mock-no-llm"
    assert parsed["requires_confirmation"] is True


def test_live_production_requires_opt_in(monkeypatch):
    monkeypatch.setenv("PERDIEMO_API_MODE", "live")
    monkeypatch.setenv("PERDIEMO_API_URL", "https://perdiemo-backend-production.onrender.com")
    monkeypatch.delenv("PERDIEMO_ALLOW_PRODUCTION", raising=False)
    assert describe_backend()["ok"] is False
    with pytest.raises(ConfigurationError):
        make_adapter()


def test_live_opt_in_reports_correct_url_without_network(monkeypatch):
    monkeypatch.setenv("PERDIEMO_API_MODE", "live")
    monkeypatch.setenv("PERDIEMO_API_URL", "https://perdiemo-backend-production.onrender.com")
    monkeypatch.setenv("PERDIEMO_ALLOW_PRODUCTION", "true")
    status = describe_backend()
    assert status["ok"] is True and status["mode"] == "live"
    assert status["synthetic"] is False
    assert make_adapter().base_url == "https://perdiemo-backend-production.onrender.com"


def test_live_api_error_does_not_fall_back_to_mock(monkeypatch):
    from perdiemo_mcp.adapter import BackendError
    from perdiemo_mcp.service import calculate_allowance
    class FailingLive:
        mode = "live"
        def calculate(self, payload):
            raise BackendError("UPSTREAM_UNREACHABLE", "synthetic downstream failure")
    monkeypatch.setenv("PERDIEMO_API_MODE", "live")
    result = calculate_allowance(example(), lambda: FailingLive())
    assert result["ok"] is False
    assert result["error"]["code"] == "UPSTREAM_UNREACHABLE"
    assert "calculation" not in result


def test_invalid_payload_does_not_hit_mock(monkeypatch):
    monkeypatch.setenv("PERDIEMO_API_MODE", "mock")
    result = calculate_allowance({"year": 2025, "trips": []})
    assert result["ok"] is False
    assert result["error"]["code"] == "INVALID_TRIP_INPUT"


def test_rest_adapter_identifies_as_live():
    from perdiemo_mcp.adapter import RESTAdapter
    client = RESTAdapter(base_url="http://127.0.0.1:8000")
    assert client.mode == "live"
