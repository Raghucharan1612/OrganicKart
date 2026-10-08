import asyncio

import httpx

from app.tools.delivery_tools import DeliveryServiceClient


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class RecordingClient:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if self.error:
            raise self.error
        return self.response


def test_delivery_client_forwards_jwt_and_accepts_customer_owned_deliveries(monkeypatch):
    transport = RecordingClient(FakeResponse(200, [{"id": 9, "user_id": 1, "status": "PENDING"}]))
    monkeypatch.setattr("app.tools.delivery_tools.httpx.AsyncClient", lambda **kwargs: transport)

    result = asyncio.run(DeliveryServiceClient(base_url="http://delivery-service").get_my_deliveries("jwt-token", 1))

    assert result["success"] is True
    assert transport.calls == [
        ("http://delivery-service/api/v1/deliveries", {"headers": {"Authorization": "Bearer jwt-token"}})
    ]


def test_delivery_client_rejects_foreign_delivery(monkeypatch):
    transport = RecordingClient(FakeResponse(200, [{"id": 9, "user_id": 2, "status": "PENDING"}]))
    monkeypatch.setattr("app.tools.delivery_tools.httpx.AsyncClient", lambda **kwargs: transport)

    result = asyncio.run(DeliveryServiceClient().get_my_deliveries("jwt-token", 1))

    assert result["success"] is False
    assert result["error"] == "forbidden"


def test_delivery_client_maps_timeout_safely(monkeypatch):
    transport = RecordingClient(error=httpx.TimeoutException("timed out"))
    monkeypatch.setattr("app.tools.delivery_tools.httpx.AsyncClient", lambda **kwargs: transport)

    result = asyncio.run(DeliveryServiceClient().get_my_deliveries("jwt-token", 1))

    assert result["success"] is False
    assert result["error"] == "timeout"


def test_delivery_client_rejects_malformed_response(monkeypatch):
    transport = RecordingClient(FakeResponse(200, {"unexpected": "response"}))
    monkeypatch.setattr("app.tools.delivery_tools.httpx.AsyncClient", lambda **kwargs: transport)

    result = asyncio.run(DeliveryServiceClient().get_my_deliveries("jwt-token", 1))

    assert result["success"] is False
    assert result["error"] == "invalid_response"
