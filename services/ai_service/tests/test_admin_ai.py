import asyncio

import httpx
import pytest

from app.agents.admin_agent import AdminAgent
from app.tools.admin_order_tools import AdminOrderServiceClient
from app.tools.product_tools import ProductServiceClient


class FakeRetriever:
    def retrieve(self, query):
        return {"context": "Admin static guidance.", "sources": [{"document": "admin.md", "title": "Admin", "score": 1.0}]}


class FakeLLM:
    def __init__(self):
        self.calls = 0

    async def generate(self, prompt, system_prompt=None):
        self.calls += 1
        return "Admin RAG answer"


class FakeAdminProductClient:
    def __init__(self, error=None):
        self.error = error
        self.catalog_calls = []
        self.detail_calls = []

    async def get_admin_products(self, token, certification=None, search=None):
        self.catalog_calls.append((token, certification, search))
        if self.error:
            return {"success": False, "error": self.error, "detail": f"Product Service {self.error}."}
        totals = {"PENDING": 2, "APPROVED": 5, "REJECTED": 1}
        return {
            "success": True,
            "total": totals[certification],
            "products": [{
                "id": 10,
                "name": f"{certification.title()} Product",
                "seller_id": 7,
                "certification": certification,
                "is_active": True,
                "price": "95.00",
                "unit": "kg",
                "stock_quantity": 4,
                "category": {"name": "Fruits"},
            }],
        }

    async def get_pending_certification_products(self, token):
        return await self.get_admin_products(token, certification="PENDING")

    async def get_admin_product(self, product_id, token):
        self.detail_calls.append((product_id, token))
        if self.error:
            return {"success": False, "error": self.error, "detail": f"Product Service {self.error}."}
        return {
            "success": True,
            "product": {
                "id": product_id,
                "name": "Hidden Product",
                "certification": "PENDING",
                "is_active": False,
                "price": "95.00",
                "unit": "kg",
                "stock_quantity": 4,
                "seller_id": 7,
            },
        }

    async def get_admin_low_stock_products(self, token):
        return {
            "success": True,
            "threshold": 10,
            "products": [{
                "id": 50,
                "name": "Low Spinach",
                "seller_id": 7,
                "certification": "APPROVED",
                "is_active": True,
                "stock_quantity": 4,
                "unit": "bunch",
            }],
        }


class FakeAdminOrderClient:
    def __init__(self, result=None):
        self.calls = []
        self.result = result or {
            "success": True,
            "analytics": {
                "total_orders": 3,
                "orders_by_status": {"CONFIRMED": 1, "CANCELLED": 1, "PAYMENT_PENDING": 1},
                "payment_status_breakdown": {"PAID": 2, "PAYMENT_PENDING": 1},
                "cancelled_orders": 1,
                "total_revenue": "100.00",
                "monthly_sales_summary": [{"month": "2026-10", "orders": 1, "revenue": "100.00"}],
                "recent_orders": [{
                    "order_id": 11,
                    "created_at": "2026-10-01T00:00:00",
                    "status": "CONFIRMED",
                    "payment_status": "PAID",
                    "items_count": 2,
                    "total_amount": "100.00",
                }],
            },
        }

    async def get_order_analytics(self, token):
        self.calls.append(token)
        return self.result

    async def get_business_insights(self, token):
        self.calls.append(token)
        return {
            "success": True,
            "insights": {
                "vendor_sales": [{"seller_id": 12, "orders_count": 4, "units_sold": 20, "revenue": "450.00"}],
                "product_sales": [{"product_id": 21, "product_name": "Organic Apples", "units_sold": 12, "revenue": "240.00"}],
                "current_period": "2026-10",
                "previous_period": "2026-09",
                "sales_decline_available": True,
                "sales_declines": [{
                    "product_id": 31,
                    "product_name": "Organic Spinach",
                    "current_period_quantity": 5,
                    "previous_period_quantity": 10,
                    "percentage_change": "-50.00",
                }],
            },
        }


def run(coro):
    return asyncio.run(coro)


