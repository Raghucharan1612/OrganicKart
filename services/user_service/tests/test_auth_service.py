import pytest
from fastapi import status
from fastapi.testclient import TestClient
from jose import jwt

from app.core.config import settings
from app.core.security import create_access_token, decode_access_token
from app.database.base import Base
from app.database.session import engine, get_db
from main import app


def override_get_db():
    from sqlalchemy.orm import sessionmaker

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_db():
    reset_db()
    yield
    reset_db()


def test_register_user_success():
    payload = {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "password": "Secret123",
        "phone": "1234567890",
        "role": "CUSTOMER",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "jane@example.com"
    assert data["full_name"] == "Jane Doe"
    assert data["role"] == "CUSTOMER"
    assert "password_hash" not in data


def test_duplicate_email_returns_conflict():
    payload = {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "password": "Secret123",
        "phone": "1234567890",
        "role": "CUSTOMER",
    }
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_invalid_registration_data():
    response = client.post(
        "/api/v1/auth/register",
        json={"full_name": "J", "email": "bad-email", "password": "short", "role": "ADMIN"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_registration_requires_phone_number():
    response = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Jane Doe", "email": "no-phone@example.com", "password": "Secret123", "role": "CUSTOMER"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_success():
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "password": "Secret123",
            "phone": "1234567890",
            "role": "CUSTOMER",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "jane@example.com", "password": "Secret123"},
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_invalid_password_fails():
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "password": "Secret123",
            "phone": "1234567890",
            "role": "CUSTOMER",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "jane@example.com", "password": "WrongPass123"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unknown_user_fails():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "Secret123"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_jwt_generation_and_validation():
    token = create_access_token("42", extra_claims={"role": "CUSTOMER"})
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "42"
    assert decoded["role"] == "CUSTOMER"


def test_expired_jwt_rejected():
    expired = jwt.encode(
        {"sub": "1", "exp": -1},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    assert decode_access_token(expired) is None


def test_invalid_jwt_rejected():
    assert decode_access_token("not-a-valid-token") is None


def test_current_user_endpoint():
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "password": "Secret123",
            "phone": "1234567890",
            "role": "CUSTOMER",
        },
    )
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "jane@example.com", "password": "Secret123"},
    ).json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "jane@example.com"


def test_role_handling_and_unauthorized_access():
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "password": "Secret123",
            "phone": "1234567890",
            "role": "CUSTOMER",
        },
    )
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "jane@example.com", "password": "Secret123"},
    ).json()["access_token"]

    protected_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert protected_response.status_code == status.HTTP_200_OK
    assert protected_response.json()["role"] == "CUSTOMER"

    invalid_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert invalid_response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_my_profile_endpoint():
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "password": "Secret123",
            "phone": "1234567890",
            "role": "CUSTOMER",
        },
    )
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "jane@example.com", "password": "Secret123"},
    ).json()["access_token"]

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "jane@example.com"
    assert response.json()["full_name"] == "Jane Doe"


