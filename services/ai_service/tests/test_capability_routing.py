import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from jose import jwt

from app.agents.customer_agent import (
    CustomerAgent,
    CustomerIntent,
    GENERAL_KNOWLEDGE_SOURCE,
    ORDER_SERVICE_SOURCE,
    PRODUCT_SERVICE_SOURCE,
)
from app.config import settings
from app.main import app
from app.tools.order_tools import OrderServiceClient
from app.tools.product_tools import ProductServiceClient

client = TestClient(app)


def create_token(role: str = "CUSTOMER", user_id: int = 1, email: str = "customer@example.com") -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "user_id": user_id,
        "email": email,
        "exp": 9999999999,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def run_async(coro):
    return asyncio.run(coro)


# ══════════════════════════════════════════════════════════════════════════════
# 1. Deterministic Intent Classification Tests for All 7 Intent Categories
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize(
    "query, expected_intent",
    [
        # POLICY_KB
        ("What are your delivery hours and how fast is delivery?", CustomerIntent.POLICY_KB),
        ("What is your return policy for damaged items?", CustomerIntent.POLICY_KB),
        ("What is your cancellation and refund policy?", CustomerIntent.POLICY_KB),
        ("What are OrganicKart's quality standards?", CustomerIntent.POLICY_KB),
        ("What payment methods are accepted?", CustomerIntent.POLICY_KB),
        # GENERAL_KNOWLEDGE
        ("What is the difference between organic fruits and hybrid fruits?", CustomerIntent.GENERAL_KNOWLEDGE),
        ("What are the benefits of cold-pressed oils?", CustomerIntent.GENERAL_KNOWLEDGE),
        ("Why should I choose organic vegetables?", CustomerIntent.GENERAL_KNOWLEDGE),
        ("How does crop rotation help organic farming?", CustomerIntent.GENERAL_KNOWLEDGE),
        ("Explain the difference between organic and conventional farming", CustomerIntent.GENERAL_KNOWLEDGE),
        ("Explain photosynthesis in simple terms.", CustomerIntent.GENERAL_KNOWLEDGE),
        ("How many calories are in one apple?", CustomerIntent.GENERAL_KNOWLEDGE),
        ("How many calories are in mango?", CustomerIntent.GENERAL_KNOWLEDGE),
        ("Why is the sky blue?", CustomerIntent.GENERAL_KNOWLEDGE),
        ("What is the difference between a fruit and a vegetable?", CustomerIntent.GENERAL_KNOWLEDGE),
        # PRODUCT_QUERY
        ("What is the price of apples?", CustomerIntent.PRODUCT_QUERY),
        ("apple price/stock", CustomerIntent.PRODUCT_QUERY),
        ("What is the price and stock of apples?", CustomerIntent.PRODUCT_QUERY),
        ("What organic products are currently available?", CustomerIntent.PRODUCT_QUERY),
        ("Do you have apples?", CustomerIntent.PRODUCT_QUERY),
        ("is spinach in stock?", CustomerIntent.PRODUCT_QUERY),
        ("how much is whole milk?", CustomerIntent.PRODUCT_QUERY),
        ("black grapes", CustomerIntent.PRODUCT_QUERY),
        # ORDER_QUERY
        ("Show my recent orders", CustomerIntent.ORDER_QUERY),
        ("Status of order 45", CustomerIntent.ORDER_QUERY),
        ("Where is my order?", CustomerIntent.ORDER_QUERY),
        ("Show my paid orders", CustomerIntent.ORDER_QUERY),
        ("Show my cart", CustomerIntent.ORDER_QUERY),
        ("Where is my delivery?", CustomerIntent.ORDER_QUERY),
        ("Show my notifications", CustomerIntent.ORDER_QUERY),
        # MULTI_INTENT
        ("What is the price of apples and what is your return policy?", CustomerIntent.MULTI_INTENT),
        ("What are your delivery hours and what is the status of my order 45?", CustomerIntent.MULTI_INTENT),
        ("What are the benefits of cold-pressed oils and do you sell them?", CustomerIntent.MULTI_INTENT),
        # GREETING_OR_CHITCHAT
        ("Hello", CustomerIntent.GREETING_OR_CHITCHAT),
        ("Hi there", CustomerIntent.GREETING_OR_CHITCHAT),
        ("Good morning!", CustomerIntent.GREETING_OR_CHITCHAT),
        ("Thank you so much", CustomerIntent.GREETING_OR_CHITCHAT),
        ("Who are you?", CustomerIntent.GREETING_OR_CHITCHAT),
        ("Goodbye", CustomerIntent.GREETING_OR_CHITCHAT),
        # CLARIFICATION_REQUIRED
        ("Can you check my order?", CustomerIntent.CLARIFICATION_REQUIRED),
        ("Help me with an order", CustomerIntent.CLARIFICATION_REQUIRED),
        ("Filter my orders", CustomerIntent.CLARIFICATION_REQUIRED),
        ("Show my refunded orders", CustomerIntent.CLARIFICATION_REQUIRED),
    ],
)
def test_intent_classification_all_categories(query, expected_intent):
    agent = CustomerAgent()
    intent, meta = agent.classify_intent(query)
    assert intent == expected_intent, f"Query '{query}' classified as {intent}, expected {expected_intent}"


