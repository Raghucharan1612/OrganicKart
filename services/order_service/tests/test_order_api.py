import pytest
import json
import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token
from app.core.config import settings
from app.database.base import Base
from app.database.session import get_db
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.payment import PaymentAttempt
from app.services.order_service import OrderService
from app.services.razorpay_service import RazorpayService
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class FakeRazorpay:
    key_id = "rzp_test_public"
    last_order_id = ""
    payment_order_id = ""
    payment_amount = 3000
    payment_status = "captured"
    last_webhook_body = None

    def __init__(self):
        pass

    def create_order(self, amount_paise, currency, receipt):
        type(self).last_order_id = f"order_{receipt}"
        type(self).payment_amount = amount_paise
        return {"id": type(self).last_order_id, "amount": amount_paise, "currency": currency}

    def verify_payment_signature(self, order_id, payment_id, signature):
        if signature != "valid-signature":
            raise HTTPException(status_code=400, detail="Invalid Razorpay payment signature")

    def fetch_payment(self, payment_id):
        return {"id": payment_id, "order_id": type(self).payment_order_id or type(self).last_order_id, "amount": type(self).payment_amount, "currency": "INR", "status": type(self).payment_status}

    @staticmethod
    def verify_webhook_signature(body, signature):
        FakeRazorpay.last_webhook_body = body
        if signature != "valid-webhook":
            raise HTTPException(status_code=400, detail="Invalid Razorpay webhook signature")


@pytest.fixture(autouse=True)
def db_session(monkeypatch):
    monkeypatch.setattr(settings, "RAZORPAY_KEY_ID", "rzp_test_public")
    monkeypatch.setattr(settings, "RAZORPAY_KEY_SECRET", "test-secret")
    monkeypatch.setattr(settings, "RAZORPAY_WEBHOOK_SECRET", "webhook-secret")
    monkeypatch.setattr("app.services.order_service.RazorpayService", FakeRazorpay)
    monkeypatch.setattr("app.api.v1.orders.RazorpayService", FakeRazorpay)
    def fake_get(url, timeout=10, headers=None):
        class Response:
            status_code = 200

            def json(self):
                if "/users/me/addresses" in url:
                    return [{"id": 1, "user_id": 1, "recipient_name": "Test Customer", "phone": "9999999999", "address_line1": "1 Main Street", "address_line2": None, "city": "Bengaluru", "state": "Karnataka", "postal_code": "560001", "country": "India"}]
                product_id = int(url.rstrip("/").split("/")[-1])
                return {"id": product_id, "name": f"Product {product_id}", "price": "15.00", "certification": "APPROVED", "is_active": True, "stock_quantity": 25}

        return Response()

    monkeypatch.setattr("app.services.cart_service.httpx.get", fake_get)
    monkeypatch.setattr("app.services.order_service.httpx.get", fake_get)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def get_auth_headers(user_id: int = 1, role: str = "CUSTOMER") -> dict:
    token = create_access_token(str(user_id), extra_claims={"role": role})
    return {"Authorization": f"Bearer {token}"}


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_unauthenticated_cart_access_is_rejected():
    response = client.get("/api/v1/cart")
    assert response.status_code == 403


def test_only_customers_can_access_cart_operations():
    assert client.get("/api/v1/cart", headers=get_auth_headers(role="CUSTOMER")).status_code == 200
    for role in ("VENDOR", "FARMER", "ADMIN", "SUPER_ADMIN", "DELIVERY_PARTNER"):
        response = client.get("/api/v1/cart", headers=get_auth_headers(role=role))
        assert response.status_code == 403, f"{role} unexpectedly accessed the cart: {response.text}"


def test_only_customers_can_create_orders():
    for role in ("VENDOR", "FARMER", "ADMIN", "SUPER_ADMIN", "DELIVERY_PARTNER"):
        response = client.post(
            "/api/v1/orders",
            json={"shipping_address": "123 Market St"},
            headers=get_auth_headers(role=role),
        )
        assert response.status_code == 403, f"{role} unexpectedly created an order: {response.text}"


def test_add_item_to_cart():
    response = client.post("/api/v1/cart/items", json={"product_id": 15, "quantity": 2}, headers=get_auth_headers())
    assert response.status_code == 201
    payload = response.json()
    assert payload["product_id"] == 15
    assert payload["quantity"] == 2


def test_pending_products_cannot_be_added_to_cart(monkeypatch):
    def pending_product_response(url, timeout):
        class Response:
            status_code = 200

            def json(self):
                product_id = int(url.rstrip("/").split("/")[-1])
                return {"id": product_id, "name": f"Product {product_id}", "price": "15.00", "certification": "PENDING", "is_active": True, "stock_quantity": 10}

        return Response()

    monkeypatch.setattr("app.services.cart_service.httpx.get", pending_product_response)
    response = client.post("/api/v1/cart/items", json={"product_id": 99, "quantity": 1}, headers=get_auth_headers())
    assert response.status_code == 400
    assert "certification" in response.json()["detail"].lower()


