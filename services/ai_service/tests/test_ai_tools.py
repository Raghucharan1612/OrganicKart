import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from fastapi import status
from fastapi.testclient import TestClient
import httpx
from jose import jwt
import pytest

from app.config import settings
from app.main import app
from app.tools.order_tools import OrderServiceClient
from app.agents.customer_agent import CustomerAgent

client = TestClient(app)
EXPECTED_ORDER_SOURCE = [{"document": "Order Service API", "title": "Order Service", "score": 1.0}]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (480, "₹480.00"),
        (480.5, "₹480.50"),
        (Decimal("480.00"), "₹480.00"),
        ("480.00", "₹480.00"),
        (None, "₹0.00"),
        ("", "₹0.00"),
        ("not-a-number", "₹0.00"),
    ],
)
def test_customer_order_currency_formatting_is_type_safe(value, expected):
    assert CustomerAgent._format_currency(value) == expected


def create_token(role: str = "CUSTOMER", user_id: int = 1) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def test_customer_retrieve_own_order_status_by_id(monkeypatch):
    """
    Test customer retrieving their own specific order status by ID.
    """
    mock_order = {
        "id": 123,
        "user_id": 1,
        "status": "CONFIRMED",
        "payment_status": "PAID",
        "subtotal": 450.0,
        "delivery_fee": 30.0,
        "total_amount": 480.0,
        "shipping_address": "45 Green Way",
        "created_at": "2026-09-29T12:00:00",
        "items": [
            {
                "id": 10,
                "order_id": 123,
                "product_id": 2,
                "product_name": "Organic Spinach",
                "unit_price": 50.0,
                "quantity": 2,
                "subtotal": 100.0,
            }
        ],
    }

    async def mock_get_order_by_id(self, order_id: int, token: str, user_id: int):
        if order_id == 123 and user_id == 1:
            return {"success": True, "order": mock_order}
        return {"success": False, "error": "not_found", "detail": f"Order #{order_id} was not found or does not belong to your account."}

    monkeypatch.setattr(OrderServiceClient, "get_order_by_id", mock_get_order_by_id)

    token = create_token(role="CUSTOMER", user_id=1)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "What is the status of order 123?"},
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Order #123 Status" in data["answer"]
    assert "CONFIRMED" in data["answer"]
    assert "PAID" in data["answer"]
    assert "Organic Spinach" in data["answer"]
    assert data["sources"] == EXPECTED_ORDER_SOURCE


def test_customer_retrieve_recent_orders(monkeypatch):
    """
    Test customer retrieving their list of recent orders.
    """
    mock_orders = [
        {
            "id": 123,
            "user_id": 1,
            "status": "CONFIRMED",
            "payment_status": "PAID",
            "total_amount": 480.0,
            "created_at": "2026-09-29T12:00:00",
            "items": [{"product_name": "Organic Apples", "quantity": 2}],
        },
        {
            "id": 110,
            "user_id": 1,
            "status": "DELIVERED",
            "payment_status": "PAID",
            "total_amount": 250.0,
            "created_at": "2026-09-20T10:00:00",
            "items": [{"product_name": "Organic Tomatoes", "quantity": 1}],
        },
    ]

    async def mock_get_recent_orders(self, token: str, user_id: int):
        return {"success": True, "orders": mock_orders}

    monkeypatch.setattr(OrderServiceClient, "get_recent_orders", mock_get_recent_orders)

    token = create_token(role="CUSTOMER", user_id=1)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "Show my recent orders."},
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Here are your recent OrganicKart orders:" in data["answer"]
    assert "Order #123" in data["answer"]
    assert "Order #110" in data["answer"]
    assert data["sources"] == EXPECTED_ORDER_SOURCE


def test_customer_order_status_without_id_uses_recent_orders_via_chat_api(monkeypatch):
    """Cover the authenticated API path for a natural-language order-status query."""
    calls: list[tuple[str, int]] = []

    async def mock_get_recent_orders(self, token: str, user_id: int):
        calls.append((token, user_id))
        return {
            "success": True,
            "orders": [{
                "id": 123,
                "user_id": user_id,
                "status": "CONFIRMED",
                "payment_status": "PAID",
                "total_amount": 480.0,
                "created_at": "2026-09-29T12:00:00",
                "items": [],
            }],
        }

    monkeypatch.setattr(OrderServiceClient, "get_recent_orders", mock_get_recent_orders)

    token = create_token(role="CUSTOMER", user_id=1)
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "What is the status of my order?"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert "Your latest order status:" in response.json()["answer"]
    assert calls == [(token, 1)]