# ══════════════════════════════════════════════════════════════════════════════
# 2. Policy-KB Questions Route to Approved RAG Content
# ══════════════════════════════════════════════════════════════════════════════

def test_delivery_policy_routes_to_rag(monkeypatch):
    """
    Delivery-policy question must route to RAG, retrieve grounded policy,
    and make 0 order or product tool calls.
    """
    order_calls = []
    product_calls = []
    llm_calls = []

    async def mock_order_call(self, *args, **kwargs):
        order_calls.append("called")
        return {"success": False}

    async def mock_product_call(self, *args, **kwargs):
        product_calls.append("called")
        return {"success": False}

    async def mock_generate(self, prompt: str, system_prompt: str | None = None) -> str:
        llm_calls.append((prompt, system_prompt))
        return "OrganicKart delivers orders between 6:00 AM and 11:00 PM."

    monkeypatch.setattr(OrderServiceClient, "get_recent_orders", mock_order_call)
    monkeypatch.setattr(OrderServiceClient, "get_order_by_id", mock_order_call)
    monkeypatch.setattr(ProductServiceClient, "search_products", mock_product_call)
    monkeypatch.setattr("app.services.llm_service.LLMService.generate", mock_generate)

    token = create_token(role="CUSTOMER", user_id=1)
    res = client.post(
        "/api/v1/ai/chat",
        json={"message": "What are your delivery hours and how fast is delivery?"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert "6:00 AM and 11:00 PM" in data["answer"]
    assert data.get("intent") == "POLICY_KB"
    assert len(order_calls) == 0, "Order tools should not be invoked for policy queries"
    assert len(product_calls) == 0, "Product tools should not be invoked for policy queries"
    assert len(llm_calls) == 1
    # Check that sources contain customer_policies
    source_docs = [s["document"] for s in data["sources"]]
    assert any("customer_policies" in doc for doc in source_docs)


# ══════════════════════════════════════════════════════════════════════════════
# 3. General Knowledge Queries (Organic vs Hybrid Fruits & Cold-Pressed Oils)
# ══════════════════════════════════════════════════════════════════════════════

def test_organic_vs_hybrid_fruits_general_knowledge(monkeypatch):
    """
    'What is the difference between organic fruits and hybrid fruits?'
    must route to GENERAL_KNOWLEDGE, provide educational answer,
    and NOT return the knowledge-base fallback message.
    """
    order_calls = []
    generated_prompts = []

    async def mock_order_call(self, *args, **kwargs):
        order_calls.append("called")
        return {"success": False}

    async def mock_generate(self, prompt: str, system_prompt: str | None = None) -> str:
        generated_prompts.append((prompt, system_prompt))
        return (
            "Organic fruits are grown without synthetic pesticides or chemical fertilizers, "
            "focusing on soil health and natural growing processes. Hybrid fruits are created "
            "by cross-breeding two different varieties of plants to produce desired traits such "
            "as sweetness, disease resistance, or size."
        )

    monkeypatch.setattr(OrderServiceClient, "get_recent_orders", mock_order_call)
    monkeypatch.setattr(OrderServiceClient, "get_order_by_id", mock_order_call)
    monkeypatch.setattr("app.services.llm_service.LLMService.generate", mock_generate)

    token = create_token(role="CUSTOMER", user_id=1)
    res = client.post(
        "/api/v1/ai/chat",
        json={"message": "What is the difference between organic fruits and hybrid fruits?"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data.get("intent") == "GENERAL_KNOWLEDGE"
    assert "Organic fruits are grown without synthetic pesticides" in data["answer"]
    assert "cross-breeding" in data["answer"]
    # Must NOT return fallback error
    assert "I don't have information about that in the OrganicKart knowledge base" not in data["answer"]
    assert len(order_calls) == 0


def test_cold_pressed_oil_benefits_no_invented_claims(monkeypatch):
    """
    'What are the benefits of cold-pressed oils?'
    must use general knowledge without inventing OrganicKart store claims or prices.
    """
    captured_systems = []

    async def mock_generate(self, prompt: str, system_prompt: str | None = None) -> str:
        captured_systems.append(system_prompt)
        return (
            "Cold-pressed oils are extracted at low temperatures without chemical solvents, "
            "retaining natural antioxidants, vitamins, and healthy fatty acids. They preserve "
            "their natural aroma and nutritional value."
        )

    monkeypatch.setattr("app.services.llm_service.LLMService.generate", mock_generate)

    token = create_token(role="CUSTOMER", user_id=1)
    res = client.post(
        "/api/v1/ai/chat",
        json={"message": "What are the benefits of cold-pressed oils?"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data.get("intent") == "GENERAL_KNOWLEDGE"
    assert "retaining natural antioxidants" in data["answer"]
    assert "I don't have information about that in the OrganicKart knowledge base" not in data["answer"]
    assert len(captured_systems) == 1
    assert "Educational Assistant" in captured_systems[0]


# ══════════════════════════════════════════════════════════════════════════════
# 4. Product Query: Apple Price and Stock Routes to Product Service
# ══════════════════════════════════════════════════════════════════════════════

def test_apple_price_stock_routes_to_product_service(monkeypatch):
    """
    'What is the price and stock of apples?' must query ProductServiceClient.
    Never invents current catalog data and does not invoke LLM or Order Service.
    """
    searches = []
    llm_calls = []
    order_calls = []

    async def mock_search_products(self, query=None):
        searches.append(query)
        return {
            "success": True,
            "products": [
                {
                    "id": 1,
                    "name": "Organic Shimla Apples",
                    "price": "140.00",
                    "unit": "kg",
                    "stock_quantity": 25,
                    "certification": "APPROVED",
                }
            ],
        }

    async def mock_order_call(self, *args, **kwargs):
        order_calls.append("called")
        return {"success": False}

    async def mock_generate(self, *args, **kwargs):
        llm_calls.append("called")
        return ""

    monkeypatch.setattr(ProductServiceClient, "search_products", mock_search_products)
    monkeypatch.setattr(OrderServiceClient, "get_recent_orders", mock_order_call)
    monkeypatch.setattr("app.services.llm_service.LLMService.generate", mock_generate)

    token = create_token(role="CUSTOMER", user_id=1)

    # Subcase 1: 'What is the price and stock of apples?'
    res1 = client.post(
        "/api/v1/ai/chat",
        json={"message": "What is the price and stock of apples?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res1.status_code == status.HTTP_200_OK
    data1 = res1.json()
    assert data1.get("intent") == "PRODUCT_QUERY"
    assert "Organic Shimla Apples" in data1["answer"]
    assert "₹140.00 / kg" in data1["answer"]
    assert "In stock (25 available)" in data1["answer"]
    assert searches == ["apples"]
    assert len(llm_calls) == 0
    assert len(order_calls) == 0

    # Subcase 2: 'apple price/stock'
    searches.clear()
    res2 = client.post(
        "/api/v1/ai/chat",
        json={"message": "apple price/stock"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res2.status_code == status.HTTP_200_OK
    data2 = res2.json()
    assert data2.get("intent") == "PRODUCT_QUERY"
    assert "Organic Shimla Apples" in data2["answer"]
    assert searches == ["apple"]

    # Subcase 3: 'What organic products are currently available?'
    searches.clear()
    res3 = client.post(
        "/api/v1/ai/chat",
        json={"message": "What organic products are currently available?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res3.status_code == status.HTTP_200_OK
    data3 = res3.json()
    assert data3.get("intent") == "PRODUCT_QUERY"
    assert "Organic Shimla Apples" in data3["answer"]
    assert searches == [None]


# ══════════════════════════════════════════════════════════════════════════════
# 5. Order Query: Recent Orders and Order Status via Authorized Order Service
# ══════════════════════════════════════════════════════════════════════════════

def test_recent_orders_and_order_status_routes_to_order_service(monkeypatch):
    """
    Recent orders and order status requests must invoke authorized Order Service
    with the customer's verified JWT.
    """
    recent_calls = []
    id_calls = []

    async def mock_get_recent_orders(self, token, user_id):
        recent_calls.append((token, user_id))
        return {
            "success": True,
            "orders": [
                {
                    "id": 101,
                    "user_id": user_id,
                    "status": "DELIVERED",
                    "payment_status": "PAID",
                    "total_amount": 500.0,
                    "created_at": "2026-10-18T10:00:00",
                    "items": [{"product_name": "Organic Honey", "quantity": 1}],
                }
            ],
        }

    async def mock_get_order_by_id(self, order_id, token, user_id):
        id_calls.append((order_id, token, user_id))
        return {
            "success": True,
            "order": {
                "id": order_id,
                "user_id": user_id,
                "status": "PROCESSING",
                "payment_status": "PAID",
                "total_amount": 250.0,
                "created_at": "2026-10-20T12:00:00",
                "items": [],
            },
        }

    monkeypatch.setattr(OrderServiceClient, "get_recent_orders", mock_get_recent_orders)
    monkeypatch.setattr(OrderServiceClient, "get_order_by_id", mock_get_order_by_id)

    token = create_token(role="CUSTOMER", user_id=42)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Recent orders
    res_recent = client.post("/api/v1/ai/chat", json={"message": "Show my recent orders"}, headers=headers)
    assert res_recent.status_code == status.HTTP_200_OK
    assert res_recent.json().get("intent") == "ORDER_QUERY"
    assert "Order #101" in res_recent.json()["answer"]
    assert recent_calls[0][1] == 42  # Authenticated user_id

    # 2. Specific order ID
    res_id = client.post("/api/v1/ai/chat", json={"message": "Status of order 45"}, headers=headers)
    assert res_id.status_code == status.HTTP_200_OK
    assert res_id.json().get("intent") == "ORDER_QUERY"
    assert "Order #45 Status" in res_id.json()["answer"]
    assert id_calls[0] == (45, token, 42)


# ══════════════════════════════════════════════════════════════════════════════
# 6. Ambiguous Order Request Triggers Clarification
# ══════════════════════════════════════════════════════════════════════════════

def test_ambiguous_order_request_prompts_clarification(monkeypatch):
    """
    Ambiguous order requests must trigger clarification asking for the order ID
    rather than guessing, halluncinating, or calling Order Service.
    """
    order_calls = []

    async def mock_order_call(self, *args, **kwargs):
        order_calls.append("called")
        return {"success": False}

    monkeypatch.setattr(OrderServiceClient, "get_order_by_id", mock_order_call)
    monkeypatch.setattr(OrderServiceClient, "get_recent_orders", mock_order_call)

    token = create_token(role="CUSTOMER", user_id=1)
    res = client.post(
        "/api/v1/ai/chat",
        json={"message": "Can you check my order?"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data.get("intent") == "CLARIFICATION_REQUIRED"
    assert "provide your order id" in data["answer"].lower()
    assert len(order_calls) == 0, "No order tools should be called for ambiguous requests"


# ══════════════════════════════════════════════════════════════════════════════
# 7. Multi-Intent Question Combines Correct Capabilities
# ══════════════════════════════════════════════════════════════════════════════

def test_multi_intent_product_and_policy(monkeypatch):
    """
    'What is the price of apples and what is your return policy?'
    combines PRODUCT_QUERY + POLICY_KB, queries both capabilities,
    and synthesizes results cleanly.
    """
    searches = []
    rag_prompts = []

    async def mock_search_products(self, query=None):
        searches.append(query)
        return {
            "success": True,
            "products": [
                {
                    "id": 1,
                    "name": "Organic Apples",
                    "price": "120.00",
                    "unit": "kg",
                    "stock_quantity": 15,
                }
            ],
        }

    async def mock_generate(self, prompt: str, system_prompt: str | None = None) -> str:
        rag_prompts.append(prompt)
        return "Returns must be requested within 24 hours of delivery for fresh produce."

    monkeypatch.setattr(ProductServiceClient, "search_products", mock_search_products)
    monkeypatch.setattr("app.services.llm_service.LLMService.generate", mock_generate)

    token = create_token(role="CUSTOMER", user_id=1)
    res = client.post(
        "/api/v1/ai/chat",
        json={"message": "What is the price of apples and what is your return policy?"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data.get("intent") == "MULTI_INTENT"
    # Contains product section
    assert "Organic Apples" in data["answer"]
    assert "₹120.00 / kg" in data["answer"]
    # Contains policy section
    assert "24 hours" in data["answer"]
    # Contains combined sources
    source_docs = [s["document"] for s in data["sources"]]
    assert any("Product Service" in doc for doc in source_docs)
    assert any("customer_policies" in doc for doc in source_docs)


# ══════════════════════════════════════════════════════════════════════════════
# 8. Unsupported Official Policy Claim: No Invention
# ══════════════════════════════════════════════════════════════════════════════

def test_unsupported_official_policy_claim_no_invention(monkeypatch):
    """
    Asking for unsupported policy options (e.g. 60-day returns or Bitcoin payment)
    must rely on retrieved policy context and NOT invent permission.
    """
    captured_system = []

    async def mock_generate(self, prompt: str, system_prompt: str | None = None) -> str:
        captured_system.append(system_prompt)
        # LLM following prompt rule 3 states policy does not permit it
        return "OrganicKart does not support returns after 60 days. Perishable organic produce must be reported within 24 hours of delivery."

    monkeypatch.setattr("app.services.llm_service.LLMService.generate", mock_generate)

    token = create_token(role="CUSTOMER", user_id=1)
    res = client.post(
        "/api/v1/ai/chat",
        json={"message": "Can I return fresh vegetables after 60 days?"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data.get("intent") == "POLICY_KB"
    assert "does not support returns after 60 days" in data["answer"]
    assert len(captured_system) == 1
    assert "unsupported policy requests" in captured_system[0]


# ══════════════════════════════════════════════════════════════════════════════
# 9. JWT Spoofing & Cross-Customer Order Access Denied
# ══════════════════════════════════════════════════════════════════════════════

def test_jwt_spoofing_and_cross_customer_order_access_denied(monkeypatch):
    """
    Customer identity comes strictly from verified JWT claims.
    Requesting another customer's order ID must safely report not found
    without revealing any other customer's order information.
    """
    requested_calls = []

    async def mock_get_order_by_id(self, order_id, token, user_id):
        requested_calls.append((order_id, user_id))
        # Simulated Order Service ownership check:
        # Order 99 belongs to user 2. If user_id != 2, return not found.
        if order_id == 99 and user_id != 2:
            return {"success": False, "detail": f"Order #{order_id} was not found."}
        return {"success": True, "order": {"id": order_id, "user_id": user_id, "status": "CONFIRMED"}}

    monkeypatch.setattr(OrderServiceClient, "get_order_by_id", mock_get_order_by_id)

    # Customer 1 attempts to access order 99 (which belongs to customer 2)
    token = create_token(role="CUSTOMER", user_id=1, email="user1@example.com")
    res = client.post(
        "/api/v1/ai/chat",
        json={"message": "What is the status of order 99?"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    assert requested_calls == [(99, 1)]  # Enforced user_id=1 from JWT
    data = res.json()
    assert "Order #99 was not found" in data["answer"]
    assert "CONFIRMED" not in data["answer"]


# ══════════════════════════════════════════════════════════════════════════════
# 10. General Knowledge Regression: Photosynthesis, Calories, Sky Blue, Fruit vs Veg
# ══════════════════════════════════════════════════════════════════════════════

def test_photosynthesis_educational_routing_no_fake_sources(monkeypatch):
    """
    'Explain photosynthesis in simple terms.' must route to GENERAL_KNOWLEDGE,
    invoke LLM without fake knowledge-base/product-catalog citations,
    and make 0 product/order tool calls.
    """
    product_calls = []
    order_calls = []
    llm_prompts = []

    async def mock_product_call(*args, **kwargs):
        product_calls.append("called")
        return {"success": False}

    async def mock_order_call(*args, **kwargs):
        order_calls.append("called")
        return {"success": False}

    async def mock_generate(self, prompt: str, system_prompt: str | None = None) -> str:
        llm_prompts.append((prompt, system_prompt))
        return (
            "Photosynthesis is the process where green plants use sunlight, water, "
            "and carbon dioxide to produce oxygen and energy in the form of sugar."
        )

    monkeypatch.setattr(ProductServiceClient, "search_products", mock_product_call)
    monkeypatch.setattr(OrderServiceClient, "get_recent_orders", mock_order_call)
    monkeypatch.setattr("app.services.llm_service.LLMService.generate", mock_generate)

    token = create_token(role="CUSTOMER", user_id=1)
    res = client.post(
        "/api/v1/ai/chat",
        json={"message": "Explain photosynthesis in simple terms."},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data.get("intent") == "GENERAL_KNOWLEDGE"
    assert "Photosynthesis is the process" in data["answer"]
    assert "I don't have information about that in the OrganicKart knowledge base" not in data["answer"]
    assert len(product_calls) == 0, "Product Service must not be invoked for photosynthesis"
    assert len(order_calls) == 0, "Order Service must not be invoked for photosynthesis"
    assert len(llm_prompts) == 1
    # Check source attribution
    assert len(data["sources"]) == 1
    assert data["sources"][0]["document"] == "General Knowledge"
    assert data["sources"][0]["title"] == "General Knowledge"
    assert not any("product" in s.get("document", "").lower() for s in data["sources"])
    assert not any("policy" in s.get("document", "").lower() for s in data["sources"])


@pytest.mark.parametrize("query", ["How many calories are in one apple?", "How many calories are in mango?"])
def test_apple_and_mango_calories_general_knowledge_no_catalog_call(monkeypatch, query):
    """
    Calorie questions must route to GENERAL_KNOWLEDGE, invoke LLM without
    making Product Service catalog calls, and label sources as General Knowledge.
    """
    product_calls = []
    order_calls = []

    async def mock_product_call(*args, **kwargs):
        product_calls.append("called")
        return {"success": False}

    async def mock_order_call(*args, **kwargs):
        order_calls.append("called")
        return {"success": False}

    async def mock_generate(self, prompt: str, system_prompt: str | None = None) -> str:
        return "A medium fruit of this type typically contains around 60 to 95 calories depending on its size and variety."

    monkeypatch.setattr(ProductServiceClient, "search_products", mock_product_call)
    monkeypatch.setattr(OrderServiceClient, "get_recent_orders", mock_order_call)
    monkeypatch.setattr("app.services.llm_service.LLMService.generate", mock_generate)

    token = create_token(role="CUSTOMER", user_id=1)
    res = client.post(
        "/api/v1/ai/chat",
        json={"message": query},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data.get("intent") == "GENERAL_KNOWLEDGE"
    assert "calories" in data["answer"]
    assert "I don't have information about that in the OrganicKart knowledge base" not in data["answer"]
    assert len(product_calls) == 0, f"Product Service should not be called for '{query}'"
    assert len(order_calls) == 0
    # Must never be labeled Product Catalog
    for s in data["sources"]:
        assert s.get("document") != "Product Service API"
        assert "Product Catalog" not in s.get("title", "")
    assert data["sources"] == GENERAL_KNOWLEDGE_SOURCE


@pytest.mark.parametrize("query", ["Why is the sky blue?", "What is the difference between a fruit and a vegetable?"])
def test_sky_blue_and_fruit_vs_vegetable_general_knowledge(monkeypatch, query):
    """
    General scientific and botanical questions must route to GENERAL_KNOWLEDGE
    and not fall back to POLICY_KB or return knowledge base errors.
    """
    product_calls = []

    async def mock_product_call(*args, **kwargs):
        product_calls.append("called")
        return {"success": False}

    async def mock_generate(self, prompt: str, system_prompt: str | None = None) -> str:
        return "This is a general educational scientific answer."

    monkeypatch.setattr(ProductServiceClient, "search_products", mock_product_call)
    monkeypatch.setattr("app.services.llm_service.LLMService.generate", mock_generate)

    token = create_token(role="CUSTOMER", user_id=1)
    res = client.post(
        "/api/v1/ai/chat",
        json={"message": query},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data.get("intent") == "GENERAL_KNOWLEDGE"
    assert data["answer"] == "This is a general educational scientific answer."
    assert len(product_calls) == 0
    assert data["sources"] == GENERAL_KNOWLEDGE_SOURCE


def test_empty_rag_results_successful_ollama_generation(monkeypatch):
    """
    When RAG returns 0 relevant documents for a general knowledge question,
    Ollama must still be invoked to generate the answer without fabricating citations.
    """
    retriever_called = []
    llm_prompts = []

    def mock_retrieve(self, query, top_k=None):
        retriever_called.append(query)
        return {"context": "", "sources": [], "raw_results": []}

    async def mock_generate(self, prompt: str, system_prompt: str | None = None) -> str:
        llm_prompts.append((prompt, system_prompt))
        return "General educational answer generated from LLM pre-trained knowledge."

    monkeypatch.setattr("app.rag.retriever.RAGRetriever.retrieve", mock_retrieve)
    monkeypatch.setattr("app.services.llm_service.LLMService.generate", mock_generate)

    token = create_token(role="CUSTOMER", user_id=1)
    res = client.post(
        "/api/v1/ai/chat",
        json={"message": "Explain photosynthesis in simple terms."},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data.get("intent") == "GENERAL_KNOWLEDGE"
    assert "General educational answer" in data["answer"]
    assert len(retriever_called) == 1
    assert len(llm_prompts) == 1
    # Prompt should ask the educational question without context
    assert "Educational Question:" in llm_prompts[0][0]
    assert "Supporting OrganicKart Knowledge Context:" not in llm_prompts[0][0]
    assert data["sources"] == GENERAL_KNOWLEDGE_SOURCE


def test_policy_question_grounded_in_rag(monkeypatch):
    """
    Store policy questions must route to POLICY_KB, retrieve grounded policy documents,
    and never invoke Product or Order microservices.
    """
    product_calls = []
    order_calls = []

    async def mock_product_call(*args, **kwargs):
        product_calls.append("called")
        return {"success": False}

    async def mock_order_call(*args, **kwargs):
        order_calls.append("called")
        return {"success": False}

    async def mock_generate(self, prompt: str, system_prompt: str | None = None) -> str:
        return "Perishable organic items must be reported within 24 hours with photos for a full refund or replacement."

    monkeypatch.setattr(ProductServiceClient, "search_products", mock_product_call)
    monkeypatch.setattr(OrderServiceClient, "get_recent_orders", mock_order_call)
    monkeypatch.setattr("app.services.llm_service.LLMService.generate", mock_generate)

    token = create_token(role="CUSTOMER", user_id=1)
    res = client.post(
        "/api/v1/ai/chat",
        json={"message": "What is your return policy for damaged items?"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data.get("intent") == "POLICY_KB"
    assert "within 24 hours" in data["answer"]
    assert len(product_calls) == 0
    assert len(order_calls) == 0
    # Policy documents should be cited
    source_docs = [s["document"] for s in data["sources"]]
    assert any("customer_policies" in doc for doc in source_docs)


def test_product_price_stock_calls_product_service_alone(monkeypatch):
    """
    Current product price/stock queries must query ProductServiceClient directly
    and NOT invoke OrderServiceClient or LLM.
    """
    searches = []
    llm_calls = []
    order_calls = []

    async def mock_search_products(self, query=None):
        searches.append(query)
        return {
            "success": True,
            "products": [
                {
                    "id": 10,
                    "name": "Kashmiri Apples",
                    "price": "180.00",
                    "unit": "kg",
                    "stock": 25,
                    "is_organic": True,
                }
            ],
        }

    async def mock_order_call(*args, **kwargs):
        order_calls.append("called")
        return {"success": False}

    async def mock_generate(*args, **kwargs):
        llm_calls.append("called")
        return "llm answer"

    monkeypatch.setattr(ProductServiceClient, "search_products", mock_search_products)
    monkeypatch.setattr(OrderServiceClient, "get_recent_orders", mock_order_call)
    monkeypatch.setattr("app.services.llm_service.LLMService.generate", mock_generate)

    token = create_token(role="CUSTOMER", user_id=1)
    res = client.post(
        "/api/v1/ai/chat",
        json={"message": "What is the price and stock of Kashmiri Apples?"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data.get("intent") == "PRODUCT_QUERY"
    assert "Kashmiri Apples" in data["answer"]
    assert "₹180.00 / kg" in data["answer"]
    assert searches == ["kashmiri apples"]
    assert len(order_calls) == 0
    assert len(llm_calls) == 0
    assert data["sources"] == PRODUCT_SERVICE_SOURCE


def test_authenticated_recent_orders_calls_order_service(monkeypatch):
    """
    Authenticated recent orders questions must call OrderServiceClient with verified JWT user_id.
    """
    order_user_ids = []
    product_calls = []
    llm_calls = []

    async def mock_get_recent_orders(self, token, user_id):
        order_user_ids.append(user_id)
        return {
            "success": True,
            "orders": [
                {
                    "id": 101,
                    "user_id": user_id,
                    "status": "CONFIRMED",
                    "payment_status": "PAID",
                    "total_amount": 350.00,
                    "items": [{"product_name": "Organic Apples", "quantity": 2}],
                }
            ],
        }

    async def mock_product_call(*args, **kwargs):
        product_calls.append("called")
        return {"success": False}

    async def mock_generate(*args, **kwargs):
        llm_calls.append("called")
        return "llm answer"

    monkeypatch.setattr(OrderServiceClient, "get_recent_orders", mock_get_recent_orders)
    monkeypatch.setattr(ProductServiceClient, "search_products", mock_product_call)
    monkeypatch.setattr("app.services.llm_service.LLMService.generate", mock_generate)

    token = create_token(role="CUSTOMER", user_id=7)
    res = client.post(
        "/api/v1/ai/chat",
        json={"message": "Show my recent orders"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data.get("intent") == "ORDER_QUERY"
    assert "Order #101" in data["answer"]
    assert "Organic Apples" in data["answer"]
    assert order_user_ids == [7]  # Enforces JWT user_id=7
    assert len(product_calls) == 0
    assert len(llm_calls) == 0
    assert data["sources"] == ORDER_SERVICE_SOURCE