def test_update_cart_item_quantity():
    created = client.post("/api/v1/cart/items", json={"product_id": 21, "quantity": 1}, headers=get_auth_headers())
    item_id = created.json()["id"]

    updated = client.put(f"/api/v1/cart/items/{item_id}", json={"quantity": 4}, headers=get_auth_headers())
    assert updated.status_code == 200
    assert updated.json()["quantity"] == 4


def test_remove_item_from_cart():
    created = client.post("/api/v1/cart/items", json={"product_id": 22, "quantity": 1}, headers=get_auth_headers())
    item_id = created.json()["id"]

    response = client.delete(f"/api/v1/cart/items/{item_id}", headers=get_auth_headers())
    assert response.status_code == 204


def test_clear_cart():
    client.post("/api/v1/cart/items", json={"product_id": 23, "quantity": 1}, headers=get_auth_headers())
    response = client.delete("/api/v1/cart", headers=get_auth_headers())
    assert response.status_code == 204


def test_invalid_quantity_rejected():
    response = client.post("/api/v1/cart/items", json={"product_id": 1, "quantity": 0}, headers=get_auth_headers())
    assert response.status_code == 422


def _initiate_checkout(user_id: int = 1, address_id: int = 1) -> dict:
    client.post("/api/v1/cart/items", json={"product_id": 30, "quantity": 2}, headers=get_auth_headers(user_id))
    response = client.post("/api/v1/orders/checkout/initiate", json={"address_id": address_id}, headers=get_auth_headers(user_id))
    assert response.status_code == 201, response.text
    return response.json()


def test_checkout_initiation_creates_pending_order_and_keeps_cart():
    client.post("/api/v1/cart/items", json={"product_id": 30, "quantity": 2}, headers=get_auth_headers())
    response = client.post(
        "/api/v1/orders/checkout/initiate",
        json={"address_id": 1, "total": "0.01", "amount_paise": 1},
        headers=get_auth_headers(),
    )
    assert response.status_code == 201
    initiated = response.json()
    assert initiated["payment_status"] == "PAYMENT_PENDING"
    assert initiated["amount_paise"] == 3000
    assert initiated["currency"] == "INR"
    assert client.get("/api/v1/cart", headers=get_auth_headers()).json()["items"]

    db = TestingSessionLocal()
    try:
        order = db.get(Order, initiated["order_id"])
        payment = db.get(PaymentAttempt, initiated["payment_attempt_id"])
        assert order.status == "PAYMENT_PENDING"
        assert order.payment_status == "PAYMENT_PENDING"
        assert payment.amount_paise == 3000
    finally:
        db.close()


def test_checkout_does_not_trigger_fulfilment(monkeypatch):
    calls = []
    monkeypatch.setattr("app.services.order_service.httpx.post", lambda *args, **kwargs: calls.append(args[0]))
    _initiate_checkout()
    assert calls == []


def test_non_customer_cannot_initiate_checkout():
    response = client.post("/api/v1/orders/checkout/initiate", json={"address_id": 1}, headers=get_auth_headers(role="VENDOR"))
    assert response.status_code == 403


def test_checkout_rejects_another_customers_address(monkeypatch):
    class Response:
        status_code = 200

        def json(self):
            return [{"id": 2, "user_id": 2, "recipient_name": "Other", "phone": "9999999999", "address_line1": "Other St", "city": "Delhi", "state": "Delhi", "postal_code": "110001", "country": "India"}]

    original_get = OrderService._validate_product
    monkeypatch.setattr("app.services.order_service.OrderService._validate_product", original_get)
    monkeypatch.setattr("app.services.order_service.httpx.get", lambda url, **kwargs: Response() if "addresses" in url else type("ProductResponse", (), {"status_code": 200, "json": lambda self: {"id": 30, "name": "Product 30", "price": "15.00", "certification": "APPROVED", "is_active": True, "stock_quantity": 25}})())
    client.post("/api/v1/cart/items", json={"product_id": 30, "quantity": 1}, headers=get_auth_headers())
    assert client.post("/api/v1/orders/checkout/initiate", json={"address_id": 2}, headers=get_auth_headers()).status_code == 404


def test_old_order_endpoint_cannot_bypass_payment():
    response = client.post("/api/v1/orders", json={"shipping_address": "123 Market St"}, headers=get_auth_headers())
    assert response.status_code == 409


def test_successful_confirmation_is_idempotent_and_triggers_fulfilment_once(monkeypatch):
    initiated = _initiate_checkout()
    calls = []

    class Response:
        def raise_for_status(self):
            return None

    monkeypatch.setattr("app.services.order_service.httpx.post", lambda url, **kwargs: calls.append(url) or Response())
    db = TestingSessionLocal()
    try:
        service = OrderService(db)
        order, payment = service.confirm_payment(initiated["payment_attempt_id"], 1, initiated["amount_paise"])
        duplicate_order, duplicate_payment = service.confirm_payment(initiated["payment_attempt_id"], 1, initiated["amount_paise"])
        assert order.status == "CONFIRMED"
        assert order.payment_status == "PAID"
        assert payment.status == "PAID"
        assert duplicate_order.id == order.id
        assert duplicate_payment.id == payment.id
        assert db.query(CartItem).count() == 0
    finally:
        db.close()
    assert len(calls) == 2
    assert any("deliveries/internal/assign" in url for url in calls)
    assert any("notifications" in url for url in calls)