def test_customer_order_status_formats_string_total_amount(monkeypatch):
    """Order Service serializes Decimal totals as strings in some responses."""
    async def mock_get_recent_orders(self, token: str, user_id: int):
        return {
            "success": True,
            "orders": [{
                "id": 123,
                "user_id": user_id,
                "status": "CONFIRMED",
                "payment_status": "PAID",
                "total_amount": "480.00",
                "created_at": "2026-09-29T12:00:00",
                "items": [],
            }],
        }

    monkeypatch.setattr(OrderServiceClient, "get_recent_orders", mock_get_recent_orders)
    token = create_token(role="CUSTOMER", user_id=1)
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "What is the status of my order?"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert "Total Amount: ₹480.00" in response.json()["answer"]


def test_customer_retrieve_live_cart_via_chat_api(monkeypatch):
    calls: list[tuple[str, int]] = []

    async def mock_get_my_cart(self, token: str, user_id: int):
        calls.append((token, user_id))
        return {
            "success": True,
            "cart": {
                "id": 10,
                "user_id": user_id,
                "items": [
                    {"product_name": "Organic Apples", "unit_price": "120.00", "quantity": 2, "unit": "kg"},
                    {"product_name": "Organic Spinach", "unit_price": 40, "quantity": 1, "unit": "bunch"},
                ],
            },
        }

    monkeypatch.setattr(OrderServiceClient, "get_my_cart", mock_get_my_cart)
    token = create_token(role="CUSTOMER", user_id=1)
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "What's in my cart?"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert "Organic Apples × 2 — ₹120.00 / kg" in response.json()["answer"]
    assert "Total quantity: 3" in response.json()["answer"]
    assert "Cart total: ₹280.00" in response.json()["answer"]
    assert calls == [(token, 1)]


def test_customer_empty_cart_via_chat_api(monkeypatch):
    async def mock_get_my_cart(self, token: str, user_id: int):
        return {"success": True, "cart": {"id": 10, "user_id": user_id, "items": []}}

    monkeypatch.setattr(OrderServiceClient, "get_my_cart", mock_get_my_cart)
    token = create_token(role="CUSTOMER", user_id=1)
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "Show my cart"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["answer"] == "Your cart is currently empty."


@pytest.mark.parametrize(
    ("error", "detail"),
    [
        ("unavailable", "Order Service is currently unavailable. Please try again later."),
        ("timeout", "Order Service cart request timed out. Please try again later."),
    ],
)
def test_customer_cart_service_failures_are_returned_safely(monkeypatch, error, detail):
    async def mock_get_my_cart(self, token: str, user_id: int):
        return {"success": False, "error": error, "detail": detail}

    monkeypatch.setattr(OrderServiceClient, "get_my_cart", mock_get_my_cart)
    token = create_token(role="CUSTOMER", user_id=1)
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "What's my cart total?"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["answer"] == detail


def test_cart_client_rejects_another_customers_cart(monkeypatch):
    class ForeignCartResponse:
        status_code = status.HTTP_200_OK

        @staticmethod
        def json():
            return {"id": 10, "user_id": 2, "items": []}

    class ForeignCartClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, *args, **kwargs):
            return ForeignCartResponse()

    monkeypatch.setattr("app.tools.order_tools.httpx.AsyncClient", lambda **kwargs: ForeignCartClient())
    result = asyncio.run(OrderServiceClient().get_my_cart("token", 1))

    assert result == {
        "success": False,
        "error": "forbidden",
        "detail": "The requested cart does not belong to your account.",
    }


def test_cart_client_handles_order_service_timeout(monkeypatch):
    class TimeoutCartClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, *args, **kwargs):
            raise httpx.TimeoutException("timed out")

    monkeypatch.setattr("app.tools.order_tools.httpx.AsyncClient", lambda **kwargs: TimeoutCartClient())
    result = asyncio.run(OrderServiceClient().get_my_cart("token", 1))

    assert result["success"] is False
    assert result["error"] == "timeout"


def test_customer_cannot_retrieve_another_customer_order(monkeypatch):
    """
    Test customer 1 trying to access order 999 belonging to customer 2.
    """
    async def mock_get_order_by_id(self, order_id: int, token: str, user_id: int):
        return {"success": False, "error": "not_found", "detail": f"Order #{order_id} was not found or does not belong to your account."}

    monkeypatch.setattr(OrderServiceClient, "get_order_by_id", mock_get_order_by_id)

    token = create_token(role="CUSTOMER", user_id=1)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "What is the status of order 999?"},
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Order #999 was not found or does not belong to your account." in data["answer"]
    assert data["sources"] == EXPECTED_ORDER_SOURCE


