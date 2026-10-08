import asyncio
import httpx
import pytest

from app.tools.notification_tools import NotificationServiceClient


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


def test_notification_client_forwards_jwt_and_accepts_customer_owned_notifications(monkeypatch):
    notifications_data = [{"id": 1, "user_id": 1, "status": "SENT", "title": "Test", "message": "Test notification"}]
    transport = RecordingClient(FakeResponse(200, notifications_data))
    monkeypatch.setattr("app.tools.notification_tools.httpx.AsyncClient", lambda **kwargs: transport)

    result = asyncio.run(NotificationServiceClient(base_url="http://notification-service").get_my_notifications("jwt-token", 1))

    assert result["success"] is True
    assert result["notifications"] == notifications_data
    assert transport.calls == [
        ("http://notification-service/api/v1/notifications", {"headers": {"Authorization": "Bearer jwt-token"}})
    ]


def test_notification_client_rejects_foreign_notification(monkeypatch):
    notifications_data = [{"id": 1, "user_id": 2, "status": "SENT", "title": "Test", "message": "Foreign notification"}]
    transport = RecordingClient(FakeResponse(200, notifications_data))
    monkeypatch.setattr("app.tools.notification_tools.httpx.AsyncClient", lambda **kwargs: transport)

    result = asyncio.run(NotificationServiceClient().get_my_notifications("jwt-token", 1))

    assert result["success"] is False
    assert result["error"] == "forbidden"


def test_notification_client_maps_timeout_safely(monkeypatch):
    transport = RecordingClient(error=httpx.TimeoutException("timed out"))
    monkeypatch.setattr("app.tools.notification_tools.httpx.AsyncClient", lambda **kwargs: transport)

    result = asyncio.run(NotificationServiceClient().get_my_notifications("jwt-token", 1))

    assert result["success"] is False
    assert result["error"] == "timeout"


def test_notification_client_rejects_malformed_response(monkeypatch):
    transport = RecordingClient(FakeResponse(200, {"invalid": "payload"}))
    monkeypatch.setattr("app.tools.notification_tools.httpx.AsyncClient", lambda **kwargs: transport)

    result = asyncio.run(NotificationServiceClient().get_my_notifications("jwt-token", 1))

    assert result["success"] is False
    assert result["error"] == "invalid_response"
