from perdiemo_mcp.adapter import RESTAdapter, BackendError


class Response:
    def __init__(self, value=None, status=200, broken_json=False):
        self.value, self.status_code, self.broken_json = value or {}, status, broken_json

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.HTTPError(response=self)

    def json(self):
        if self.broken_json:
            import requests
            raise requests.exceptions.JSONDecodeError("bad JSON", "not JSON", 0)
        return self.value


class StubSession:
    def __init__(self, response):
        self.response = response
        self.headers = {}
        self.last = None

    def request(self, method, url, json=None, timeout=None):
        self.last = {"method": method, "url": url, "json": json, "timeout": timeout}
        return self.response


def test_request_uses_exact_documented_endpoint():
    fake = StubSession(Response({"metadata": {"year": 2025}}))
    client = RESTAdapter("http://127.0.0.1:8000", fake)
    result = client.calculate({"year": 2025, "trips": []})
    assert result == {"metadata": {"year": 2025}}
    assert fake.last["url"] == "http://127.0.0.1:8000/api/calculate"
    assert fake.last["method"] == "POST"


def test_http_failure_is_not_silent():
    fake = StubSession(Response(status=422))
    client = RESTAdapter("http://127.0.0.1:8000", fake)
    try:
        client.calculate({})
    except BackendError as exc:
        assert exc.code == "UPSTREAM_HTTP_ERROR"
        assert exc.http_status == 422
    else:
        raise AssertionError("should report upstream 422")