def test_admin_catalog_summary_uses_read_only_product_counts_without_llm():
    client = FakeAdminProductClient()
    llm = FakeLLM()
    agent = AdminAgent(retriever=FakeRetriever(), llm_service=llm, product_client=client)

    response = run(agent.handle_query("Show the product catalog summary", token="admin-jwt"))

    assert "Total active products: 8" in response["answer"]
    assert "PENDING: 2" in response["answer"]
    assert client.catalog_calls == [
        ("admin-jwt", "PENDING", None),
        ("admin-jwt", "APPROVED", None),
        ("admin-jwt", "REJECTED", None),
    ]
    assert llm.calls == 0


def test_admin_certification_query_uses_live_catalog_without_llm():
    client = FakeAdminProductClient()
    llm = FakeLLM()
    agent = AdminAgent(retriever=FakeRetriever(), llm_service=llm, product_client=client)

    response = run(agent.handle_query("Show pending products", token="admin-jwt"))

    assert "Active pending products: 2" in response["answer"]
    assert client.catalog_calls == [("admin-jwt", "PENDING", None)]
    assert llm.calls == 0


@pytest.mark.parametrize("question", [
    "Show pending certifications",
    "Which products are waiting for approval?",
    "How many products are pending certification?",
    "Show pending products",
    "Give me the pending certification list",
    "Which products need admin review?",
])
def test_pending_certification_questions_use_dedicated_live_tool_without_llm(question):
    client = FakeAdminProductClient()
    llm = FakeLLM()
    agent = AdminAgent(retriever=FakeRetriever(), llm_service=llm, product_client=client)

    response = run(agent.handle_query(question, token="admin-jwt"))

    assert "Active pending products: 2" in response["answer"]
    assert "Product #10: Pending Product" in response["answer"]
    assert "Seller ID: 7" in response["answer"]
    assert "Category: Fruits" in response["answer"]
    assert client.catalog_calls == [("admin-jwt", "PENDING", None)]
    assert llm.calls == 0


def test_pending_certification_empty_queue_is_handled_cleanly():
    class EmptyPendingClient(FakeAdminProductClient):
        async def get_pending_certification_products(self, token):
            self.catalog_calls.append((token, "PENDING", None))
            return {"success": True, "total": 0, "products": []}

    client = EmptyPendingClient()
    agent = AdminAgent(retriever=FakeRetriever(), llm_service=FakeLLM(), product_client=client)

    response = run(agent.handle_query("Show pending certifications", token="admin-jwt"))

    assert response["answer"] == "There are no active products pending certification review."


@pytest.mark.parametrize("error", ["timeout", "unavailable"])
def test_pending_certification_service_failures_are_returned_safely(error):
    class FailingPendingClient(FakeAdminProductClient):
        async def get_pending_certification_products(self, token):
            return {"success": False, "error": error, "detail": f"Product Service {error}."}

    agent = AdminAgent(retriever=FakeRetriever(), llm_service=FakeLLM(), product_client=FailingPendingClient())

    response = run(agent.handle_query("Which products need admin review?", token="admin-jwt"))

    assert response["answer"] == f"Product Service {error}."


def test_admin_product_detail_uses_live_product_without_llm():
    client = FakeAdminProductClient()
    llm = FakeLLM()
    agent = AdminAgent(retriever=FakeRetriever(), llm_service=llm, product_client=client)

    response = run(agent.handle_query("Show product ID 42", token="admin-jwt"))

    assert "Product #42: Hidden Product" in response["answer"]
    assert "Active: No" in response["answer"]
    assert client.detail_calls == [(42, "admin-jwt")]
    assert llm.calls == 0


def test_admin_catalog_failure_is_returned_safely():
    agent = AdminAgent(retriever=FakeRetriever(), llm_service=FakeLLM(), product_client=FakeAdminProductClient(error="unavailable"))

    response = run(agent.handle_query("total products", token="admin-jwt"))

    assert response["answer"] == "Product Service unavailable."


def test_admin_rag_fallback_remains_available_for_non_catalog_question():
    llm = FakeLLM()
    client = FakeAdminProductClient()
    agent = AdminAgent(retriever=FakeRetriever(), llm_service=llm, product_client=client)

    response = run(agent.handle_query("Explain the certification process", token="admin-jwt"))

    assert response["answer"] == "Admin RAG answer"
    assert client.catalog_calls == []
    assert llm.calls == 1


