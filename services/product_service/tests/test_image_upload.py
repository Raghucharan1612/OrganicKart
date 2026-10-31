import io
import os
from pathlib import Path
import pytest
from app.core.config import settings
from app.database.base import Base
from app.services.image_service import get_upload_dir
from test_catalog_api import client, engine, _token


@pytest.fixture(autouse=True)
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _auth_header(role: str = "CUSTOMER", user_id: int = 1) -> dict:
    return {"Authorization": f"Bearer {_token(role=role, subject=user_id)}"}


# Realistic valid image bytes
VALID_JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00" + b"\x00" * 50 + b"\xff\xd9"
VALID_PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
VALID_WEBP = b"RIFF\x20\x00\x00\x00WEBPVP8 " + b"\x00" * 20


def _create_category_and_product(seller_id: int = 10, role: str = "VENDOR") -> tuple[int, int]:
    cat = client.post(
        "/api/v1/categories/",
        json={"name": "Fresh Organic Produce"},
        headers=_auth_header("ADMIN", 999),
    )
    assert cat.status_code == 201
    cat_id = cat.json()["id"]

    prod = client.post(
        "/api/v1/products/",
        json={
            "category_id": cat_id,
            "name": "Organic Tomatoes",
            "description": "Vine ripened",
            "price": "40.00",
            "stock_quantity": 50,
            "unit": "kg",
            "is_active": True,
        },
        headers=_auth_header(role, seller_id),
    )
    assert prod.status_code == 201
    return cat_id, prod.json()["id"]