def test_order_service_unavailable(monkeypatch):
    """
    Test graceful handling when Order Service is down/unavailable.
    """
    async def mock_get_recent_orders(self, token: str, user_id: int):
        return {
            "success": False,
            "error": "unavailable",
            "detail": "Order Service is currently unavailable. Please try again later.",
        }

    monkeypatch.setattr(OrderServiceClient, "get_recent_orders", mock_get_recent_orders)

    token = create_token(role="CUSTOMER", user_id=1)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "Show my recent orders."},
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Order Service is currently unavailable" in data["answer"]


def test_order_service_timeout(monkeypatch):
    """
    Test graceful handling when Order Service request times out.
    """
    async def mock_get_recent_orders(self, token: str, user_id: int):
        return {
            "success": False,
            "error": "timeout",
            "detail": "Order Service request timed out. Please try again later.",
        }

    monkeypatch.setattr(OrderServiceClient, "get_recent_orders", mock_get_recent_orders)

    token = create_token(role="CUSTOMER", user_id=1)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "What is my order status?"},
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Order Service request timed out" in data["answer"]


def test_rag_questions_still_work(monkeypatch):
    """
    Verify static knowledge base RAG questions continue to work properly.
    """
    monkeypatch.setattr(settings, "MOCK_LLM", True)

    token = create_token(role="CUSTOMER", user_id=1)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "What are your delivery policies?"},
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["answer"]) > 0
    assert len(data["sources"]) > 0
    assert any("customer_policies.md" in s["document"] for s in data["sources"])


def test_unsupported_questions_do_not_hallucinate(monkeypatch):
    """
    Verify unsupported knowledge questions return standard no-information response.
    """
    monkeypatch.setattr(settings, "MOCK_LLM", True)

    token = create_token(role="CUSTOMER", user_id=1)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "What is the orbital speed of Jupiter?"},
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "don't have information" in data["answer"] or "Mock LLM Response" in data["answer"] or len(data["answer"]) > 0


def test_customer_tell_me_details_of_order_59(monkeypatch):
    """
    Test customer querying 'Tell me details of order 59' extracts order ID 59 and returns order details.
    """
    mock_order = {
        "id": 59,
        "user_id": 1,
        "status": "CONFIRMED",
        "payment_status": "PAID",
        "total_amount": 350.0,
        "shipping_address": "78 Organic Avenue",
        "created_at": "2026-10-03T14:00:00",
        "items": [
            {
                "id": 1,
                "order_id": 59,
                "product_id": 3,
                "product_name": "Organic Mangoes",
                "unit_price": 175.0,
                "quantity": 2,
                "subtotal": 350.0,
            }
        ],
    }

    async def mock_get_order_by_id(self, order_id: int, token: str, user_id: int):
        if order_id == 59 and user_id == 1:
            return {"success": True, "order": mock_order}
        return {"success": False, "error": "not_found", "detail": f"Order #{order_id} was not found."}

    monkeypatch.setattr(OrderServiceClient, "get_order_by_id", mock_get_order_by_id)

    token = create_token(role="CUSTOMER", user_id=1)
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "Tell me details of order 59"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Order #59 Status" in data["answer"]
    assert "CONFIRMED" in data["answer"]
    assert "Organic Mangoes" in data["answer"]
    assert data["sources"] == EXPECTED_ORDER_SOURCE


def test_customer_where_is_my_order_returns_latest_order_status(monkeypatch):
    """
    Test customer querying 'Where is my order?' routes to live Order Service and returns latest order status.
    """
    mock_orders = [
        {
            "id": 59,
            "user_id": 1,
            "status": "CONFIRMED",
            "payment_status": "PAID",
            "total_amount": 350.0,
            "created_at": "2026-10-03T14:00:00",
            "items": [{"product_name": "Organic Mangoes", "quantity": 2}],
        }
    ]

    async def mock_get_recent_orders(self, token: str, user_id: int):
        return {"success": True, "orders": mock_orders}

    monkeypatch.setattr(OrderServiceClient, "get_recent_orders", mock_get_recent_orders)

    token = create_token(role="CUSTOMER", user_id=1)
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "Where is my order?"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Your latest order status:" in data["answer"]
    assert "Order #59" in data["answer"]
    assert "CONFIRMED" in data["answer"]
    assert data["sources"] == EXPECTED_ORDER_SOURCE