def test_failed_payment_does_not_fulfil_order():
    initiated = _initiate_checkout()
    db = TestingSessionLocal()
    try:
        payment = OrderService(db).mark_payment_failed(initiated["payment_attempt_id"], 1, "declined")
        assert payment.status == "FAILED"
        assert db.get(Order, initiated["order_id"]).status == "PAYMENT_PENDING"
        assert db.query(CartItem).count() == 1
    finally:
        db.close()


def test_payment_status_is_limited_to_order_owner():
    initiated = _initiate_checkout()
    own = client.get(f"/api/v1/orders/{initiated['order_id']}/payment-status", headers=get_auth_headers())
    other = client.get(f"/api/v1/orders/{initiated['order_id']}/payment-status", headers=get_auth_headers(user_id=2))
    assert own.status_code == 200
    assert own.json()["status"] == "PAYMENT_PENDING"
    assert other.status_code == 404


def test_checkout_creates_and_returns_safe_razorpay_order():
    initiated = _initiate_checkout()
    assert initiated["razorpay_key_id"] == "rzp_test_public"
    assert initiated["razorpay_order_id"].startswith("order_ok-")
    assert initiated["amount_paise"] == 3000
    assert "secret" not in initiated

    db = TestingSessionLocal()
    try:
        payment = db.get(PaymentAttempt, initiated["payment_attempt_id"])
        assert payment.provider_order_id == initiated["razorpay_order_id"]
    finally:
        db.close()


def test_checkout_idempotency_key_reuses_local_and_razorpay_order():
    client.post("/api/v1/cart/items", json={"product_id": 30, "quantity": 2}, headers=get_auth_headers())
    headers = {**get_auth_headers(), "Idempotency-Key": "checkout-attempt-1"}
    first = client.post("/api/v1/orders/checkout/initiate", json={"address_id": 1}, headers=headers)
    second = client.post("/api/v1/orders/checkout/initiate", json={"address_id": 1}, headers=headers)
    assert first.status_code == second.status_code == 201
    assert first.json()["order_id"] == second.json()["order_id"]
    assert first.json()["razorpay_order_id"] == second.json()["razorpay_order_id"]


def test_payment_verify_rejects_invalid_signature_without_fulfilment():
    initiated = _initiate_checkout()
    response = client.post("/api/v1/orders/payments/verify", json={
        "order_id": initiated["order_id"],
        "razorpay_order_id": initiated["razorpay_order_id"],
        "razorpay_payment_id": "pay_invalid",
        "razorpay_signature": "bad-signature",
    }, headers=get_auth_headers())
    assert response.status_code == 400
    assert client.get("/api/v1/cart", headers=get_auth_headers()).json()["items"]
    assert client.get(f"/api/v1/orders/{initiated['order_id']}/payment-status", headers=get_auth_headers()).json()["status"] == "PAYMENT_PENDING"


def test_payment_verify_requires_customer_and_order_ownership():
    initiated = _initiate_checkout()
    payload = {
        "order_id": initiated["order_id"], "razorpay_order_id": initiated["razorpay_order_id"],
        "razorpay_payment_id": "pay_1", "razorpay_signature": "valid-signature",
    }
    assert client.post("/api/v1/orders/payments/verify", json=payload, headers=get_auth_headers(role="VENDOR")).status_code == 403
    assert client.post("/api/v1/orders/payments/verify", json=payload, headers=get_auth_headers(user_id=2)).status_code == 404
    payload["razorpay_order_id"] = "order_wrong"
    assert client.post("/api/v1/orders/payments/verify", json=payload, headers=get_auth_headers()).status_code == 400


def test_valid_payment_verify_confirms_once_and_payment_id_cannot_be_reused(monkeypatch):
    first = _initiate_checkout()
    FakeRazorpay.payment_order_id = first["razorpay_order_id"]
    calls = []

    class Response:
        def raise_for_status(self):
            return None

    monkeypatch.setattr("app.services.order_service.httpx.post", lambda url, **kwargs: calls.append(url) or Response())
    payload = {
        "order_id": first["order_id"], "razorpay_order_id": first["razorpay_order_id"],
        "razorpay_payment_id": "pay_shared", "razorpay_signature": "valid-signature",
    }
    assert client.post("/api/v1/orders/payments/verify", json=payload, headers=get_auth_headers()).json()["payment_status"] == "PAID"
    assert client.post("/api/v1/orders/payments/verify", json=payload, headers=get_auth_headers()).json()["payment_status"] == "PAID"
    assert len(calls) == 2

    second = _initiate_checkout()
    payload.update({"order_id": second["order_id"], "razorpay_order_id": second["razorpay_order_id"]})
    assert client.post("/api/v1/orders/payments/verify", json=payload, headers=get_auth_headers()).status_code == 409


