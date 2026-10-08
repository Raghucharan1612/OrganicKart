"""Tests for Vendor/Farmer AI Assistant (Phase 4)."""

from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from jose import jwt

from app.config import settings
from app.main import app

# The module-level VendorAgent singleton used by the /vendor/chat endpoint.
from app.api.v1.vendor_chat import vendor_agent

client = TestClient(app)


def create_token(role: str = "VENDOR", user_id: int = 10) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_PRODUCTS = [
    {
        "id": 101,
        "seller_id": 10,
        "category_id": 1,
        "name": "Organic Tomatoes",
        "price": "60.00",
        "stock_quantity": 40,
        "unit": "kg",
        "certification": "APPROVED",
        "is_active": True,
    },
    {
        "id": 102,
        "seller_id": 10,
        "category_id": 1,
        "name": "Organic Spinach",
        "price": "30.00",
        "stock_quantity": 3,
        "unit": "bunch",
        "certification": "PENDING",
        "is_active": False,
    },
]


def _mock_get_my_products(products: list[dict[str, Any]]) -> AsyncMock:
    """Return an AsyncMock that simulates ProductServiceClient.get_my_products."""
    mock = AsyncMock(return_value={"success": True, "products": products})
    return mock


# ---------------------------------------------------------------------------
# RBAC: Role denial tests
# ---------------------------------------------------------------------------


def test_vendor_chat_unauthenticated_fails():
    response = client.post("/api/v1/ai/vendor/chat", json={"message": "Show my products"})
    assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


def test_vendor_chat_customer_role_denied():
    token = create_token(role="CUSTOMER", user_id=1)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/ai/vendor/chat", json={"message": "Show my products"}, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_vendor_chat_admin_role_denied():
    token = create_token(role="ADMIN", user_id=99)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/ai/vendor/chat", json={"message": "Show my products"}, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_vendor_chat_delivery_partner_role_denied():
    token = create_token(role="DELIVERY_PARTNER", user_id=88)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/ai/vendor/chat", json={"message": "Show my products"}, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# VENDOR access: my products
# ---------------------------------------------------------------------------


