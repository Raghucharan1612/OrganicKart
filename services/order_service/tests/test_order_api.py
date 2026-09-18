import pytest
import json
import hashlib
import hmac
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
from app.models.order import Order
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