def test_webhook_validates_raw_body_and_is_idempotent(monkeypatch):
    initiated = _initiate_checkout()
    FakeRazorpay.payment_order_id = initiated["razorpay_order_id"]
    calls = []

    class Response:
        def raise_for_status(self):
            return None

    monkeypatch.setattr("app.services.order_service.httpx.post", lambda url, **kwargs: calls.append(url) or Response())
    event = {"event": "payment.captured", "payload": {"payment": {"entity": {"id": "pay_webhook", "order_id": initiated["razorpay_order_id"]}}}}
    body = json.dumps(event, separators=(",", ":")).encode()
    invalid = client.post("/api/v1/orders/payments/webhook", content=body, headers={"X-Razorpay-Signature": "invalid"})
    assert invalid.status_code == 400
    assert client.get("/api/v1/cart", headers=get_auth_headers()).json()["items"]
    first = client.post("/api/v1/orders/payments/webhook", content=body, headers={"X-Razorpay-Signature": "valid-webhook"})
    second = client.post("/api/v1/orders/payments/webhook", content=body, headers={"X-Razorpay-Signature": "valid-webhook"})
    assert first.status_code == second.status_code == 200
    assert first.json()["payment_status"] == "PAID"
    assert FakeRazorpay.last_webhook_body == body
    assert len(calls) == 2


def test_webhook_order_paid_and_irrelevant_events_do_not_double_fulfil(monkeypatch):
    initiated = _initiate_checkout()
    ignored = client.post("/api/v1/orders/payments/webhook", content=json.dumps({"event": "payment.failed"}).encode(), headers={"X-Razorpay-Signature": "valid-webhook"})
    assert ignored.json() == {"status": "ignored"}
    FakeRazorpay.payment_order_id = initiated["razorpay_order_id"]
    monkeypatch.setattr("app.services.order_service.httpx.post", lambda *args, **kwargs: type("Response", (), {"raise_for_status": lambda self: None})())
    event = {"event": "order.paid", "payload": {"payment": {"entity": {"id": "pay_order_paid", "order_id": initiated["razorpay_order_id"]}}}}
    response = client.post("/api/v1/orders/payments/webhook", content=json.dumps(event).encode(), headers={"X-Razorpay-Signature": "valid-webhook"})
    assert response.status_code == 200


def test_razorpay_webhook_signature_uses_unmodified_raw_body():
    body = b'{"event":"payment.captured", "spacing":"must remain"}'
    signature = hmac.new(b"webhook-secret", body, hashlib.sha256).hexdigest()
    RazorpayService.verify_webhook_signature(body, signature)
    with pytest.raises(HTTPException):
        RazorpayService.verify_webhook_signature(body + b" ", signature)


def test_checkout_captures_seller_id_from_product_service(monkeypatch):
    def custom_product_get(url, **kwargs):
        class Response:
            status_code = 200

            def json(self):
                if "addresses" in url:
                    return [{"id": 1, "user_id": 1, "recipient_name": "Test Customer", "phone": "9999999999", "address_line1": "1 Main St", "city": "Bengaluru", "state": "Karnataka", "postal_code": "560001", "country": "India"}]
                return {"id": 10, "name": "Organic Apples", "price": "50.00", "certification": "APPROVED", "is_active": True, "stock_quantity": 50, "seller_id": 42}

        return Response()

    monkeypatch.setattr("app.services.cart_service.httpx.get", custom_product_get)
    monkeypatch.setattr("app.services.order_service.httpx.get", custom_product_get)

    client.post("/api/v1/cart/items", json={"product_id": 10, "quantity": 2}, headers=get_auth_headers())
    res = client.post("/api/v1/orders/checkout/initiate", json={"address_id": 1}, headers=get_auth_headers())
    assert res.status_code == 201
    order_id = res.json()["order_id"]

    db = TestingSessionLocal()
    try:
        order = db.get(Order, order_id)
        assert len(order.items) == 1
        assert order.items[0].seller_id == 42
    finally:
        db.close()


def test_checkout_captures_same_seller_id_for_multiple_items_from_same_seller(monkeypatch):
    def custom_product_get(url, **kwargs):
        class Response:
            status_code = 200

            def json(self):
                if "addresses" in url:
                    return [{"id": 1, "user_id": 1, "recipient_name": "Test Customer", "phone": "9999999999", "address_line1": "1 Main St", "city": "Bengaluru", "state": "Karnataka", "postal_code": "560001", "country": "India"}]
                product_id = int(url.rstrip("/").split("/")[-1])
                return {"id": product_id, "name": f"Product {product_id}", "price": "20.00", "certification": "APPROVED", "is_active": True, "stock_quantity": 50, "seller_id": 99}

        return Response()

    monkeypatch.setattr("app.services.cart_service.httpx.get", custom_product_get)
    monkeypatch.setattr("app.services.order_service.httpx.get", custom_product_get)

    client.post("/api/v1/cart/items", json={"product_id": 1, "quantity": 1}, headers=get_auth_headers())
    client.post("/api/v1/cart/items", json={"product_id": 2, "quantity": 1}, headers=get_auth_headers())
    res = client.post("/api/v1/orders/checkout/initiate", json={"address_id": 1}, headers=get_auth_headers())
    assert res.status_code == 201

    db = TestingSessionLocal()
    try:
        order = db.get(Order, res.json()["order_id"])
        assert len(order.items) == 2
        assert all(item.seller_id == 99 for item in order.items)
    finally:
        db.close()