def test_valid_single_and_multi_image_upload():
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    files = [
        ("files", ("tomato1.jpg", io.BytesIO(VALID_JPEG), "image/jpeg")),
        ("files", ("tomato2.png", io.BytesIO(VALID_PNG), "image/png")),
    ]

    response = client.post(
        f"/api/v1/products/{product_id}/images",
        files=files,
        headers=_auth_header("VENDOR", 10),
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert len(data) == 2
    assert data[0]["is_primary"] is True
    assert data[0]["mime_type"] == "image/jpeg"
    assert data[1]["is_primary"] is False
    assert data[1]["mime_type"] == "image/png"
    assert data[0]["url"] == f"/api/v1/products/images/{data[0]['id']}"

    # Verify product detail now reflects primary image_url and images list
    detail = client.get(f"/api/v1/products/{product_id}", headers=_auth_header("VENDOR", 10))
    assert detail.status_code == 200
    prod_data = detail.json()
    assert prod_data["image_url"] == data[0]["url"]
    assert len(prod_data["images"]) == 2


def test_invalid_image_format_rejected():
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    # A plain text / fake file disguised as png
    fake_png = b"This is not a real PNG image content."
    files = [("files", ("fake.png", io.BytesIO(fake_png), "image/png"))]

    response = client.post(
        f"/api/v1/products/{product_id}/images",
        files=files,
        headers=_auth_header("VENDOR", 10),
    )
    assert response.status_code == 422
    assert "Unsupported image format or invalid file signature" in response.json()["detail"]


def test_empty_image_rejected():
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")
    files = [("files", ("empty.jpg", io.BytesIO(b""), "image/jpeg"))]

    response = client.post(
        f"/api/v1/products/{product_id}/images",
        files=files,
        headers=_auth_header("VENDOR", 10),
    )
    assert response.status_code == 422
    assert "empty" in response.json()["detail"].lower()


def test_oversized_image_rejected():
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")
    oversized_data = VALID_JPEG + b"0" * (5 * 1024 * 1024 + 100)
    files = [("files", ("huge.jpg", io.BytesIO(oversized_data), "image/jpeg"))]

    response = client.post(
        f"/api/v1/products/{product_id}/images",
        files=files,
        headers=_auth_header("VENDOR", 10),
    )
    assert response.status_code == 413
    assert "exceeds" in response.json()["detail"].lower()


def test_missing_authentication_rejected():
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")
    files = [("files", ("tomato.jpg", io.BytesIO(VALID_JPEG), "image/jpeg"))]

    response = client.post(f"/api/v1/products/{product_id}/images", files=files)
    assert response.status_code == 401


def test_customer_role_forbidden():
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")
    files = [("files", ("tomato.jpg", io.BytesIO(VALID_JPEG), "image/jpeg"))]

    response = client.post(
        f"/api/v1/products/{product_id}/images",
        files=files,
        headers=_auth_header("CUSTOMER", 10),
    )
    assert response.status_code == 403


def test_cross_vendor_access_forbidden():
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    # Vendor 10 uploads an image
    files = [("files", ("tomato.jpg", io.BytesIO(VALID_JPEG), "image/jpeg"))]
    upload_res = client.post(
        f"/api/v1/products/{product_id}/images",
        files=files,
        headers=_auth_header("VENDOR", 10),
    )
    assert upload_res.status_code == 201
    image_id = upload_res.json()[0]["id"]

    # Vendor 20 tries to upload to Vendor 10's product
    cross_upload = client.post(
        f"/api/v1/products/{product_id}/images",
        files=files,
        headers=_auth_header("VENDOR", 20),
    )
    assert cross_upload.status_code == 403
    assert "own" in cross_upload.json()["detail"]

    # Vendor 20 tries to set primary
    cross_primary = client.patch(
        f"/api/v1/products/{product_id}/images/{image_id}/primary",
        headers=_auth_header("VENDOR", 20),
    )
    assert cross_primary.status_code == 403

    # Vendor 20 tries to replace
    cross_replace = client.put(
        f"/api/v1/products/{product_id}/images/{image_id}",
        files=[("file", ("new.jpg", io.BytesIO(VALID_JPEG), "image/jpeg"))],
        headers=_auth_header("VENDOR", 20),
    )
    assert cross_replace.status_code == 403

    # Vendor 20 tries to delete
    cross_delete = client.delete(
        f"/api/v1/products/{product_id}/images/{image_id}",
        headers=_auth_header("VENDOR", 20),
    )
    assert cross_delete.status_code == 403


def test_admin_cannot_manage_images_for_vendor_owned_product():
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    response = client.post(
        f"/api/v1/products/{product_id}/images",
        files=[("files", ("tomato.jpg", io.BytesIO(VALID_JPEG), "image/jpeg"))],
        headers=_auth_header("ADMIN", 1),
    )

    assert response.status_code == 403
    assert "own" in response.json()["detail"]


def test_delete_image_and_disk_cleanup():
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    files = [
        ("files", ("first.jpg", io.BytesIO(VALID_JPEG), "image/jpeg")),
        ("files", ("second.png", io.BytesIO(VALID_PNG), "image/png")),
    ]
    upload_res = client.post(
        f"/api/v1/products/{product_id}/images",
        files=files,
        headers=_auth_header("VENDOR", 10),
    )
    assert upload_res.status_code == 201
    img1, img2 = upload_res.json()

    upload_dir = get_upload_dir()
    file1_path = upload_dir / img1["filename"]
    assert file1_path.is_file()

    # Delete primary image (img1)
    del_res = client.delete(
        f"/api/v1/products/{product_id}/images/{img1['id']}",
        headers=_auth_header("VENDOR", 10),
    )
    assert del_res.status_code == 200
    assert not file1_path.is_file()

    # Verify img2 automatically became primary and product.image_url updated
    detail = client.get(f"/api/v1/products/{product_id}", headers=_auth_header("VENDOR", 10))
    prod_data = detail.json()
    assert prod_data["image_url"] == img2["url"]
    assert len(prod_data["images"]) == 1
    assert prod_data["images"][0]["id"] == img2["id"]
    assert prod_data["images"][0]["is_primary"] is True


def test_replace_image():
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")
    files = [("files", ("initial.jpg", io.BytesIO(VALID_JPEG), "image/jpeg"))]
    upload_res = client.post(
        f"/api/v1/products/{product_id}/images",
        files=files,
        headers=_auth_header("VENDOR", 10),
    )
    img = upload_res.json()[0]
    upload_dir = get_upload_dir()
    old_file_path = upload_dir / img["filename"]
    assert old_file_path.is_file()

    # Replace with PNG
    replace_res = client.put(
        f"/api/v1/products/{product_id}/images/{img['id']}",
        files={"file": ("replaced.png", io.BytesIO(VALID_PNG), "image/png")},
        headers=_auth_header("VENDOR", 10),
    )
    assert replace_res.status_code == 200
    replaced_data = replace_res.json()
    assert replaced_data["id"] == img["id"]
    assert replaced_data["mime_type"] == "image/png"
    assert replaced_data["original_filename"] == "replaced.png"

    # Old file removed, new file exists
    assert not old_file_path.is_file()
    new_file_path = upload_dir / replaced_data["filename"]
    assert new_file_path.is_file()


def test_set_primary_image():
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")
    files = [
        ("files", ("one.jpg", io.BytesIO(VALID_JPEG), "image/jpeg")),
        ("files", ("two.png", io.BytesIO(VALID_PNG), "image/png")),
    ]
    upload_res = client.post(
        f"/api/v1/products/{product_id}/images",
        files=files,
        headers=_auth_header("VENDOR", 10),
    )
    img1, img2 = upload_res.json()
    assert img1["is_primary"] is True
    assert img2["is_primary"] is False

    # Set img2 as primary
    primary_res = client.patch(
        f"/api/v1/products/{product_id}/images/{img2['id']}/primary",
        headers=_auth_header("VENDOR", 10),
    )
    assert primary_res.status_code == 200
    assert primary_res.json()["is_primary"] is True

    # Check images list
    list_res = client.get(f"/api/v1/products/{product_id}/images")
    images = list_res.json()
    img2_updated = next(i for i in images if i["id"] == img2["id"])
    img1_updated = next(i for i in images if i["id"] == img1["id"])
    assert img2_updated["is_primary"] is True
    assert img1_updated["is_primary"] is False


def test_max_image_count_limit():
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    # Upload 10 valid images
    files = [("files", (f"img_{i}.jpg", io.BytesIO(VALID_JPEG), "image/jpeg")) for i in range(10)]
    upload_res = client.post(
        f"/api/v1/products/{product_id}/images",
        files=files,
        headers=_auth_header("VENDOR", 10),
    )
    assert upload_res.status_code == 201
    assert len(upload_res.json()) == 10

    # Attempting 11th image should fail
    extra_file = [("files", ("extra.jpg", io.BytesIO(VALID_JPEG), "image/jpeg"))]
    extra_res = client.post(
        f"/api/v1/products/{product_id}/images",
        files=extra_file,
        headers=_auth_header("VENDOR", 10),
    )
    assert extra_res.status_code == 422
    assert "Cannot exceed" in extra_res.json()["detail"]


def test_image_persistence_and_file_serving():
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")
    files = [("files", ("tomato.jpg", io.BytesIO(VALID_JPEG), "image/jpeg"))]
    upload_res = client.post(
        f"/api/v1/products/{product_id}/images",
        files=files,
        headers=_auth_header("VENDOR", 10),
    )
    img_id = upload_res.json()[0]["id"]

    # Serve image via GET /api/v1/products/images/{img_id}
    img_file_res = client.get(f"/api/v1/products/images/{img_id}")
    assert img_file_res.status_code == 200
    assert img_file_res.content == VALID_JPEG
    assert img_file_res.headers["content-type"] == "image/jpeg"
    assert "public, max-age=" in img_file_res.headers["cache-control"]


def test_approval_workflow_and_customer_catalog_visibility():
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    # Initially product is PENDING
    detail = client.get(f"/api/v1/products/{product_id}", headers=_auth_header("VENDOR", 10))
    assert detail.json()["certification"] == "PENDING"

    # Customer catalog should NOT show unapproved product
    public_catalog = client.get("/api/v1/products/")
    assert not any(p["id"] == product_id for p in public_catalog.json())

    # Vendor uploads images - certification remains PENDING
    files = [("files", ("tomato.jpg", io.BytesIO(VALID_JPEG), "image/jpeg"))]
    upload_res = client.post(
        f"/api/v1/products/{product_id}/images",
        files=files,
        headers=_auth_header("VENDOR", 10),
    )
    assert upload_res.status_code == 201

    detail_after = client.get(f"/api/v1/products/{product_id}", headers=_auth_header("VENDOR", 10))
    assert detail_after.json()["certification"] == "PENDING"
    assert detail_after.json()["seller_id"] == 10

    # Admin approves product
    approve_res = client.post(f"/api/v1/products/{product_id}/approve", headers=_auth_header("ADMIN", 1))
    assert approve_res.status_code == 200
    assert approve_res.json()["certification"] == "APPROVED"

    # Now customer catalog shows product with its uploaded image!
    public_catalog_after = client.get("/api/v1/products/")
    approved_product = next((p for p in public_catalog_after.json() if p["id"] == product_id), None)
    assert approved_product is not None
    assert approved_product["image_url"] is not None
    assert approved_product["image_url"].startswith("/api/v1/products/images/")
    assert len(approved_product["images"]) == 1

    # Vendor edits product -> certification resets to PENDING
    edit_res = client.put(
        f"/api/v1/products/{product_id}",
        json={"name": "Organic Tomatoes Premium", "price": "45.00"},
        headers=_auth_header("VENDOR", 10),
    )
    assert edit_res.status_code == 200
    assert edit_res.json()["certification"] == "PENDING"

    # Customer can no longer see the product while pending re-approval
    public_catalog_recheck = client.get("/api/v1/products/")
    assert not any(p["id"] == product_id for p in public_catalog_recheck.json())


# ===========================================================================
# URL-based image tests
# ===========================================================================

VALID_HTTPS_URL = "https://example.com/images/tomato.jpg"
VALID_HTTP_URL = "http://cdn.example.org/product/img.webp"


def test_add_image_url_valid_https():
    """Vendor can add a valid HTTPS image URL and it becomes primary (first image)."""
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    res = client.post(
        f"/api/v1/products/{product_id}/images/url",
        json={"external_url": VALID_HTTPS_URL, "url_label": "Main tomato"},
        headers=_auth_header("VENDOR", 10),
    )
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["image_type"] == "URL"
    assert data["external_url"] == VALID_HTTPS_URL
    assert data["url_label"] == "Main tomato"
    assert data["url"] == VALID_HTTPS_URL        # .url property returns external_url for URL-type
    assert data["is_primary"] is True            # first image on product -> primary
    assert data["filename"] is None              # no uploaded file
    assert data["file_size"] is None


def test_admin_category_image_upload_url_and_vendor_authorization():
    category = client.post(
        "/api/v1/categories/",
        json={"name": "Image managed category"},
        headers=_auth_header("ADMIN", 1),
    ).json()
    category_id = category["id"]

    forbidden = client.post(
        f"/api/v1/categories/{category_id}/image",
        files={"file": ("category.jpg", io.BytesIO(VALID_JPEG), "image/jpeg")},
        headers=_auth_header("VENDOR", 10),
    )
    assert forbidden.status_code == 403

    uploaded = client.post(
        f"/api/v1/categories/{category_id}/image",
        files={"file": ("category.jpg", io.BytesIO(VALID_JPEG), "image/jpeg")},
        headers=_auth_header("ADMIN", 1),
    )
    assert uploaded.status_code == 200, uploaded.text
    assert uploaded.json()["image_source"] == "UPLOAD"
    assert uploaded.json()["image_url"] == f"/api/v1/categories/images/{category_id}"

    served = client.get(f"/api/v1/categories/images/{category_id}")
    assert served.status_code == 200
    assert served.content == VALID_JPEG

    external = client.put(
        f"/api/v1/categories/{category_id}/image/url",
        json={"external_url": VALID_HTTPS_URL},
        headers=_auth_header("ADMIN", 1),
    )
    assert external.status_code == 200, external.text
    assert external.json()["image_source"] == "URL"
    assert external.json()["image_url"] == VALID_HTTPS_URL

    removed = client.delete(f"/api/v1/categories/{category_id}/image", headers=_auth_header("ADMIN", 1))
    assert removed.status_code == 200
    assert removed.json()["image_url"] is None


def test_add_image_url_valid_http():
    """HTTP (non-HTTPS) URLs are also accepted."""
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    res = client.post(
        f"/api/v1/products/{product_id}/images/url",
        json={"external_url": VALID_HTTP_URL},
        headers=_auth_header("VENDOR", 10),
    )
    assert res.status_code == 201, res.text
    assert res.json()["external_url"] == VALID_HTTP_URL


def test_add_image_url_empty_rejected():
    """An empty (whitespace-only) URL string must be rejected at schema or service level."""
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    res = client.post(
        f"/api/v1/products/{product_id}/images/url",
        json={"external_url": "   "},
        headers=_auth_header("VENDOR", 10),
    )
    # Pydantic min_length=1 rejects whitespace-only at the schema layer (422),
    # or the service _validate_external_url raises 422 after stripping.
    assert res.status_code in {422, 400}, res.text


def test_add_image_url_unsafe_scheme_rejected():
    """javascript:, file:, ftp: and similar schemes must be rejected."""
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    for bad_url in [
        "javascript:alert(1)",
        "file:///etc/passwd",
        "ftp://files.example.com/img.jpg",
        "data:image/png;base64,abc",
    ]:
        res = client.post(
            f"/api/v1/products/{product_id}/images/url",
            json={"external_url": bad_url},
            headers=_auth_header("VENDOR", 10),
        )
        assert res.status_code == 422, (
            f"Expected rejection for {bad_url!r}, got {res.status_code}: {res.text}"
        )


def test_add_image_url_private_address_rejected():
    """URLs pointing to localhost or private ranges must be blocked (SSRF guard)."""
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    for private_url in [
        "http://localhost/img.jpg",
        "http://127.0.0.1/secret.png",
        "http://192.168.1.1/admin.jpg",
        "http://10.0.0.1/internal.webp",
        "http://169.254.169.254/latest/meta-data/",
    ]:
        res = client.post(
            f"/api/v1/products/{product_id}/images/url",
            json={"external_url": private_url},
            headers=_auth_header("VENDOR", 10),
        )
        assert res.status_code == 422, (
            f"Expected rejection for {private_url!r}, got {res.status_code}: {res.text}"
        )


def test_add_image_url_too_long_rejected():
    """URLs longer than 2048 characters must be rejected."""
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    long_url = "https://example.com/" + "a" * 2040
    res = client.post(
        f"/api/v1/products/{product_id}/images/url",
        json={"external_url": long_url},
        headers=_auth_header("VENDOR", 10),
    )
    assert res.status_code == 422, res.text


def test_add_image_url_unauthorized_rejected():
    """Unauthenticated requests must be rejected with 401/403."""
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    res = client.post(
        f"/api/v1/products/{product_id}/images/url",
        json={"external_url": VALID_HTTPS_URL},
    )
    assert res.status_code in {401, 403}


def test_add_image_url_cross_vendor_rejected():
    """A vendor cannot add URL images to another vendor's product."""
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    res = client.post(
        f"/api/v1/products/{product_id}/images/url",
        json={"external_url": VALID_HTTPS_URL},
        headers=_auth_header("VENDOR", 99),   # different vendor
    )
    assert res.status_code == 403


def test_add_image_url_second_not_primary():
    """The second URL image added should NOT become primary."""
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    r1 = client.post(
        f"/api/v1/products/{product_id}/images/url",
        json={"external_url": VALID_HTTPS_URL},
        headers=_auth_header("VENDOR", 10),
    )
    assert r1.status_code == 201
    assert r1.json()["is_primary"] is True

    r2 = client.post(
        f"/api/v1/products/{product_id}/images/url",
        json={"external_url": VALID_HTTP_URL},
        headers=_auth_header("VENDOR", 10),
    )
    assert r2.status_code == 201
    assert r2.json()["is_primary"] is False


def test_mixed_file_and_url_images():
    """A product may have both uploaded files and URL-based images simultaneously."""
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    # Upload a file first (becomes primary)
    file_res = client.post(
        f"/api/v1/products/{product_id}/images",
        files=[("files", ("tomato.jpg", io.BytesIO(VALID_JPEG), "image/jpeg"))],
        headers=_auth_header("VENDOR", 10),
    )
    assert file_res.status_code == 201

    # Add a URL image (not primary, since one already exists)
    url_res = client.post(
        f"/api/v1/products/{product_id}/images/url",
        json={"external_url": VALID_HTTPS_URL},
        headers=_auth_header("VENDOR", 10),
    )
    assert url_res.status_code == 201

    # Fetch the image list — should contain both types
    list_res = client.get(f"/api/v1/products/{product_id}/images")
    assert list_res.status_code == 200
    images = list_res.json()
    assert len(images) == 2
    types = {img["image_type"] for img in images}
    assert types == {"UPLOAD", "URL"}


def test_delete_url_image_no_disk_remnant():
    """Deleting a URL-type image succeeds without disk-cleanup errors."""
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    add_res = client.post(
        f"/api/v1/products/{product_id}/images/url",
        json={"external_url": VALID_HTTPS_URL},
        headers=_auth_header("VENDOR", 10),
    )
    assert add_res.status_code == 201
    image_id = add_res.json()["id"]

    del_res = client.delete(
        f"/api/v1/products/{product_id}/images/{image_id}",
        headers=_auth_header("VENDOR", 10),
    )
    assert del_res.status_code == 200

    # Image should no longer appear in the list
    list_res = client.get(f"/api/v1/products/{product_id}/images")
    assert list_res.status_code == 200
    assert not any(img["id"] == image_id for img in list_res.json())


def test_url_image_max_count_limit():
    """Cannot exceed MAX_IMAGES_PER_PRODUCT using URL-based images."""
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")
    max_count = settings.MAX_IMAGES_PER_PRODUCT

    for i in range(max_count):
        r = client.post(
            f"/api/v1/products/{product_id}/images/url",
            json={"external_url": f"https://example.com/img{i}.jpg"},
            headers=_auth_header("VENDOR", 10),
        )
        assert r.status_code == 201, f"Failed at image {i}: {r.text}"

    over_limit = client.post(
        f"/api/v1/products/{product_id}/images/url",
        json={"external_url": "https://example.com/overflow.jpg"},
        headers=_auth_header("VENDOR", 10),
    )
    assert over_limit.status_code == 422


def test_set_primary_on_url_image():
    """Promoting a URL image to primary updates the product's image_url to the external URL."""
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    # First image (URL) is auto-primary
    r1 = client.post(
        f"/api/v1/products/{product_id}/images/url",
        json={"external_url": VALID_HTTPS_URL},
        headers=_auth_header("VENDOR", 10),
    )
    assert r1.status_code == 201
    id1 = r1.json()["id"]  # noqa: F841 - kept for clarity

    # Second URL image
    r2 = client.post(
        f"/api/v1/products/{product_id}/images/url",
        json={"external_url": VALID_HTTP_URL},
        headers=_auth_header("VENDOR", 10),
    )
    assert r2.status_code == 201
    id2 = r2.json()["id"]

    # Promote second image to primary
    patch_res = client.patch(
        f"/api/v1/products/{product_id}/images/{id2}/primary",
        headers=_auth_header("VENDOR", 10),
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["is_primary"] is True
    assert patch_res.json()["url"] == VALID_HTTP_URL

    # Product's image_url should now reflect the new primary's external URL
    prod = client.get(f"/api/v1/products/{product_id}", headers=_auth_header("VENDOR", 10))
    assert prod.json()["image_url"] == VALID_HTTP_URL


def test_image_url_no_hostname_rejected():
    """URLs without a hostname (e.g. bare paths) must be rejected."""
    _, product_id = _create_category_and_product(seller_id=10, role="VENDOR")

    res = client.post(
        f"/api/v1/products/{product_id}/images/url",
        json={"external_url": "https:///no-host.jpg"},
        headers=_auth_header("VENDOR", 10),
    )
    assert res.status_code == 422, res.text
