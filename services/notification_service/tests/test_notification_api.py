from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.security import jwt
from app.database.base import Base
from app.database.session import get_db
from main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def token(user_id: int, role: str = "CUSTOMER") -> str:
    return jwt.encode(
        {"sub": str(user_id), "role": role},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def headers(user_id: int, role: str = "CUSTOMER") -> dict:
    return {"Authorization": f"Bearer {token(user_id, role)}"}


def payload(user_id: int = 1, **overrides) -> dict:
    result = {
        "user_id": user_id,
        "type": "WELCOME",
        "title": "Welcome",
        "message": "Welcome to OrganicKart",
        "channel": "IN_APP",
    }
    result.update(overrides)
    return result


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def internal_headers():
    return {"X-Internal-Service-Key": "test-internal-key"}


def test_health_endpoint():
    assert client.get("/health").status_code == 200


def test_customer_list_detail_and_ownership():
    created = client.post("/api/v1/notifications", json=payload(), headers=internal_headers())
    assert created.status_code == 201
    notification_id = created.json()["id"]
    assert client.get("/api/v1/notifications", headers=headers(1)).status_code == 200
    assert client.get(f"/api/v1/notifications/{notification_id}", headers=headers(1)).status_code == 200
    assert client.get(f"/api/v1/notifications/{notification_id}", headers=headers(2)).status_code == 404


def test_authentication_is_required():
    assert client.get("/api/v1/notifications").status_code == 401
    assert client.get("/api/v1/notifications", headers={"Authorization": "Bearer invalid"}).status_code == 401


def test_read_and_read_all():
    first = client.post("/api/v1/notifications", json=payload(reference_type="USER", reference_id=1), headers=internal_headers()).json()
    pending = client.post("/api/v1/notifications", json=payload(reference_type="USER", reference_id=2), headers=internal_headers()).json()
    other = client.post("/api/v1/notifications", json=payload(user_id=2, reference_type="USER", reference_id=3), headers=internal_headers()).json()
    read = client.patch(f"/api/v1/notifications/{first['id']}/read", headers=headers(1))
    assert read.status_code == 200
    assert read.json()["status"] == "READ"
    all_read = client.patch("/api/v1/notifications/read-all", headers=headers(1))
    assert all_read.status_code == 200
    assert all_read.json()["updated"] == 1
    assert client.get(f"/api/v1/notifications/{pending['id']}", headers=headers(1)).json()["status"] == "READ"
    assert client.get(f"/api/v1/notifications/{other['id']}", headers=headers(1)).status_code == 404


def test_creation_is_admin_or_internal_only():
    assert client.post("/api/v1/notifications", json=payload(), headers=headers(1)).status_code == 403
    assert client.post("/api/v1/notifications", json=payload(), headers=headers(1, "ADMIN")).status_code == 201
    assert client.post("/api/v1/notifications", json={"user_id": 0}, headers=internal_headers()).status_code == 422


def test_idempotency_returns_existing_notification():
    event = payload(type="ORDER_CREATED", reference_type="ORDER", reference_id=44)
    first = client.post("/api/v1/notifications", json=event, headers=internal_headers())
    second = client.post("/api/v1/notifications", json=event, headers=internal_headers())
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]


def test_email_uses_mock_sender():
    response = client.post(
        "/api/v1/notifications",
        json=payload(channel="EMAIL", reference_type="USER", reference_id=99),
        headers=internal_headers(),
    )
    assert response.status_code == 201
    assert response.json()["status"] == "SENT"
    assert response.json()["sent_at"] is not None