def test_checkout_captures_different_seller_ids_for_items_from_different_sellers(monkeypatch):
    def custom_product_get(url, **kwargs):
        class Response:
            status_code = 200

            def json(self):
                if "addresses" in url:
                    return [{"id": 1, "user_id": 1, "recipient_name": "Test Customer", "phone": "9999999999", "address_line1": "1 Main St", "city": "Bengaluru", "state": "Karnataka", "postal_code": "560001", "country": "India"}]
                product_id = int(url.rstrip("/").split("/")[-1])
                seller_map = {101: 5, 102: 12}
                return {"id": product_id, "name": f"Product {product_id}", "price": "25.00", "certification": "APPROVED", "is_active": True, "stock_quantity": 50, "seller_id": seller_map.get(product_id, 1)}

        return Response()

    monkeypatch.setattr("app.services.cart_service.httpx.get", custom_product_get)
    monkeypatch.setattr("app.services.order_service.httpx.get", custom_product_get)

    client.post("/api/v1/cart/items", json={"product_id": 101, "quantity": 1}, headers=get_auth_headers())
    client.post("/api/v1/cart/items", json={"product_id": 102, "quantity": 1}, headers=get_auth_headers())
    res = client.post("/api/v1/orders/checkout/initiate", json={"address_id": 1}, headers=get_auth_headers())
    assert res.status_code == 201

    db = TestingSessionLocal()
    try:
        order = db.get(Order, res.json()["order_id"])
        assert len(order.items) == 2
        item_sellers = {item.product_id: item.seller_id for item in order.items}
        assert item_sellers[101] == 5
        assert item_sellers[102] == 12
    finally:
        db.close()


def test_checkout_handles_product_without_seller_id_gracefully(monkeypatch):
    def custom_product_get(url, **kwargs):
        class Response:
            status_code = 200

            def json(self):
                if "addresses" in url:
                    return [{"id": 1, "user_id": 1, "recipient_name": "Test Customer", "phone": "9999999999", "address_line1": "1 Main St", "city": "Bengaluru", "state": "Karnataka", "postal_code": "560001", "country": "India"}]
                return {"id": 200, "name": "Legacy Product", "price": "10.00", "certification": "APPROVED", "is_active": True, "stock_quantity": 50}

        return Response()

    monkeypatch.setattr("app.services.cart_service.httpx.get", custom_product_get)
    monkeypatch.setattr("app.services.order_service.httpx.get", custom_product_get)

    client.post("/api/v1/cart/items", json={"product_id": 200, "quantity": 1}, headers=get_auth_headers())
    res = client.post("/api/v1/orders/checkout/initiate", json={"address_id": 1}, headers=get_auth_headers())
    assert res.status_code == 201

    db = TestingSessionLocal()
    try:
        order = db.get(Order, res.json()["order_id"])
        assert len(order.items) == 1
        assert order.items[0].seller_id is None
    finally:
        db.close()


def test_checkout_customer_cannot_inject_seller_id(monkeypatch):
    def custom_product_get(url, **kwargs):
        class Response:
            status_code = 200

            def json(self):
                if "addresses" in url:
                    return [{"id": 1, "user_id": 1, "recipient_name": "Test Customer", "phone": "9999999999", "address_line1": "1 Main St", "city": "Bengaluru", "state": "Karnataka", "postal_code": "560001", "country": "India"}]
                return {"id": 300, "name": "Organic Honey", "price": "100.00", "certification": "APPROVED", "is_active": True, "stock_quantity": 50, "seller_id": 77}

        return Response()

    monkeypatch.setattr("app.services.cart_service.httpx.get", custom_product_get)
    monkeypatch.setattr("app.services.order_service.httpx.get", custom_product_get)

    client.post("/api/v1/cart/items", json={"product_id": 300, "quantity": 1}, headers=get_auth_headers())
    res = client.post("/api/v1/orders/checkout/initiate", json={"address_id": 1, "seller_id": 9999}, headers=get_auth_headers())
    assert res.status_code == 201

    db = TestingSessionLocal()
    try:
        order = db.get(Order, res.json()["order_id"])
        assert len(order.items) == 1
        assert order.items[0].seller_id == 77
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Step 8: Seller Orders API tests
# ---------------------------------------------------------------------------