def test_admin_order_statistics_uses_live_order_service_without_llm():
    order_client = FakeAdminOrderClient()
    llm = FakeLLM()
    agent = AdminAgent(
        retriever=FakeRetriever(), llm_service=llm, product_client=FakeAdminProductClient(), order_client=order_client
    )

    response = run(agent.handle_query("Show order statistics", token="admin-jwt"))

    assert "Total orders: 3" in response["answer"]
    assert "CANCELLED: 1" in response["answer"]
    assert order_client.calls == ["admin-jwt"]
    assert llm.calls == 0


def test_admin_sales_analytics_uses_authoritative_server_value_without_llm():
    order_client = FakeAdminOrderClient()
    llm = FakeLLM()
    agent = AdminAgent(
        retriever=FakeRetriever(), llm_service=llm, product_client=FakeAdminProductClient(), order_client=order_client
    )

    response = run(agent.handle_query("What is our monthly sales revenue?", token="admin-jwt"))

    assert "Paid, non-cancelled revenue: ₹100.00" in response["answer"]
    assert "2026-10: 1 orders, ₹100.00" in response["answer"]
    assert order_client.calls == ["admin-jwt"]
    assert llm.calls == 0


def test_admin_recent_orders_exposes_only_safe_summary_fields_without_llm():
    order_client = FakeAdminOrderClient()
    llm = FakeLLM()
    agent = AdminAgent(
        retriever=FakeRetriever(), llm_service=llm, product_client=FakeAdminProductClient(), order_client=order_client
    )

    response = run(agent.handle_query("Show recent orders", token="admin-jwt"))

    assert "Order #11" in response["answer"]
    assert "Payment: PAID" in response["answer"]
    assert "₹100.00" in response["answer"]
    assert order_client.calls == ["admin-jwt"]
    assert llm.calls == 0


@pytest.mark.parametrize("error", ["timeout", "unavailable", "invalid_response"])
def test_admin_order_analytics_failures_are_returned_without_hallucinating(error):
    order_client = FakeAdminOrderClient({"success": False, "error": error, "detail": f"Order Service {error}."})
    agent = AdminAgent(
        retriever=FakeRetriever(), llm_service=FakeLLM(), product_client=FakeAdminProductClient(), order_client=order_client
    )

    response = run(agent.handle_query("How many orders do we have?", token="admin-jwt"))

    assert response["answer"] == f"Order Service {error}."


def test_admin_empty_order_analytics_is_handled_cleanly():
    order_client = FakeAdminOrderClient({
        "success": True,
        "analytics": {
            "total_orders": 0,
            "orders_by_status": {},
            "payment_status_breakdown": {},
            "cancelled_orders": 0,
            "total_revenue": "0.00",
            "monthly_sales_summary": [],
            "recent_orders": [],
        },
    })
    agent = AdminAgent(
        retriever=FakeRetriever(), llm_service=FakeLLM(), product_client=FakeAdminProductClient(), order_client=order_client
    )

    response = run(agent.handle_query("How many orders do we have?", token="admin-jwt"))

    assert response["answer"] == "No orders are available yet."


def test_admin_order_policy_question_remains_rag_not_live_analytics():
    order_client = FakeAdminOrderClient()
    llm = FakeLLM()
    agent = AdminAgent(
        retriever=FakeRetriever(), llm_service=llm, product_client=FakeAdminProductClient(), order_client=order_client
    )

    response = run(agent.handle_query("What is the order cancellation policy?", token="admin-jwt"))

    assert response["answer"] == "Admin RAG answer"
    assert order_client.calls == []
    assert llm.calls == 1


@pytest.mark.parametrize("question", [
    "Who are the highest selling vendors?",
    "Show vendor sales",
    "Compare vendor performance",
])
def test_admin_vendor_sales_questions_use_live_order_business_insights_without_llm(question):
    order_client = FakeAdminOrderClient()
    llm = FakeLLM()
    agent = AdminAgent(retriever=FakeRetriever(), llm_service=llm, product_client=FakeAdminProductClient(), order_client=order_client)

    response = run(agent.handle_query(question, token="admin-jwt"))

    assert "Seller #12" in response["answer"]
    assert "₹450.00" in response["answer"]
    assert order_client.calls == ["admin-jwt"]
    assert llm.calls == 0


