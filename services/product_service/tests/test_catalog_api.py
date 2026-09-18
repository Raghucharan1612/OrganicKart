import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.database.base import Base
from app.database.database import get_db
from main import app


SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def db_session():
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


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_product_list_returns_empty_catalog():
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    assert response.json() == []


def test_category_list_returns_empty_catalog():
    response = client.get("/api/v1/categories/")
    assert response.status_code == 200
    assert response.json() == []


def _admin_headers() -> dict:
    return {"Authorization": "Bearer " + _token("ADMIN", 1)}


def test_create_product_and_fetch_detail():
    category_response = client.post(
        "/api/v1/categories/",
        json={"name": "Vegetables", "description": "Fresh produce"},
        headers=_admin_headers(),
    )
    assert category_response.status_code == 201
    category_id = category_response.json()["id"]

    product_payload = {
        "seller_id": 10,
        "category_id": category_id,
        "name": "Organic Carrots",
        "description": "Sweet and crunchy carrots",
        "price": "12.50",
        "stock_quantity": 25,
        "unit": "kg",
        "certification": "USDA Organic",
        "image_url": "https://example.com/carrots.jpg",
        "is_active": True,
    }

    created = client.post("/api/v1/products/", json=product_payload, headers=_admin_headers())
    assert created.status_code == 201, created.text
    created_data = created.json()
    assert created_data["name"] == product_payload["name"]
    assert created_data["category_id"] == category_id
    assert created_data["price"] == "12.50"

    product_id = created_data["id"]
    approved = client.post(f"/api/v1/products/{product_id}/approve", headers=_admin_headers())
    assert approved.status_code == 200
    fetched = client.get(f"/api/v1/products/{product_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Organic Carrots"


def test_new_products_default_to_pending_and_admin_can_approve():
    category_response = client.post(
        "/api/v1/categories/",
        json={"name": "Leafy Greens", "description": "Fresh greens"},
        headers=_admin_headers(),
    )
    category_id = category_response.json()["id"]

    created = client.post(
        "/api/v1/products/",
        json={
            "seller_id": 9,
            "category_id": category_id,
            "name": "Spinach",
            "description": "Leafy greens",
            "price": "5.99",
            "stock_quantity": 30,
            "unit": "bunch",
        },
        headers=_admin_headers(),
    )
    assert created.status_code == 201, created.text
    assert created.json()["certification"] == "PENDING"

    approved = client.post(f"/api/v1/products/{created.json()['id']}/approve", headers=_admin_headers())
    assert approved.status_code == 200
    assert approved.json()["certification"] == "APPROVED"


def test_product_not_found():
    response = client.get("/api/v1/products/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_update_product():
    category_response = client.post(
        "/api/v1/categories/",
        json={"name": "Fruits", "description": "Fresh fruits"},
        headers=_admin_headers(),
    )
    category_id = category_response.json()["id"]

    created = client.post(
        "/api/v1/products/",
        json={
            "seller_id": 3,
            "category_id": category_id,
            "name": "Apples",
            "description": "Crisp apples",
            "price": "8.99",
            "stock_quantity": 10,
            "unit": "kg",
            "certification": "Local",
            "is_active": True,
        },
        headers=_admin_headers(),
    )
    product_id = created.json()["id"]

    updated = client.put(
        f"/api/v1/products/{product_id}",
        json={"name": "Honeycrisp Apples", "price": "9.49", "stock_quantity": 12},
        headers=_admin_headers(),
    )
    assert updated.status_code == 200
    data = updated.json()
    assert data["name"] == "Honeycrisp Apples"
    assert data["price"] == "9.49"
    assert data["stock_quantity"] == 12


def test_delete_product_soft_deletes():
    category_response = client.post("/api/v1/categories/", json={"name": "Bakery"}, headers=_admin_headers())
    category_id = category_response.json()["id"]

    created = client.post(
        "/api/v1/products/",
        json={
            "seller_id": 7,
            "category_id": category_id,
            "name": "Bread",
            "description": "Fresh baked bread",
            "price": "4.50",
            "stock_quantity": 8,
            "unit": "loaf",
            "is_active": True,
        },
        headers=_admin_headers(),
    )
    product_id = created.json()["id"]

    deleted = client.delete(f"/api/v1/products/{product_id}", headers=_admin_headers())
    assert deleted.status_code == 200
    assert deleted.json()["is_active"] is False

    detail = client.get(f"/api/v1/products/{product_id}")
    assert detail.status_code == 404


def test_create_category_and_fetch_detail():
    created = client.post("/api/v1/categories/", json={"name": "Dairy", "description": "Milk and cheese"}, headers=_admin_headers())
    assert created.status_code == 201
    category_id = created.json()["id"]

    fetched = client.get(f"/api/v1/categories/{category_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Dairy"


def test_category_not_found():
    response = client.get("/api/v1/categories/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_update_category():
    created = client.post("/api/v1/categories/", json={"name": "Grains", "description": "Whole grains"}, headers=_admin_headers())
    category_id = created.json()["id"]

    updated = client.put(
        f"/api/v1/categories/{category_id}",
        json={"name": "Whole Grains", "description": "Healthy grains"},
        headers=_admin_headers(),
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Whole Grains"


def test_delete_category_soft_deletes():
    created = client.post("/api/v1/categories/", json={"name": "Beverages"}, headers=_admin_headers())
    category_id = created.json()["id"]

    deleted = client.delete(f"/api/v1/categories/{category_id}", headers=_admin_headers())
    assert deleted.status_code == 200
    assert deleted.json()["is_active"] is False

    detail = client.get(f"/api/v1/categories/{category_id}")
    assert detail.status_code == 404


def test_invalid_product_data_rejected():
    category_response = client.post("/api/v1/categories/", json={"name": "Meat"}, headers=_admin_headers())
    category_id = category_response.json()["id"]

    bad_data = {
        "seller_id": 1,
        "category_id": category_id,
        "name": "",
        "price": "-1.00",
        "stock_quantity": -1,
        "unit": "",
    }
    response = client.post("/api/v1/products/", json=bad_data, headers=_admin_headers())
    assert response.status_code == 422


def test_invalid_category_data_rejected():
    response = client.post("/api/v1/categories/", json={"name": "", "description": "bad"}, headers=_admin_headers())
    assert response.status_code == 422


def test_invalid_category_reference_rejected():
    response = client.post(
        "/api/v1/products/",
        json={
            "seller_id": 1,
            "category_id": 999,
            "name": "Oranges",
            "description": "Fresh oranges",
            "price": "7.25",
            "stock_quantity": 11,
            "unit": "kg",
        },
        headers=_admin_headers(),
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_database_persistence_across_requests():
    category_response = client.post("/api/v1/categories/", json={"name": "Herbs"}, headers=_admin_headers())
    category_id = category_response.json()["id"]

    response = client.post(
        "/api/v1/products/",
        json={
            "seller_id": 18,
            "category_id": category_id,
            "name": "Basil",
            "description": "Fresh basil",
            "price": "3.30",
            "stock_quantity": 20,
            "unit": "bunch",
        },
        headers=_admin_headers(),
    )
    assert response.status_code == 201
    product_id = response.json()["id"]

    approved = client.post(f"/api/v1/products/{product_id}/approve", headers=_admin_headers())
    assert approved.status_code == 200

    retrieved = client.get(f"/api/v1/products/{product_id}")
    assert retrieved.status_code == 200
    assert retrieved.json()["name"] == "Basil"


def test_public_catalog_access_does_not_require_auth():
    category_response = client.post("/api/v1/categories/", json={"name": "Exotic"}, headers=_admin_headers())
    category_id = category_response.json()["id"]

    create_response = client.post(
        "/api/v1/products/",
        json={
            "seller_id": 42,
            "category_id": category_id,
            "name": "Mango",
            "description": "Sweet mango",
            "price": "6.25",
            "stock_quantity": 9,
            "unit": "kg",
        },
        headers=_admin_headers(),
    )
    assert create_response.status_code == 201
    approved = client.post(f"/api/v1/products/{create_response.json()['id']}/approve", headers=_admin_headers())
    assert approved.status_code == 200

    public_products = client.get("/api/v1/products/")
    public_categories = client.get("/api/v1/categories/")

    assert public_products.status_code == 200
    assert len(public_products.json()) == 1
    assert public_categories.status_code == 200
    assert len(public_categories.json()) == 1


def _token(role: str = "CUSTOMER", subject: int = 1) -> str:
    return jwt.encode({"sub": str(subject), "role": role}, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def test_product_catalog_filters_and_pagination():
    category_response = client.post("/api/v1/categories/", json={"name": "Fruit"}, headers=_admin_headers())
    category_id = category_response.json()["id"]

    for payload in [
        {"seller_id": 9, "category_id": category_id, "name": "Apple", "description": "Crisp apple", "price": "12.00", "stock_quantity": 3, "unit": "kg"},
        {"seller_id": 10, "category_id": category_id, "name": "Apricot", "description": "Sweet apricot", "price": "18.00", "stock_quantity": 2, "unit": "kg"},
        {"seller_id": 11, "category_id": category_id, "name": "Banana", "description": "Yellow banana", "price": "5.00", "stock_quantity": 10, "unit": "bunch"},
    ]:
        created = client.post("/api/v1/products/", json=payload, headers=_admin_headers())
        assert created.status_code == 201, created.text
        approved = client.post(f"/api/v1/products/{created.json()['id']}/approve", headers=_admin_headers())
        assert approved.status_code == 200, approved.text

    response = client.get(
        "/api/v1/products/",
        params={
            "search": "app",
            "category_id": category_id,
            "min_price": 5,
            "max_price": 20,
            "sort_by": "price",
            "sort_order": "asc",
            "page": 1,
            "page_size": 2,
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total"] == 2
    assert payload["items"][0]["name"] == "Apple"
    assert payload["items"][1]["name"] == "Apricot"

    bad_sort = client.get("/api/v1/products/", params={"sort_by": "secret"})
    assert bad_sort.status_code == 422

    bad_range = client.get("/api/v1/products/", params={"min_price": 20, "max_price": 5})
    assert bad_range.status_code == 422


def test_vendor_can_list_own_products_and_admin_can_filter_pending_certifications():
    category_response = client.post("/api/v1/categories/", json={"name": "Farm Fresh"}, headers=_admin_headers())
    category_id = category_response.json()["id"]

    vendor_headers = {"Authorization": "Bearer " + _token("VENDOR", 77)}
    created = client.post(
        "/api/v1/products/",
        json={
            "seller_id": 77,
            "category_id": category_id,
            "name": "Sweet Corn",
            "description": "Fresh sweet corn",
            "price": "4.25",
            "stock_quantity": 8,
            "unit": "piece",
        },
        headers=vendor_headers,
    )
    assert created.status_code == 201, created.text
    product_id = created.json()["id"]

    mine = client.get("/api/v1/products/mine", headers=vendor_headers)
    assert mine.status_code == 200, mine.text
    assert mine.json()[0]["id"] == product_id

    pending = client.get("/api/v1/products/", params={"certification": "PENDING"}, headers=_admin_headers())
    assert pending.status_code == 200, pending.text
    assert any(item["id"] == product_id for item in pending.json()["items"])

    admin_headers = {"Authorization": "Bearer " + _token("ADMIN", 1)}
    approved = client.post(f"/api/v1/products/{product_id}/approve", headers=admin_headers)
    assert approved.status_code == 200
    assert approved.json()["certification"] == "APPROVED"


def test_management_routes_require_auth_and_roles():
    category_response = client.post("/api/v1/categories/", json={"name": "Admin"}, headers=_admin_headers())
    category_id = category_response.json()["id"]

    unauth = client.post("/api/v1/products/", json={"seller_id": 1, "category_id": category_id, "name": "Mango", "description": "Tasty", "price": "10.00", "stock_quantity": 5, "unit": "kg"})
    assert unauth.status_code == 401

    customer_headers = {"Authorization": "Bearer " + _token("CUSTOMER", 2)}
    customer = client.post("/api/v1/products/", json={"seller_id": 2, "category_id": category_id, "name": "Pear", "description": "Fresh", "price": "11.00", "stock_quantity": 4, "unit": "kg"}, headers=customer_headers)
    assert customer.status_code == 403

    admin_headers = {"Authorization": "Bearer " + _token("ADMIN", 1)}
    created = client.post("/api/v1/products/", json={"seller_id": 1, "category_id": category_id, "name": "Pear", "description": "Fresh", "price": "11.00", "stock_quantity": 4, "unit": "kg"}, headers=admin_headers)
    assert created.status_code == 201


@pytest.mark.parametrize("role", ["VENDOR", "FARMER"])
@pytest.mark.parametrize("requested_certification", ["APPROVED", "REJECTED"])
def test_catalog_manager_certification_input_is_ignored_and_new_products_are_pending(role, requested_certification):
    category = client.post("/api/v1/categories/", json={"name": "Vendor catalog"}, headers=_admin_headers())
    manager_headers = {"Authorization": "Bearer " + _token(role, 73)}

    created = client.post(
        "/api/v1/products/",
        json={
            "seller_id": 1,
            "category_id": category.json()["id"],
            "name": f"Vendor product {requested_certification}",
            "price": "10.00",
            "stock_quantity": 3,
            "unit": "kg",
            "certification": requested_certification,
        },
        headers=manager_headers,
    )

    assert created.status_code == 201, created.text
    assert created.json()["seller_id"] == 73
    assert created.json()["certification"] == "PENDING"


@pytest.mark.parametrize("role", ["VENDOR", "FARMER"])
@pytest.mark.parametrize("requested_certification", ["APPROVED", "REJECTED"])
def test_catalog_manager_update_cannot_change_certification(role, requested_certification):
    category = client.post("/api/v1/categories/", json={"name": "Vendor updates"}, headers=_admin_headers())
    manager_headers = {"Authorization": "Bearer " + _token(role, 74)}
    created = client.post(
        "/api/v1/products/",
        json={
            "category_id": category.json()["id"],
            "name": "Pending vendor product",
            "price": "10.00",
            "stock_quantity": 3,
            "unit": "kg",
        },
        headers=manager_headers,
    )

    updated = client.put(
        f"/api/v1/products/{created.json()['id']}",
        json={"name": "Renamed vendor product", "certification": requested_certification},
        headers=manager_headers,
    )

    assert updated.status_code == 200, updated.text
    assert updated.json()["name"] == "Renamed vendor product"
    assert updated.json()["certification"] == "PENDING"


def test_admin_can_reject_pending_product():
    category = client.post("/api/v1/categories/", json={"name": "Certification queue"}, headers=_admin_headers())
    created = client.post(
        "/api/v1/products/",
        json={"category_id": category.json()["id"], "name": "Rejected crop", "price": "10.00", "stock_quantity": 3, "unit": "kg"},
        headers={"Authorization": "Bearer " + _token("FARMER", 75)},
    )

    rejected = client.post(f"/api/v1/products/{created.json()['id']}/reject", headers=_admin_headers())
    assert rejected.status_code == 200, rejected.text
    assert rejected.json()["certification"] == "REJECTED"


def test_customer_catalog_only_exposes_active_approved_products():
    category = client.post("/api/v1/categories/", json={"name": "Customer catalog"}, headers=_admin_headers())
    category_id = category.json()["id"]

    def create(name):
        response = client.post(
            "/api/v1/products/",
            json={"category_id": category_id, "name": name, "price": "10.00", "stock_quantity": 3, "unit": "kg"},
            headers={"Authorization": "Bearer " + _token("VENDOR", 76)},
        )
        assert response.status_code == 201, response.text
        return response.json()["id"]

    pending_id = create("Pending crop")
    rejected_id = create("Rejected crop")
    approved_id = create("Approved crop")
    inactive_approved_id = create("Inactive approved crop")
    assert client.post(f"/api/v1/products/{rejected_id}/reject", headers=_admin_headers()).status_code == 200
    assert client.post(f"/api/v1/products/{approved_id}/approve", headers=_admin_headers()).status_code == 200
    assert client.post(f"/api/v1/products/{inactive_approved_id}/approve", headers=_admin_headers()).status_code == 200
    assert client.delete(f"/api/v1/products/{inactive_approved_id}", headers=_admin_headers()).status_code == 200

    catalog = client.get("/api/v1/products/")
    assert catalog.status_code == 200
    assert [item["id"] for item in catalog.json()] == [approved_id]
    assert client.get(f"/api/v1/products/{pending_id}").status_code == 404
    assert client.get(f"/api/v1/products/{rejected_id}").status_code == 404
    assert client.get(f"/api/v1/products/{inactive_approved_id}").status_code == 404