def _create_order_with_seller_items(monkeypatch, customer_user_id: int, items: list[dict]) -> int:
    """Helper: place a checkout order for a customer whose cart has the given items.

    Each entry in `items` is {"product_id": int, "seller_id": int|None, "price": str}.
    Returns the created order_id.
    """
    seller_map = {item["product_id"]: item for item in items}

    def custom_get(url, **kwargs):
        class Resp:
            status_code = 200
            def json(self_inner):
                if "addresses" in url:
                    return [{
                        "id": 1, "user_id": customer_user_id,
                        "recipient_name": "Buyer", "phone": "9000000000",
                        "address_line1": "10 Farm Rd", "city": "Pune",
                        "state": "Maharashtra", "postal_code": "411001",
                        "country": "India",
                    }]
                pid = int(url.rstrip("/").split("/")[-1])
                meta = seller_map.get(pid, {"product_id": pid, "seller_id": None, "price": "10.00"})
                out = {
                    "id": pid,
                    "name": f"Product {pid}",
                    "price": meta.get("price", "10.00"),
                    "certification": "APPROVED",
                    "is_active": True,
                    "stock_quantity": 50,
                }
                if meta.get("seller_id") is not None:
                    out["seller_id"] = meta["seller_id"]
                return out
        return Resp()

    monkeypatch.setattr("app.services.cart_service.httpx.get", custom_get)
    monkeypatch.setattr("app.services.order_service.httpx.get", custom_get)

    headers = get_auth_headers(user_id=customer_user_id, role="CUSTOMER")
    for item in items:
        client.post("/api/v1/cart/items", json={"product_id": item["product_id"], "quantity": 1}, headers=headers)

    res = client.post("/api/v1/orders/checkout/initiate", json={"address_id": 1}, headers=headers)
    assert res.status_code == 201, f"Checkout failed: {res.text}"
    return res.json()["order_id"]


def test_vendor_can_access_seller_orders_endpoint():
    """A. VENDOR JWT can call GET /api/v1/orders/seller and get 200."""
    res = client.get("/api/v1/orders/seller", headers=get_auth_headers(user_id=10, role="VENDOR"))
    assert res.status_code == 200


def test_farmer_can_access_seller_orders_endpoint():
    """B. FARMER JWT can call GET /api/v1/orders/seller and get 200."""
    res = client.get("/api/v1/orders/seller", headers=get_auth_headers(user_id=20, role="FARMER"))
    assert res.status_code == 200


def test_customer_cannot_access_seller_orders_endpoint():
    """C. CUSTOMER JWT receives 403 from GET /api/v1/orders/seller."""
    res = client.get("/api/v1/orders/seller", headers=get_auth_headers(user_id=1, role="CUSTOMER"))
    assert res.status_code == 403


def test_unauthenticated_seller_orders_request_is_rejected():
    """D. No token → 401 (HTTPBearer returns 403 when header is absent)."""
    res = client.get("/api/v1/orders/seller")
    assert res.status_code in {401, 403}


def test_seller_receives_only_own_order_items(monkeypatch):
    """E. Seller 42 sees only items with seller_id=42."""
    _create_order_with_seller_items(
        monkeypatch,
        customer_user_id=1,
        items=[{"product_id": 10, "seller_id": 42, "price": "20.00"}],
    )

    res = client.get("/api/v1/orders/seller", headers=get_auth_headers(user_id=42, role="VENDOR"))
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert all(it["seller_id"] == 42 for order in data for it in order["items"])


def test_mixed_seller_order_isolation(monkeypatch):
    """F. Order with items from seller 10 and seller 20 — each sees only their own item."""
    _create_order_with_seller_items(
        monkeypatch,
        customer_user_id=2,
        items=[
            {"product_id": 101, "seller_id": 10, "price": "30.00"},
            {"product_id": 102, "seller_id": 20, "price": "50.00"},
        ],
    )

    # Seller 10
    res10 = client.get("/api/v1/orders/seller", headers=get_auth_headers(user_id=10, role="VENDOR"))
    assert res10.status_code == 200
    orders10 = res10.json()
    assert len(orders10) == 1
    items10 = orders10[0]["items"]
    assert len(items10) == 1
    assert items10[0]["product_id"] == 101
    assert items10[0]["seller_id"] == 10

    # Seller 20
    res20 = client.get("/api/v1/orders/seller", headers=get_auth_headers(user_id=20, role="VENDOR"))
    assert res20.status_code == 200
    orders20 = res20.json()
    assert len(orders20) == 1
    items20 = orders20[0]["items"]
    assert len(items20) == 1
    assert items20[0]["product_id"] == 102
    assert items20[0]["seller_id"] == 20


def test_seller_cannot_override_identity_via_query_param(monkeypatch):
    """G. seller_id query param is ignored; endpoint always uses JWT sub."""
    _create_order_with_seller_items(
        monkeypatch,
        customer_user_id=3,
        items=[{"product_id": 200, "seller_id": 55, "price": "15.00"}],
    )

    # Seller 99 tries to pass seller_id=55 as a query param
    res = client.get(
        "/api/v1/orders/seller?seller_id=55",
        headers=get_auth_headers(user_id=99, role="VENDOR"),
    )
    assert res.status_code == 200
    # Seller 99 has no items, so must get an empty list (not seller 55's data)
    assert res.json() == []


# ---------------------------------------------------------------------------
# Step 9: Seller Analytics API tests
# ---------------------------------------------------------------------------

