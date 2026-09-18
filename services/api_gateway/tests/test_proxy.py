from unittest.mock import AsyncMock, patch

import httpx
from fastapi.testclient import TestClient

from main import app


class DummyResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self):
        return self._payload


def test_auth_proxy_forwards_request_to_auth_service():
    with patch("app.core.proxy.httpx.AsyncClient") as mock_async_client:
        mock_request = AsyncMock(return_value=DummyResponse(200, {"access_token": "abc"}))
        mock_async_client.return_value.__aenter__.return_value.request = mock_request

        client = TestClient(app)
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "secret"},
            headers={"Authorization": "Bearer token"},
        )

        assert response.status_code == 200
        assert response.json() == {"access_token": "abc"}
        mock_request.assert_awaited_once()
        call_kwargs = mock_request.await_args.kwargs
        assert call_kwargs["method"] == "POST"
        assert call_kwargs["url"] == "http://localhost:8001/api/v1/auth/login"
        assert call_kwargs["headers"]["authorization"] == "Bearer token"


def test_proxy_returns_bad_gateway_when_upstream_is_unavailable():
    with patch("app.core.proxy.httpx.AsyncClient") as mock_async_client:
        mock_request = AsyncMock(side_effect=httpx.ConnectError("downstream unavailable"))
        mock_async_client.return_value.__aenter__.return_value.request = mock_request

        client = TestClient(app)
        response = client.get("/api/v1/products/")

        assert response.status_code == 502
        assert "Upstream service unavailable" in response.json()["detail"]
        assert "ConnectError" in response.json()["detail"]


def test_notification_proxy_forwards_to_notification_service():
    with patch("app.core.proxy.httpx.AsyncClient") as mock_async_client:
        mock_request = AsyncMock(return_value=DummyResponse(200, []))
        mock_async_client.return_value.__aenter__.return_value.request = mock_request

        response = TestClient(app).get(
            "/api/v1/notifications",
            headers={"Authorization": "Bearer token"},
        )

        assert response.status_code == 200
        assert response.json() == []
        assert mock_request.await_args.kwargs["url"] == "http://localhost:8006/api/v1/notifications"


def test_users_proxy_forwards_address_routes_to_user_service():
    with patch("app.core.proxy.httpx.AsyncClient") as mock_async_client:
        mock_request = AsyncMock(return_value=DummyResponse(201, {"id": 1, "label": "Home"}))
        mock_async_client.return_value.__aenter__.return_value.request = mock_request

        response = TestClient(app).post(
            "/api/v1/users/me/addresses",
            json={"label": "Home"},
            headers={"Authorization": "Bearer token"},
        )

        assert response.status_code == 200
        assert mock_request.await_args.kwargs["url"] == "http://localhost:8001/api/v1/users/me/addresses"
        assert mock_request.await_args.kwargs["method"] == "POST"


def test_orders_proxy_forwards_checkout_initiation_with_auth_body_and_idempotency_key():
    with patch("app.core.proxy.httpx.AsyncClient") as mock_async_client:
        mock_request = AsyncMock(return_value=DummyResponse(201, {"order_id": 7, "payment_status": "PAYMENT_PENDING"}))
        mock_async_client.return_value.__aenter__.return_value.request = mock_request
        request_body = {"address_id": 42}

        response = TestClient(app).post(
            "/api/v1/orders/checkout/initiate",
            json=request_body,
            headers={
                "Authorization": "Bearer customer-token",
                "Idempotency-Key": "checkout-attempt-7",
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 200
        call_kwargs = mock_request.await_args.kwargs
        assert call_kwargs["method"] == "POST"
        assert call_kwargs["url"] == "http://localhost:8004/api/v1/orders/checkout/initiate"
        assert call_kwargs["content"] == b'{"address_id":42}'
        assert call_kwargs["headers"]["authorization"] == "Bearer customer-token"
        assert call_kwargs["headers"]["idempotency-key"] == "checkout-attempt-7"
        assert call_kwargs["headers"]["content-type"] == "application/json"