def test_admin_product_sales_questions_use_live_order_business_insights_without_llm():
    order_client = FakeAdminOrderClient()
    llm = FakeLLM()
    agent = AdminAgent(retriever=FakeRetriever(), llm_service=llm, product_client=FakeAdminProductClient(), order_client=order_client)

    response = run(agent.handle_query("Which products sell the most?", token="admin-jwt"))

    assert "Product #21" in response["answer"]
    assert "12 units" in response["answer"]
    assert order_client.calls == ["admin-jwt"]
    assert llm.calls == 0


def test_admin_low_stock_uses_live_product_service_without_llm():
    client = FakeAdminProductClient()
    llm = FakeLLM()
    agent = AdminAgent(retriever=FakeRetriever(), llm_service=llm, product_client=client, order_client=FakeAdminOrderClient())

    response = run(agent.handle_query("Show low stock products", token="admin-jwt"))

    assert "Low Spinach" in response["answer"]
    assert "Stock: 4 bunch" in response["answer"]
    assert llm.calls == 0


def test_admin_sales_decline_uses_server_comparison_without_llm():
    order_client = FakeAdminOrderClient()
    llm = FakeLLM()
    agent = AdminAgent(retriever=FakeRetriever(), llm_service=llm, product_client=FakeAdminProductClient(), order_client=order_client)

    response = run(agent.handle_query("Which products have declining sales?", token="admin-jwt"))

    assert "Organic Spinach" in response["answer"]
    assert "10 → 5 units (-50.00%)" in response["answer"]
    assert order_client.calls == ["admin-jwt"]
    assert llm.calls == 0


def test_admin_sales_decline_reports_insufficient_history_without_hallucinating():
    class NoHistoryOrderClient(FakeAdminOrderClient):
        async def get_business_insights(self, token):
            self.calls.append(token)
            result = await super().get_business_insights(token)
            result["insights"]["sales_decline_available"] = False
            result["insights"]["sales_declines"] = []
            return result

    order_client = NoHistoryOrderClient()
    agent = AdminAgent(retriever=FakeRetriever(), llm_service=FakeLLM(), product_client=FakeAdminProductClient(), order_client=order_client)

    response = run(agent.handle_query("sales declining", token="admin-jwt"))

    assert "insufficient paid order history" in response["answer"]


@pytest.mark.parametrize("intent_question, client_kind", [
    ("Show vendor sales", "order"),
    ("Show low stock products", "product"),
])
def test_admin_business_insight_service_failures_are_returned_safely(intent_question, client_kind):
    class FailingOrderClient(FakeAdminOrderClient):
        async def get_business_insights(self, token):
            return {"success": False, "error": "timeout", "detail": "Order Service timed out."}

    class FailingProductClient(FakeAdminProductClient):
        async def get_admin_low_stock_products(self, token):
            return {"success": False, "error": "unavailable", "detail": "Product Service unavailable."}

    agent = AdminAgent(
        retriever=FakeRetriever(),
        llm_service=FakeLLM(),
        product_client=FailingProductClient() if client_kind == "product" else FakeAdminProductClient(),
        order_client=FailingOrderClient() if client_kind == "order" else FakeAdminOrderClient(),
    )
    response = run(agent.handle_query(intent_question, token="admin-jwt"))

    assert response["answer"] in {"Order Service timed out.", "Product Service unavailable."}


def test_admin_static_vendor_guidelines_remain_rag():
    order_client = FakeAdminOrderClient()
    llm = FakeLLM()
    agent = AdminAgent(retriever=FakeRetriever(), llm_service=llm, product_client=FakeAdminProductClient(), order_client=order_client)

    response = run(agent.handle_query("What are the vendor guidelines?", token="admin-jwt"))

    assert response["answer"] == "Admin RAG answer"
    assert order_client.calls == []
    assert llm.calls == 1


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class RecordingClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.response


def test_admin_catalog_client_forwards_jwt_and_uses_read_only_get(monkeypatch):
    transport = RecordingClient(FakeResponse(200, {"items": [{"id": 1}], "total": 1, "page": 1, "page_size": 100}))
    monkeypatch.setattr("app.tools.product_tools.httpx.AsyncClient", lambda **kwargs: transport)

    result = run(ProductServiceClient(base_url="http://product-service").get_admin_products("admin-jwt", certification="PENDING"))

    assert result == {"success": True, "products": [{"id": 1}], "total": 1}
    assert transport.calls == [
        (
            "http://product-service/api/v1/products/",
            {"headers": {"Authorization": "Bearer admin-jwt"}, "params": {"page": 1, "page_size": 100, "certification": "PENDING"}},
        )
    ]