def test_vendor_can_access_seller_analytics_endpoint():
    """A. VENDOR JWT can call GET /api/v1/orders/seller/analytics and get 200."""
    res = client.get("/api/v1/orders/seller/analytics", headers=get_auth_headers(user_id=10, role="VENDOR"))
    assert res.status_code == 200
    data = res.json()
    assert data["total_orders"] == 0
    assert float(data["total_revenue"]) == 0.0


def test_farmer_can_access_seller_analytics_endpoint():
    """B. FARMER JWT can call GET /api/v1/orders/seller/analytics and get 200."""
    res = client.get("/api/v1/orders/seller/analytics", headers=get_auth_headers(user_id=20, role="FARMER"))
    assert res.status_code == 200
    data = res.json()
    assert data["total_orders"] == 0
    assert float(data["total_revenue"]) == 0.0


def test_customer_cannot_access_seller_analytics_endpoint():
    """C. CUSTOMER JWT receives 403 from GET /api/v1/orders/seller/analytics."""
    res = client.get("/api/v1/orders/seller/analytics", headers=get_auth_headers(user_id=1, role="CUSTOMER"))
    assert res.status_code == 403


def test_unauthenticated_seller_analytics_request_is_rejected():
    """D. No token → 401 or 403 from HTTPBearer."""
    res = client.get("/api/v1/orders/seller/analytics")
    assert res.status_code in {401, 403}


def test_seller_analytics_revenue_calculation_and_isolation(monkeypatch):
    """E. Seller analytics calculates total orders, total revenue, monthly summary, and recent orders."""
    _create_order_with_seller_items(
        monkeypatch,
        customer_user_id=1,
        items=[
            {"product_id": 10, "seller_id": 42, "price": "20.00"},
            {"product_id": 11, "seller_id": 42, "price": "30.00"},
        ],
    )

    res = client.get("/api/v1/orders/seller/analytics", headers=get_auth_headers(user_id=42, role="VENDOR"))
    assert res.status_code == 200
    data = res.json()
    assert data["total_orders"] == 1
    assert float(data["total_revenue"]) == 50.0
    assert len(data["monthly_sales_summary"]) == 1
    assert data["monthly_sales_summary"][0]["orders"] == 1
    assert float(data["monthly_sales_summary"][0]["revenue"]) == 50.0
    assert len(data["recent_order_summary"]) == 1
    assert data["recent_order_summary"][0]["items_count"] == 2
    assert float(data["recent_order_summary"][0]["seller_revenue"]) == 50.0


def test_mixed_seller_order_revenue_calculation(monkeypatch):
    """F. Mixed-seller order: revenue is calculated ONLY from that seller's OrderItem subtotal, never full order total."""
    # Order 1: Seller 10 item ($30.00) + Seller 20 item ($50.00). Total Order Amount = $80.00
    _create_order_with_seller_items(
        monkeypatch,
        customer_user_id=1,
        items=[
            {"product_id": 101, "seller_id": 10, "price": "30.00"},
            {"product_id": 102, "seller_id": 20, "price": "50.00"},
        ],
    )
    # Order 2: Seller 10 item ($25.00)
    _create_order_with_seller_items(
        monkeypatch,
        customer_user_id=2,
        items=[
            {"product_id": 103, "seller_id": 10, "price": "25.00"},
        ],
    )

    # Seller 10 Analytics
    res10 = client.get("/api/v1/orders/seller/analytics", headers=get_auth_headers(user_id=10, role="VENDOR"))
    assert res10.status_code == 200
    data10 = res10.json()
    assert data10["total_orders"] == 2
    # Revenue should be 30.00 + 25.00 = 55.00 (NOT 80.00 + 25.00 = 105.00)
    assert float(data10["total_revenue"]) == 55.0

    # Seller 20 Analytics
    res20 = client.get("/api/v1/orders/seller/analytics", headers=get_auth_headers(user_id=20, role="FARMER"))
    assert res20.status_code == 200
    data20 = res20.json()
    assert data20["total_orders"] == 1
    # Revenue should be 50.00 (NOT full order total of 80.00)
    assert float(data20["total_revenue"]) == 50.0


def test_seller_analytics_prevents_seller_id_query_manipulation(monkeypatch):
    """G. Query/body seller_id is ignored; endpoint uses JWT sub."""
    _create_order_with_seller_items(
        monkeypatch,
        customer_user_id=3,
        items=[{"product_id": 200, "seller_id": 55, "price": "100.00"}],
    )

    # Seller 99 attempts to query analytics for seller_id=55 via query string
    res = client.get(
        "/api/v1/orders/seller/analytics?seller_id=55",
        headers=get_auth_headers(user_id=99, role="VENDOR"),
    )
    assert res.status_code == 200
    data = res.json()
    # Seller 99 has no orders
    assert data["total_orders"] == 0
    assert float(data["total_revenue"]) == 0.0


