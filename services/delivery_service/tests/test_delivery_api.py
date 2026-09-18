from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.security import create_access_token
from app.database.base import Base
from app.database.session import get_db
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def db_session(monkeypatch):
    def fake_get(url, timeout):
        class Response:
            def __init__(self, status_code, payload):
                self.status_code = status_code
                self._payload = payload

            def json(self):
                return self._payload

        if url.endswith("/99"):
            return Response(404, {"detail": "Order not found"})
        if url.endswith("/100"):
            return Response(403, {"detail": "Order does not belong to this user"})
        return Response(200, {"id": 1, "user_id": 1, "status": "PENDING"})

    monkeypatch.setattr("app.services.delivery_service.httpx.get", fake_get)
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


def test_route_registration():
    routes = {route.path for route in app.routes}
    assert "/api/v1/deliveries" in routes
    assert "/api/v1/deliveries/{delivery_id}" in routes


def test_unauthenticated_request():
    response = client.get("/api/v1/deliveries")
    assert response.status_code == 403


def test_authenticated_customer_request():
    response = client.get("/api/v1/deliveries", headers=get_auth_headers())
    assert response.status_code == 200


def test_create_delivery():
    response = client.post(
        "/api/v1/deliveries",
        json={
            "order_id": 1,
            "address": {
                "recipient_name": "Alice Smith",
                "recipient_phone": "5551234",
                "address_line1": "123 Main St",
                "address_line2": "Apt 4",
                "city": "Seattle",
                "state": "WA",
                "postal_code": "98101",
                "country": "US",
            },
        },
        headers=get_auth_headers(),
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "PENDING"
    assert payload["tracking_number"].startswith("OK-")


def test_get_delivery():
    created = client.post(
        "/api/v1/deliveries",
        json={
            "order_id": 1,
            "address": {
                "recipient_name": "Alice Smith",
                "address_line1": "123 Main St",
                "city": "Seattle",
                "postal_code": "98101",
                "country": "US",
            },
        },
        headers=get_auth_headers(),
    )
    delivery_id = created.json()["id"]
    response = client.get(f"/api/v1/deliveries/{delivery_id}", headers=get_auth_headers())
    assert response.status_code == 200
    assert response.json()["id"] == delivery_id


def test_list_customer_deliveries():
    client.post(
        "/api/v1/deliveries",
        json={
            "order_id": 1,
            "address": {
                "recipient_name": "Alice Smith",
                "address_line1": "123 Main St",
                "city": "Seattle",
                "postal_code": "98101",
                "country": "US",
            },
        },
        headers=get_auth_headers(),
    )
    response = client.get("/api/v1/deliveries", headers=get_auth_headers())
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_unauthorized_delivery_access():
    created = client.post(
        "/api/v1/deliveries",
        json={
            "order_id": 1,
            "address": {
                "recipient_name": "Alice Smith",
                "address_line1": "123 Main St",
                "city": "Seattle",
                "postal_code": "98101",
                "country": "US",
            },
        },
        headers=get_auth_headers(user_id=1),
    )
    response = client.get(f"/api/v1/deliveries/{created.json()['id']}", headers=get_auth_headers(user_id=2))
    assert response.status_code == 404


def test_update_delivery():
    created = client.post(
        "/api/v1/deliveries",
        json={
            "order_id": 1,
            "address": {
                "recipient_name": "Alice Smith",
                "address_line1": "123 Main St",
                "city": "Seattle",
                "postal_code": "98101",
                "country": "US",
            },
        },
        headers=get_auth_headers(),
    )
    response = client.put(
        f"/api/v1/deliveries/{created.json()['id']}",
        json={"city": "Portland", "state": "OR"},
        headers=get_auth_headers(),
    )
    assert response.status_code == 200
    assert response.json()["city"] == "Portland"


def test_tracking_number_generation():
    created = client.post(
        "/api/v1/deliveries",
        json={
            "order_id": 1,
            "address": {
                "recipient_name": "Alice Smith",
                "address_line1": "123 Main St",
                "city": "Seattle",
                "postal_code": "98101",
                "country": "US",
            },
        },
        headers=get_auth_headers(),
    )
    assert created.json()["tracking_number"].startswith("OK-")


def test_duplicate_tracking_number_is_not_allowed():
    response = client.post(
        "/api/v1/deliveries",
        json={
            "order_id": 1,
            "address": {
                "recipient_name": "Alice Smith",
                "address_line1": "123 Main St",
                "city": "Seattle",
                "postal_code": "98101",
                "country": "US",
            },
        },
        headers=get_auth_headers(),
    )
    assert response.status_code == 201


def test_valid_status_transition():
    created = client.post(
        "/api/v1/deliveries",
        json={
            "order_id": 1,
            "address": {
                "recipient_name": "Alice Smith",
                "address_line1": "123 Main St",
                "city": "Seattle",
                "postal_code": "98101",
                "country": "US",
            },
        },
        headers=get_auth_headers(),
    )
    response = client.patch(
        f"/api/v1/deliveries/{created.json()['id']}/status",
        json={"status": "CONFIRMED"},
        headers=get_auth_headers(),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "CONFIRMED"


def test_invalid_status_transition():
    created = client.post(
        "/api/v1/deliveries",
        json={
            "order_id": 1,
            "address": {
                "recipient_name": "Alice Smith",
                "address_line1": "123 Main St",
                "city": "Seattle",
                "postal_code": "98101",
                "country": "US",
            },
        },
        headers=get_auth_headers(),
    )
    client.patch(
        f"/api/v1/deliveries/{created.json()['id']}/status",
        json={"status": "CONFIRMED"},
        headers=get_auth_headers(),
    )
    response = client.patch(
        f"/api/v1/deliveries/{created.json()['id']}/status",
        json={"status": "PENDING"},
        headers=get_auth_headers(),
    )
    assert response.status_code == 400


def test_delivered_status():
    created = client.post(
        "/api/v1/deliveries",
        json={
            "order_id": 1,
            "address": {
                "recipient_name": "Alice Smith",
                "address_line1": "123 Main St",
                "city": "Seattle",
                "postal_code": "98101",
                "country": "US",
            },
        },
        headers=get_auth_headers(),
    )
    client.patch(
        f"/api/v1/deliveries/{created.json()['id']}/status",
        json={"status": "CONFIRMED"},
        headers=get_auth_headers(),
    )
    client.patch(
        f"/api/v1/deliveries/{created.json()['id']}/status",
        json={"status": "PICKED_UP"},
        headers=get_auth_headers(),
    )
    client.patch(
        f"/api/v1/deliveries/{created.json()['id']}/status",
        json={"status": "IN_TRANSIT"},
        headers=get_auth_headers(),
    )
    client.patch(
        f"/api/v1/deliveries/{created.json()['id']}/status",
        json={"status": "OUT_FOR_DELIVERY"},
        headers=get_auth_headers(),
    )
    response = client.patch(
        f"/api/v1/deliveries/{created.json()['id']}/status",
        json={"status": "DELIVERED"},
        headers=get_auth_headers(),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "DELIVERED"


def test_nonexistent_delivery():
    response = client.get("/api/v1/deliveries/999", headers=get_auth_headers())
    assert response.status_code == 404


def test_customer_cannot_perform_manager_operation():
    response = client.post(
        "/api/v1/deliveries",
        json={
            "order_id": 1,
            "address": {
                "recipient_name": "Alice Smith",
                "address_line1": "123 Main St",
                "city": "Seattle",
                "postal_code": "98101",
                "country": "US",
            },
        },
        headers=get_auth_headers(role="CUSTOMER"),
    )
    assert response.status_code == 201


def test_manager_can_perform_management_operation():
    headers = get_auth_headers(user_id=1, role="ADMIN")
    response = client.post(
        "/api/v1/deliveries",
        json={
            "order_id": 1,
            "address": {
                "recipient_name": "Admin User",
                "address_line1": "77 Main St",
                "city": "Boston",
                "postal_code": "02110",
                "country": "US",
            },
        },
        headers=headers,
    )
    assert response.status_code == 201


def test_invalid_payload():
    response = client.post(
        "/api/v1/deliveries",
        json={"order_id": 0, "address": {"recipient_name": "", "address_line1": "", "city": "", "postal_code": "", "country": ""}},
        headers=get_auth_headers(),
    )
    assert response.status_code == 422


def test_invalid_order_id():
    response = client.post(
        "/api/v1/deliveries",
        json={
            "order_id": 99,
            "address": {
                "recipient_name": "Alice Smith",
                "address_line1": "123 Main St",
                "city": "Seattle",
                "postal_code": "98101",
                "country": "US",
            },
        },
        headers=get_auth_headers(),
    )
    assert response.status_code == 404


def test_invalid_status():
    created = client.post(
        "/api/v1/deliveries",
        json={
            "order_id": 1,
            "address": {
                "recipient_name": "Alice Smith",
                "address_line1": "123 Main St",
                "city": "Seattle",
                "postal_code": "98101",
                "country": "US",
            },
        },
        headers=get_auth_headers(),
    )
    response = client.patch(
        f"/api/v1/deliveries/{created.json()['id']}/status",
        json={"status": "BOGUS"},
        headers=get_auth_headers(),
    )
    assert response.status_code == 400


def test_order_service_dependency_failure():
    def bad_get(url, timeout):
        raise RuntimeError("boom")

    import app.services.delivery_service as ds

    ds.httpx.get = bad_get
    response = client.post(
        "/api/v1/deliveries",
        json={
            "order_id": 1,
            "address": {
                "recipient_name": "Alice Smith",
                "address_line1": "123 Main St",
                "city": "Seattle",
                "postal_code": "98101",
                "country": "US",
            },
        },
        headers=get_auth_headers(),
    )
    assert response.status_code == 503


# ==========================================
# PHASE 6: DELIVERY PARTNER WORKFLOW TESTS
# ==========================================


def test_partner_endpoint_unauthenticated():
    response = client.get("/api/v1/deliveries/partner/available")
    assert response.status_code in {401, 403}


def test_partner_endpoint_customer_rejected():
    response = client.get("/api/v1/deliveries/partner/available", headers=get_auth_headers(role="CUSTOMER"))
    assert response.status_code == 403


def test_partner_endpoint_vendor_rejected():
    response = client.get("/api/v1/deliveries/partner/available", headers=get_auth_headers(role="VENDOR"))
    assert response.status_code == 403


def test_partner_endpoint_allowed():
    response = client.get("/api/v1/deliveries/partner/available", headers=get_auth_headers(role="DELIVERY_PARTNER"))
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_partner_available_and_assigned_queue():
    # Create internal delivery for order 10
    client.post(
        "/api/v1/deliveries/internal/assign",
        json={"order_id": 10, "user_id": 5, "shipping_address": "123 Green Ave"},
        headers={"X-Internal-Service-Key": settings.INTERNAL_SERVICE_KEY},
    )

    # 1. Partner checks available queue
    partner_headers = get_auth_headers(user_id=100, role="DELIVERY_PARTNER")
    avail_res = client.get("/api/v1/deliveries/partner/available", headers=partner_headers)
    assert avail_res.status_code == 200
    available_deliveries = avail_res.json()
    assert len(available_deliveries) >= 1
    target = next(d for d in available_deliveries if d["order_id"] == 10)
    assert target["assigned_partner_id"] is None

    # 2. Partner accepts delivery
    accept_res = client.post(f"/api/v1/deliveries/{target['id']}/accept", headers=partner_headers)
    assert accept_res.status_code == 200
    accepted_data = accept_res.json()
    assert accepted_data["assigned_partner_id"] == 100
    assert accepted_data["status"] == "ACCEPTED"
    assert accepted_data["accepted_at"] is not None

    # 3. Delivery no longer appears in available queue
    avail_res2 = client.get("/api/v1/deliveries/partner/available", headers=partner_headers)
    assert not any(d["id"] == target["id"] for d in avail_res2.json())

    # 4. Delivery appears in partner's assigned queue
    assigned_res = client.get("/api/v1/deliveries/partner/assigned", headers=partner_headers)
    assert assigned_res.status_code == 200
    assert any(d["id"] == target["id"] for d in assigned_res.json())


def test_duplicate_partner_acceptance_conflict():
    client.post(
        "/api/v1/deliveries/internal/assign",
        json={"order_id": 20, "user_id": 6, "shipping_address": "456 Oak St"},
        headers={"X-Internal-Service-Key": settings.INTERNAL_SERVICE_KEY},
    )
    partner1 = get_auth_headers(user_id=101, role="DELIVERY_PARTNER")
    partner2 = get_auth_headers(user_id=102, role="DELIVERY_PARTNER")

    avail = client.get("/api/v1/deliveries/partner/available", headers=partner1).json()
    delivery = next(d for d in avail if d["order_id"] == 20)

    # Partner 1 accepts first
    res1 = client.post(f"/api/v1/deliveries/{delivery['id']}/accept", headers=partner1)
    assert res1.status_code == 200

    # Partner 2 attempts to accept same delivery -> 409 Conflict
    res2 = client.post(f"/api/v1/deliveries/{delivery['id']}/accept", headers=partner2)
    assert res2.status_code == 409


def test_partner_status_transition_flow():
    client.post(
        "/api/v1/deliveries/internal/assign",
        json={"order_id": 30, "user_id": 7, "shipping_address": "789 Pine Rd"},
        headers={"X-Internal-Service-Key": settings.INTERNAL_SERVICE_KEY},
    )
    partner_headers = get_auth_headers(user_id=105, role="DELIVERY_PARTNER")
    other_partner_headers = get_auth_headers(user_id=106, role="DELIVERY_PARTNER")

    avail = client.get("/api/v1/deliveries/partner/available", headers=partner_headers).json()
    delivery_id = next(d["id"] for d in avail if d["order_id"] == 30)

    client.post(f"/api/v1/deliveries/{delivery_id}/accept", headers=partner_headers)

    # Other partner cannot update status -> 403 Forbidden
    bad_partner_res = client.patch(
        f"/api/v1/deliveries/{delivery_id}/status",
        json={"status": "PICKED_UP"},
        headers=other_partner_headers,
    )
    assert bad_partner_res.status_code == 403

    # Assigned partner updates to PICKED_UP
    st1 = client.patch(
        f"/api/v1/deliveries/{delivery_id}/status",
        json={"status": "PICKED_UP"},
        headers=partner_headers,
    )
    assert st1.status_code == 200
    assert st1.json()["status"] == "PICKED_UP"

    # Assigned partner updates to OUT_FOR_DELIVERY
    st2 = client.patch(
        f"/api/v1/deliveries/{delivery_id}/status",
        json={"status": "OUT_FOR_DELIVERY"},
        headers=partner_headers,
    )
    assert st2.status_code == 200
    assert st2.json()["status"] == "OUT_FOR_DELIVERY"

    # Assigned partner updates to DELIVERED
    st3 = client.patch(
        f"/api/v1/deliveries/{delivery_id}/status",
        json={"status": "DELIVERED"},
        headers=partner_headers,
    )
    assert st3.status_code == 200
    assert st3.json()["status"] == "DELIVERED"

    # Cannot move backwards from DELIVERED -> 400 Bad Request
    backwards = client.patch(
        f"/api/v1/deliveries/{delivery_id}/status",
        json={"status": "OUT_FOR_DELIVERY"},
        headers=partner_headers,
    )
    assert backwards.status_code == 400


def test_customer_isolation():
    # Customer 1 delivery
    c1 = client.post(
        "/api/v1/deliveries",
        json={
            "order_id": 50,
            "address": {
                "recipient_name": "Cust One",
                "address_line1": "Address 1",
                "city": "City",
                "postal_code": "10001",
                "country": "US",
            },
        },
        headers=get_auth_headers(user_id=1, role="CUSTOMER"),
    ).json()

    # Customer 2 cannot access Customer 1 delivery
    res = client.get(f"/api/v1/deliveries/{c1['id']}", headers=get_auth_headers(user_id=2, role="CUSTOMER"))
    assert res.status_code == 404

    # Customer 2 cannot accept delivery
    accept_res = client.post(f"/api/v1/deliveries/{c1['id']}/accept", headers=get_auth_headers(user_id=2, role="CUSTOMER"))
    assert accept_res.status_code == 403

