from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import status
from fastapi.testclient import TestClient
from jose import jwt
import pytest

from app.config import settings
from app.main import app
from app.rag.embeddings import LocalEmbeddingService
from app.rag.ingestion import ingest_customer_knowledge_base
from app.rag.retriever import RAGRetriever
from app.rag.vector_store import LocalVectorStore

client = TestClient(app)


def create_token(role: str = "CUSTOMER", user_id: int = 1) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def test_ai_health_endpoint():
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["service"] == "ai-service"
    assert data["status"] == "healthy"
    assert data["port"] == 8002


def test_rag_embedding_and_similarity():
    service = LocalEmbeddingService()
    docs = [
        "Organic produce is grown without synthetic chemical pesticides.",
        "Quick commerce delivers groceries in 10 minutes.",
    ]
    service.fit(docs)

    vec1 = service.embed_text("organic pesticide free")
    vec2 = service.embed_text("quick delivery 10 minutes")

    assert len(vec1) > 0
    assert len(vec2) > 0

    sim1 = LocalEmbeddingService.cosine_similarity(vec1, service.embed_text("organic farming"))
    sim2 = LocalEmbeddingService.cosine_similarity(vec1, service.embed_text("car engine oil"))

    assert sim1 > sim2


def test_vector_store_and_retriever(tmp_path):
    store_file = tmp_path / "test_vector_store.json"
    vector_store = LocalVectorStore(store_file)
    vector_store.fit_and_add_documents([
        {
            "id": "1",
            "source": "test_faq.md",
            "title": "FAQ",
            "content": "OrganicKart provides 100% certified organic fruits and vegetables.",
        },
        {
            "id": "2",
            "source": "test_policy.md",
            "title": "Policy",
            "content": "Returns are accepted within 24 hours of delivery.",
        },
    ])
    vector_store.save()

    retriever = RAGRetriever(vector_store_path=store_file)
    results = retriever.retrieve("certified organic fruits")

    assert len(results["sources"]) > 0
    assert "OrganicKart" in results["context"]


def test_chat_unauthenticated_fails():
    # FastAPI HTTPBearer returns 403 when no Authorization header is present.
    # (Starlette raises 403 for missing Bearer, not 401.)
    response = client.post("/api/v1/ai/chat", json={"message": "What is organic?"})
    assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


def test_chat_unauthorized_role_forbidden():
    token = create_token(role="VENDOR", user_id=10)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/ai/chat", json={"message": "What is organic?"}, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_customer_chat_success(monkeypatch):
    # Enable MOCK_LLM mode for fast automated API test
    monkeypatch.setattr(settings, "MOCK_LLM", True)

    token = create_token(role="CUSTOMER", user_id=1)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "What are the benefits of organic vegetables?"},
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "answer" in data
    assert isinstance(data["sources"], list)
    assert len(data["answer"]) > 0


def test_admin_chat_allows_admin_and_returns_rag_response(monkeypatch):
    monkeypatch.setattr(settings, "MOCK_LLM", True)
    token = create_token(role="ADMIN", user_id=99)

    response = client.post(
        "/api/v1/ai/admin/chat",
        json={"message": "Who can approve product certification?"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "answer" in data
    assert isinstance(data["sources"], list)
    assert data["sources"]


@pytest.mark.parametrize("role", ["CUSTOMER", "VENDOR", "FARMER"])
def test_admin_chat_rejects_non_admin_roles(role):
    token = create_token(role=role, user_id=1)

    response = client.post(
        "/api/v1/ai/admin/chat",
        json={"message": "Who can approve product certification?"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_chat_rejects_unauthenticated_request():
    response = client.post("/api/v1/ai/admin/chat", json={"message": "Who can approve product certification?"})

    assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


def test_admin_pending_certification_request_uses_live_tool(monkeypatch):
    from app.api.v1.admin_chat import admin_agent

    class PendingProductClient:
        async def get_pending_certification_products(self, token):
            return {
                "success": True,
                "total": 1,
                "products": [{
                    "id": 50,
                    "name": "Organic Apples",
                    "seller_id": 9,
                    "certification": "PENDING",
                    "is_active": True,
                    "price": "100.00",
                    "unit": "kg",
                    "stock_quantity": 12,
                }],
            }

    monkeypatch.setattr(admin_agent, "product_client", PendingProductClient())
    token = create_token(role="ADMIN", user_id=99)
    response = client.post(
        "/api/v1/ai/admin/chat",
        json={"message": "Show pending certifications"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert "Active pending products: 1" in response.json()["answer"]


def test_admin_order_statistics_request_uses_live_order_tool(monkeypatch):
    from app.api.v1.admin_chat import admin_agent

    class AdminOrderClient:
        async def get_order_analytics(self, token):
            return {
                "success": True,
                "analytics": {
                    "total_orders": 1,
                    "orders_by_status": {"CONFIRMED": 1},
                    "payment_status_breakdown": {"PAID": 1},
                    "cancelled_orders": 0,
                    "total_revenue": "20.00",
                    "monthly_sales_summary": [],
                    "recent_orders": [],
                },
            }

    monkeypatch.setattr(admin_agent, "order_client", AdminOrderClient())
    token = create_token(role="ADMIN", user_id=99)
    response = client.post(
        "/api/v1/ai/admin/chat",
        json={"message": "Show order statistics"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert "Total orders: 1" in response.json()["answer"]


def test_admin_vendor_sales_request_uses_live_business_insights_tool(monkeypatch):
    from app.api.v1.admin_chat import admin_agent

    class AdminOrderClient:
        async def get_business_insights(self, token):
            return {
                "success": True,
                "insights": {
                    "vendor_sales": [{"seller_id": 9, "orders_count": 2, "units_sold": 7, "revenue": "120.00"}],
                    "product_sales": [],
                    "current_period": "2026-10",
                    "previous_period": "2026-09",
                    "sales_decline_available": False,
                    "sales_declines": [],
                },
            }

    monkeypatch.setattr(admin_agent, "order_client", AdminOrderClient())
    token = create_token(role="ADMIN", user_id=99)
    response = client.post(
        "/api/v1/ai/admin/chat",
        json={"message": "Show vendor sales"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert "Seller #9" in response.json()["answer"]