def test_admin_order_analytics_uses_whole_paid_orders_without_customer_pii():
    db = TestingSessionLocal()
    try:
        db.add_all([
            Order(
                user_id=1,
                status="CONFIRMED",
                payment_status="PAID",
                subtotal=Decimal("100.00"),
                delivery_fee=Decimal("0.00"),
                total_amount=Decimal("100.00"),
            ),
            Order(
                user_id=2,
                status="CANCELLED",
                payment_status="PAID",
                subtotal=Decimal("50.00"),
                delivery_fee=Decimal("0.00"),
                total_amount=Decimal("50.00"),
            ),
            Order(
                user_id=3,
                status="PAYMENT_PENDING",
                payment_status="PAYMENT_PENDING",
                subtotal=Decimal("75.00"),
                delivery_fee=Decimal("0.00"),
                total_amount=Decimal("75.00"),
            ),
        ])
        db.commit()
    finally:
        db.close()

    response = client.get("/api/v1/orders/admin/analytics", headers=get_auth_headers(user_id=99, role="ADMIN"))

    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] == 3
    assert data["orders_by_status"] == {"CONFIRMED": 1, "CANCELLED": 1, "PAYMENT_PENDING": 1}
    assert data["cancelled_orders"] == 1
    assert float(data["total_revenue"]) == 100.0
    assert data["recent_orders"]
    assert "user_id" not in data["recent_orders"][0]
    assert "shipping_address" not in data["recent_orders"][0]


@pytest.mark.parametrize("role", ["CUSTOMER", "VENDOR", "FARMER"])
def test_non_admin_cannot_access_admin_order_analytics(role):
    response = client.get("/api/v1/orders/admin/analytics", headers=get_auth_headers(user_id=1, role=role))
    assert response.status_code == 403


def _add_paid_order_with_items(db, *, created_at, items, status="CONFIRMED", payment_status="PAID"):
    order = Order(
        user_id=1,
        status=status,
        payment_status=payment_status,
        subtotal=sum((Decimal(item["subtotal"]) for item in items), Decimal("0.00")),
        delivery_fee=Decimal("0.00"),
        total_amount=sum((Decimal(item["subtotal"]) for item in items), Decimal("0.00")),
        created_at=created_at,
    )
    db.add(order)
    db.flush()
    for item in items:
        db.add(OrderItem(
            order_id=order.id,
            product_id=item["product_id"],
            seller_id=item.get("seller_id"),
            product_name=item["product_name"],
            unit_price=Decimal(item["unit_price"]),
            quantity=item["quantity"],
            subtotal=Decimal(item["subtotal"]),
        ))
    db.commit()


def test_admin_business_insights_aggregate_paid_items_without_mixed_seller_double_counting():
    now = datetime.now(UTC).replace(tzinfo=None)
    previous_month = (now.replace(day=1) - timedelta(days=1)).replace(day=10)
    db = TestingSessionLocal()
    try:
        _add_paid_order_with_items(db, created_at=now, items=[
            {"product_id": 1, "seller_id": 10, "product_name": "Apples", "unit_price": "10.00", "quantity": 3, "subtotal": "30.00"},
            {"product_id": 2, "seller_id": 20, "product_name": "Spinach", "unit_price": "5.00", "quantity": 2, "subtotal": "10.00"},
        ])
        _add_paid_order_with_items(db, created_at=previous_month, items=[
            {"product_id": 1, "seller_id": 10, "product_name": "Apples", "unit_price": "10.00", "quantity": 8, "subtotal": "80.00"},
        ])
        _add_paid_order_with_items(db, created_at=now, status="CANCELLED", items=[
            {"product_id": 3, "seller_id": 30, "product_name": "Cancelled", "unit_price": "99.00", "quantity": 99, "subtotal": "9801.00"},
        ])
        _add_paid_order_with_items(db, created_at=now, payment_status="PAYMENT_PENDING", items=[
            {"product_id": 4, "seller_id": 40, "product_name": "Unpaid", "unit_price": "50.00", "quantity": 9, "subtotal": "450.00"},
        ])
    finally:
        db.close()

    response = client.get("/api/v1/orders/admin/business-insights", headers=get_auth_headers(user_id=99, role="ADMIN"))

    assert response.status_code == 200
    data = response.json()
    assert [entry["seller_id"] for entry in data["vendor_sales"]] == [10, 20]
    assert data["vendor_sales"][0] == {"seller_id": 10, "orders_count": 2, "units_sold": 11, "revenue": "110.00"}
    assert data["product_sales"][0]["product_id"] == 1
    assert data["product_sales"][0]["units_sold"] == 11
    assert data["product_sales"][0]["revenue"] == "110.00"
    assert data["sales_decline_available"] is True
    assert data["sales_declines"] == [{
        "product_id": 1,
        "product_name": "Apples",
        "current_period_quantity": 3,
        "previous_period_quantity": 8,
        "percentage_change": "-62.50",
    }]
    assert "user_id" not in data["vendor_sales"][0]


@pytest.mark.parametrize("role", ["CUSTOMER", "VENDOR", "FARMER"])
def test_non_admin_cannot_access_admin_business_insights(role):
    response = client.get("/api/v1/orders/admin/business-insights", headers=get_auth_headers(user_id=1, role=role))
    assert response.status_code == 403
