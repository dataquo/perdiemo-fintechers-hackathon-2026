"""Narrow REST client that can be used independently of the Hackathon repo."""
from __future__ import annotations

import os
from urllib.parse import urlparse
from typing import Any

import requests

PRODUCTION_HOST = "perdiemo-backend-production.onrender.com"


class ConfigurationError(Exception):
    pass


class BackendError(Exception):
    def __init__(self, code: str, message: str, http_status: int | None = None):
        super().__init__(message)
        self.code, self.http_status = code, http_status


def _enabled(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes"}


def get_base_url() -> str:
    url = os.environ.get("PERDIEMO_API_URL", "").strip().rstrip("/")
    if not url:
        raise ConfigurationError(
            "PERDIEMO_API_URL is missing; set it to an isolated local/staging API URL."
        )
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ConfigurationError("PERDIEMO_API_URL must be a valid http(s) URL.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ConfigurationError("PERDIEMO_API_URL must not contain credentials, query or fragment.")
    if parsed.hostname.lower() == PRODUCTION_HOST and not _enabled("PERDIEMO_ALLOW_PRODUCTION"):
        raise ConfigurationError(
            "Production PerDiemo is disabled for hackathon development; use local/staging."
        )
    if parsed.scheme == "http" and parsed.hostname not in ("localhost", "127.0.0.1", "::1") \
            and not _enabled("PERDIEMO_ALLOW_INSECURE_HTTP"):
        raise ConfigurationError("Remote HTTP is disabled; use HTTPS or explicitly allow internal HTTP.")
    return url


class RESTAdapter:
    """GET / + POST /api/calculate + POST /api/parse-itinerary, no payment APIs."""
    mode = "live"

    def __init__(self, base_url: str | None = None, session: requests.Session | None = None):
        self.base_url = (base_url or get_base_url()).rstrip("/")
        self.session = session or requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "PerDiemo-MCP-Hackathon/0.2",
        })

    def _request(self, method: str, path: str, *, payload: dict | None = None) -> dict[str, Any]:
        try:
            response = self.session.request(
                method, f"{self.base_url}{path}", json=payload, timeout=30
            )
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise BackendError("BAD_BACKEND_RESPONSE", "Expected a JSON object from PerDiemo.")
            return data
        except requests.Timeout as exc:
            raise BackendError("UPSTREAM_TIMEOUT", "PerDiemo did not respond within 30 seconds.") from exc
        except requests.ConnectionError as exc:
            raise BackendError("UPSTREAM_UNREACHABLE", "Cannot reach the configured PerDiemo API.") from exc
        except requests.HTTPError as exc:
            status = getattr(exc.response, "status_code", None)
            raise BackendError("UPSTREAM_HTTP_ERROR", f"PerDiemo returned HTTP {status}.", status) from exc
        except requests.exceptions.JSONDecodeError as exc:
            raise BackendError("BAD_BACKEND_RESPONSE", "PerDiemo did not return valid JSON.") from exc

    def calculate(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/api/calculate", payload=payload)

    def parse(self, text: str) -> dict[str, Any]:
        return self._request("POST", "/api/parse-itinerary", payload={"text": text})

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/")