def test_vendor_my_products_success(monkeypatch):
    token = create_token(role="VENDOR", user_id=10)
    headers = {"Authorization": f"Bearer {token}"}

    mock = _mock_get_my_products(SAMPLE_PRODUCTS)
    monkeypatch.setattr(vendor_agent.product_client, "get_my_products", mock)

    response = client.post("/api/v1/ai/vendor/chat", json={"message": "Show my products"}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Organic Tomatoes" in data["answer"]
    assert "Stock: 40" in data["answer"]
    assert "Certification: APPROVED" in data["answer"]

    # Verify JWT was forwarded
    mock.assert_called_once()
    call_kwargs = mock.call_args
    assert call_kwargs.kwargs.get("token") == token or call_kwargs.args == () and call_kwargs.kwargs["token"] == token


# ---------------------------------------------------------------------------
# FARMER access
# ---------------------------------------------------------------------------


def test_farmer_role_access_success(monkeypatch):
    token = create_token(role="FARMER", user_id=20)
    headers = {"Authorization": f"Bearer {token}"}

    farmer_products = [
        {
            "id": 202,
            "seller_id": 20,
            "category_id": 2,
            "name": "Fresh Organic Carrots",
            "price": "50.00",
            "stock_quantity": 5,
            "unit": "kg",
            "certification": "PENDING",
            "is_active": True,
        }
    ]
    mock = _mock_get_my_products(farmer_products)
    monkeypatch.setattr(vendor_agent.product_client, "get_my_products", mock)

    response = client.post("/api/v1/ai/vendor/chat", json={"message": "Check my inventory stock"}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Fresh Organic Carrots: 5 kg" in data["answer"]


# ---------------------------------------------------------------------------
# Intent routing: low stock
# ---------------------------------------------------------------------------


def test_vendor_low_stock_routing(monkeypatch):
    token = create_token(role="VENDOR", user_id=10)
    headers = {"Authorization": f"Bearer {token}"}

    mock = _mock_get_my_products(SAMPLE_PRODUCTS)
    monkeypatch.setattr(vendor_agent.product_client, "get_my_products", mock)

    response = client.post(
        "/api/v1/ai/vendor/chat",
        json={"message": "Which products are low on stock?"},
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Only Organic Spinach (stock 3) qualifies as low stock
    assert "Organic Spinach (ID: 102): 3 bunch remaining" in data["answer"]
    # Organic Tomatoes (stock 40) should NOT appear
    assert "Organic Tomatoes" not in data["answer"]


# ---------------------------------------------------------------------------
# Intent routing: certification status
# ---------------------------------------------------------------------------


def test_vendor_certification_status_routing(monkeypatch):
    token = create_token(role="VENDOR", user_id=10)
    headers = {"Authorization": f"Bearer {token}"}

    mock = _mock_get_my_products(SAMPLE_PRODUCTS)
    monkeypatch.setattr(vendor_agent.product_client, "get_my_products", mock)

    response = client.post(
        "/api/v1/ai/vendor/chat",
        json={"message": "What is my product certification status?"},
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Organic Tomatoes: APPROVED (Active: Yes)" in data["answer"]
    assert "Organic Spinach: PENDING (Active: No)" in data["answer"]


# ---------------------------------------------------------------------------
# Ownership isolation: two vendors see only their own products
# ---------------------------------------------------------------------------


def test_vendor_ownership_isolation(monkeypatch):
    # Vendor A
    token_a = create_token(role="VENDOR", user_id=10)
    payload_a = [{"id": 1, "seller_id": 10, "name": "Vendor A Apples", "price": "100.00", "stock_quantity": 20, "unit": "kg", "certification": "APPROVED", "is_active": True}]

    mock_a = _mock_get_my_products(payload_a)
    monkeypatch.setattr(vendor_agent.product_client, "get_my_products", mock_a)

    res_a = client.post("/api/v1/ai/vendor/chat", json={"message": "Show my products"}, headers={"Authorization": f"Bearer {token_a}"})
    assert "Vendor A Apples" in res_a.json()["answer"]
    mock_a.assert_called_once_with(token=token_a)

    # Vendor B
    token_b = create_token(role="VENDOR", user_id=20)
    payload_b = [{"id": 2, "seller_id": 20, "name": "Vendor B Oranges", "price": "80.00", "stock_quantity": 15, "unit": "kg", "certification": "APPROVED", "is_active": True}]

    mock_b = _mock_get_my_products(payload_b)
    monkeypatch.setattr(vendor_agent.product_client, "get_my_products", mock_b)

    res_b = client.post("/api/v1/ai/vendor/chat", json={"message": "Show my products"}, headers={"Authorization": f"Bearer {token_b}"})
    assert "Vendor B Oranges" in res_b.json()["answer"]
    assert "Vendor A Apples" not in res_b.json()["answer"]
    mock_b.assert_called_once_with(token=token_b)


# ---------------------------------------------------------------------------
# Service failure: timeout
# ---------------------------------------------------------------------------


def test_product_service_timeout_handling(monkeypatch):
    token = create_token(role="VENDOR", user_id=10)
    headers = {"Authorization": f"Bearer {token}"}

    mock = AsyncMock(return_value={
        "success": False,
        "error": "timeout",
        "detail": "Product Service request timed out. Please try again later.",
    })
    monkeypatch.setattr(vendor_agent.product_client, "get_my_products", mock)

    response = client.post("/api/v1/ai/vendor/chat", json={"message": "Show my products"}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Product Service request timed out" in data["answer"]
    assert "Traceback" not in data["answer"]


# ---------------------------------------------------------------------------
# Service failure: unavailable
# ---------------------------------------------------------------------------


def test_product_service_unavailable_handling(monkeypatch):
    token = create_token(role="VENDOR", user_id=10)
    headers = {"Authorization": f"Bearer {token}"}

    mock = AsyncMock(return_value={
        "success": False,
        "error": "unavailable",
        "detail": "Product Service is currently unavailable. Please try again later.",
    })
    monkeypatch.setattr(vendor_agent.product_client, "get_my_products", mock)

    response = client.post("/api/v1/ai/vendor/chat", json={"message": "Show my products"}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Product Service is currently unavailable" in data["answer"]


# ---------------------------------------------------------------------------
# Empty catalog
# ---------------------------------------------------------------------------


def test_vendor_empty_catalog(monkeypatch):
    token = create_token(role="VENDOR", user_id=10)
    headers = {"Authorization": f"Bearer {token}"}

    mock = _mock_get_my_products([])
    monkeypatch.setattr(vendor_agent.product_client, "get_my_products", mock)

    response = client.post("/api/v1/ai/vendor/chat", json={"message": "Show my products"}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "do not have any products" in data["answer"]


# ---------------------------------------------------------------------------
# All stock sufficient
# ---------------------------------------------------------------------------


def test_vendor_no_low_stock(monkeypatch):
    token = create_token(role="VENDOR", user_id=10)
    headers = {"Authorization": f"Bearer {token}"}

    high_stock = [{"id": 1, "seller_id": 10, "name": "Apples", "price": "100", "stock_quantity": 50, "unit": "kg", "certification": "APPROVED", "is_active": True}]
    mock = _mock_get_my_products(high_stock)
    monkeypatch.setattr(vendor_agent.product_client, "get_my_products", mock)

    response = client.post("/api/v1/ai/vendor/chat", json={"message": "Any low stock items?"}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "sufficient stock" in data["answer"]


# ---------------------------------------------------------------------------
# Routing: customer assistant endpoint still rejects VENDOR
# ---------------------------------------------------------------------------


def test_customer_chat_rejects_vendor():
    token = create_token(role="VENDOR", user_id=10)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/ai/chat", json={"message": "What organic products?"}, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