def test_admin_order_analytics_client_forwards_jwt_to_read_only_endpoint(monkeypatch):
    payload = {
        "total_orders": 0,
        "orders_by_status": {},
        "payment_status_breakdown": {},
        "cancelled_orders": 0,
        "total_revenue": "0.00",
        "monthly_sales_summary": [],
        "recent_orders": [],
    }
    transport = RecordingClient(FakeResponse(200, payload))
    monkeypatch.setattr("app.tools.admin_order_tools.httpx.AsyncClient", lambda **kwargs: transport)

    result = run(AdminOrderServiceClient(base_url="http://order-service").get_order_analytics("admin-jwt"))

    assert result == {"success": True, "analytics": payload}
    assert transport.calls == [
        (
            "http://order-service/api/v1/orders/admin/analytics",
            {"headers": {"Authorization": "Bearer admin-jwt"}},
        )
    ]


def test_admin_order_analytics_client_rejects_malformed_response(monkeypatch):
    transport = RecordingClient(FakeResponse(200, {"total_orders": "3"}))
    monkeypatch.setattr("app.tools.admin_order_tools.httpx.AsyncClient", lambda **kwargs: transport)

    result = run(AdminOrderServiceClient(base_url="http://order-service").get_order_analytics("admin-jwt"))

    assert result["success"] is False
    assert result["error"] == "invalid_response"


def test_admin_order_analytics_client_rejects_incomplete_response(monkeypatch):
    transport = RecordingClient(FakeResponse(200, {"total_orders": 3}))
    monkeypatch.setattr("app.tools.admin_order_tools.httpx.AsyncClient", lambda **kwargs: transport)

    result = run(AdminOrderServiceClient(base_url="http://order-service").get_order_analytics("admin-jwt"))

    assert result["success"] is False
    assert result["error"] == "invalid_response"


def test_admin_business_insights_client_forwards_jwt_and_rejects_malformed_response(monkeypatch):
    payload = {
        "vendor_sales": [],
        "product_sales": [],
        "current_period": "2026-10",
        "previous_period": "2026-09",
        "sales_decline_available": False,
        "sales_declines": [],
    }
    transport = RecordingClient(FakeResponse(200, payload))
    monkeypatch.setattr("app.tools.admin_order_tools.httpx.AsyncClient", lambda **kwargs: transport)

    result = run(AdminOrderServiceClient(base_url="http://order-service").get_business_insights("admin-jwt"))

    assert result == {"success": True, "insights": payload}
    assert transport.calls == [
        (
            "http://order-service/api/v1/orders/admin/business-insights",
            {"headers": {"Authorization": "Bearer admin-jwt"}},
        )
    ]

    malformed_transport = RecordingClient(FakeResponse(200, {"vendor_sales": []}))
    monkeypatch.setattr("app.tools.admin_order_tools.httpx.AsyncClient", lambda **kwargs: malformed_transport)
    malformed = run(AdminOrderServiceClient(base_url="http://order-service").get_business_insights("admin-jwt"))
    assert malformed["success"] is False
    assert malformed["error"] == "invalid_response"


def test_admin_low_stock_client_forwards_jwt_and_rejects_malformed_response(monkeypatch):
    payload = {"threshold": 10, "items": []}
    transport = RecordingClient(FakeResponse(200, payload))
    monkeypatch.setattr("app.tools.product_tools.httpx.AsyncClient", lambda **kwargs: transport)

    result = run(ProductServiceClient(base_url="http://product-service").get_admin_low_stock_products("admin-jwt"))

    assert result == {"success": True, "threshold": 10, "products": []}
    assert transport.calls == [
        (
            "http://product-service/api/v1/products/admin/low-stock",
            {"headers": {"Authorization": "Bearer admin-jwt"}},
        )
    ]

    malformed_transport = RecordingClient(FakeResponse(200, {"threshold": "10", "items": []}))
    monkeypatch.setattr("app.tools.product_tools.httpx.AsyncClient", lambda **kwargs: malformed_transport)
    malformed = run(ProductServiceClient(base_url="http://product-service").get_admin_low_stock_products("admin-jwt"))
    assert malformed["success"] is False
    assert malformed["error"] == "invalid_response"