def test_update_my_profile_endpoint():
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "password": "Secret123",
            "phone": "1234567890",
            "role": "CUSTOMER",
        },
    )
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "jane@example.com", "password": "Secret123"},
    ).json()["access_token"]

    response = client.put(
        "/api/v1/users/me",
        json={"full_name": "Jane Smith", "phone": "9876543210"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["full_name"] == "Jane Smith"
    assert response.json()["phone"] == "9876543210"
    assert response.json()["email"] == "jane@example.com"


def test_authenticated_user_can_change_password():
    client.post(
        "/api/v1/auth/register",
        json={"full_name": "Jane Doe", "email": "change@example.com", "password": "Secret123", "phone": "1234567890", "role": "CUSTOMER"},
    )
    token = client.post("/api/v1/auth/login", json={"email": "change@example.com", "password": "Secret123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    changed = client.post(
        "/api/v1/users/me/change-password",
        json={"current_password": "Secret123", "new_password": "NewSecret456"},
        headers=headers,
    )

    assert changed.status_code == status.HTTP_200_OK
    assert changed.json() == {"message": "Password changed successfully."}
    assert client.post("/api/v1/auth/login", json={"email": "change@example.com", "password": "Secret123"}).status_code == status.HTTP_401_UNAUTHORIZED
    assert client.post("/api/v1/auth/login", json={"email": "change@example.com", "password": "NewSecret456"}).status_code == status.HTTP_200_OK


def test_change_password_rejects_incorrect_current_or_invalid_new_password():
    headers = _register_and_login("password-errors@example.com")

    incorrect_current = client.post(
        "/api/v1/users/me/change-password",
        json={"current_password": "WrongPassword123", "new_password": "NewSecret456"},
        headers=headers,
    )
    invalid_new = client.post(
        "/api/v1/users/me/change-password",
        json={"current_password": "Secret123", "new_password": "password"},
        headers=headers,
    )

    assert incorrect_current.status_code == status.HTTP_400_BAD_REQUEST
    assert invalid_new.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_password_reset_uses_expiring_single_use_token(monkeypatch):
    monkeypatch.setattr(settings, "APP_ENV", "development")
    client.post(
        "/api/v1/auth/register",
        json={"full_name": "Jane Doe", "email": "forgot@example.com", "password": "Secret123", "phone": "1234567890", "role": "CUSTOMER"},
    )

    requested = client.post("/api/v1/auth/password-reset/request", json={"email": "forgot@example.com"})
    assert requested.status_code == status.HTTP_200_OK
    reset_token = requested.json()["development_reset_token"]
    assert reset_token

    reset = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": reset_token, "new_password": "ResetSecret456"},
    )
    assert reset.status_code == status.HTTP_200_OK
    assert client.post("/api/v1/auth/password-reset/confirm", json={"token": reset_token, "new_password": "ResetSecret456"}).status_code == status.HTTP_400_BAD_REQUEST
    assert client.post("/api/v1/auth/login", json={"email": "forgot@example.com", "password": "ResetSecret456"}).status_code == status.HTTP_200_OK
    assert client.post("/api/v1/auth/login", json={"email": "forgot@example.com", "password": "Secret123"}).status_code == status.HTTP_401_UNAUTHORIZED


def test_password_reset_request_does_not_reveal_unknown_email(monkeypatch):
    monkeypatch.setattr(settings, "APP_ENV", "development")
    response = client.post("/api/v1/auth/password-reset/request", json={"email": "unknown@example.com"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["development_reset_token"] is None


def _register_and_login(email: str, role: str = "CUSTOMER") -> dict:
    registered = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Address User", "email": email, "password": "Secret123", "phone": "9876543210", "role": role},
    )
    assert registered.status_code == status.HTTP_201_CREATED
    token = client.post("/api/v1/auth/login", json={"email": email, "password": "Secret123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _address_payload(**overrides):
    payload = {
        "label": "Home",
        "recipient_name": "Jane Doe",
        "phone": "9876543210",
        "address_line1": "123 Market Street",
        "address_line2": "Flat 4B",
        "city": "Bengaluru",
        "state": "Karnataka",
        "postal_code": "560001",
        "country": "India",
    }
    payload.update(overrides)
    return payload


def test_customer_address_crud_and_default_behavior():
    headers = _register_and_login("addresses@example.com")
    first = client.post("/api/v1/users/me/addresses", json=_address_payload(is_default=True), headers=headers)
    assert first.status_code == status.HTTP_201_CREATED
    assert first.json()["is_default"] is True

    second = client.post(
        "/api/v1/users/me/addresses",
        json=_address_payload(label="Work", address_line1="500 Office Road", is_default=True, latitude="12.971599", longitude="77.594566"),
        headers=headers,
    )
    assert second.status_code == status.HTTP_201_CREATED
    assert second.json()["latitude"] == "12.971599"

    listed = client.get("/api/v1/users/me/addresses", headers=headers)
    assert listed.status_code == status.HTTP_200_OK
    assert [item["is_default"] for item in listed.json()] == [True, False]
    assert listed.json()[0]["id"] == second.json()["id"]

    updated = client.put(
        f"/api/v1/users/me/addresses/{first.json()['id']}",
        json={"city": "Mysuru", "is_default": True},
        headers=headers,
    )
    assert updated.status_code == status.HTTP_200_OK
    assert updated.json()["city"] == "Mysuru"
    assert updated.json()["is_default"] is True

    after_update = client.get("/api/v1/users/me/addresses", headers=headers).json()
    assert [item["is_default"] for item in after_update] == [True, False]

    deleted = client.delete(f"/api/v1/users/me/addresses/{second.json()['id']}", headers=headers)
    assert deleted.status_code == status.HTTP_204_NO_CONTENT
    assert len(client.get("/api/v1/users/me/addresses", headers=headers).json()) == 1


def test_customer_address_ownership_and_access_control():
    owner_headers = _register_and_login("owner@example.com")
    other_headers = _register_and_login("other@example.com")
    address = client.post("/api/v1/users/me/addresses", json=_address_payload(), headers=owner_headers).json()

    assert client.get("/api/v1/users/me/addresses").status_code == status.HTTP_403_FORBIDDEN
    assert client.get("/api/v1/users/me/addresses", headers=other_headers).json() == []
    assert client.put(f"/api/v1/users/me/addresses/{address['id']}", json={"city": "Delhi"}, headers=other_headers).status_code == status.HTTP_404_NOT_FOUND
    assert client.delete(f"/api/v1/users/me/addresses/{address['id']}", headers=other_headers).status_code == status.HTTP_404_NOT_FOUND

    vendor_headers = _register_and_login("vendor-address@example.com", role="VENDOR")
    assert client.get("/api/v1/users/me/addresses", headers=vendor_headers).status_code == status.HTTP_403_FORBIDDEN
