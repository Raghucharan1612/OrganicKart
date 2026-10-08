import asyncio

import pytest
import httpx

from app.agents.customer_agent import CustomerAgent
from app.services.web_search_service import WebSearchService, WebSearchUnavailable


class FakeRetriever:
    def retrieve(self, query):
        return {
            "context": "OrganicKart delivers certified organic products.",
            "sources": [{"document": "overview.md", "title": "Overview", "score": 0.9}],
        }


class FakeLLM:
    def __init__(self):
        self.calls = 0

    async def generate(self, prompt, system_prompt=None):
        self.calls += 1
        return "OrganicKart is an organic marketplace."


class FakeOrderClient:
    def __init__(self):
        self.calls = 0
        self.order_by_id_calls = []
        self.recent_order_calls = 0
        self.cart_calls = 0

    async def get_order_by_id(self, order_id, token, user_id):
        self.calls += 1
        self.order_by_id_calls.append(order_id)
        return {"success": True, "order": {"id": order_id, "status": "CONFIRMED", "payment_status": "PAID", "total_amount": 10, "items": []}}

    async def get_recent_orders(self, token, user_id):
        self.calls += 1
        self.recent_order_calls += 1
        return {"success": True, "orders": [{"id": 123, "status": "CONFIRMED", "payment_status": "PAID", "total_amount": 10, "items": []}]}

    async def get_my_cart(self, token, user_id):
        self.calls += 1
        self.cart_calls += 1
        return {
            "success": True,
            "cart": {
                "id": 1,
                "user_id": user_id,
                "items": [{"product_name": "Organic Apples", "unit_price": 50, "quantity": 2}],
            },
        }


class FakeWebSearch:
    def __init__(self, results=None, error=None):
        self.results = results or []
        self.error = error
        self.calls = 0

    async def search(self, query):
        self.calls += 1
        if self.error:
            raise self.error
        return self.results


class FakeProductClient:
    def __init__(self, products=None, error=None):
        self.products = products if products is not None else [
            {
                "id": 1,
                "name": "Organic Apples",
                "price": "120.00",
                "stock_quantity": 10,
                "unit": "kg",
                "certification": "APPROVED",
            },
        ]
        self.error = error
        self.search_calls = []
        self.product_calls = []

    async def search_products(self, query=None):
        self.search_calls.append(query)
        if self.error:
            return {"success": False, "error": self.error, "detail": f"Product Service {self.error}."}
        return {"success": True, "products": self.products}

    async def get_product(self, product_id):
        self.product_calls.append(product_id)
        if self.error:
            return {"success": False, "error": self.error, "detail": f"Product Service {self.error}."}
        return {"success": True, "product": self.products[0]}


class FakeDeliveryClient:
    def __init__(self, deliveries=None, error=None):
        self.deliveries = deliveries if deliveries is not None else [{
            "id": 9,
            "order_id": 123,
            "user_id": 1,
            "tracking_number": "OK-TRACK123",
            "status": "OUT_FOR_DELIVERY",
            "estimated_delivery_date": "2026-10-04T12:00:00",
            "shipped_at": "2026-10-03T08:00:00",
        }]
        self.error = error
        self.calls = []

    async def get_my_deliveries(self, token, user_id):
        self.calls.append((token, user_id))
        if self.error:
            return {"success": False, "error": self.error, "detail": f"Delivery Service {self.error}."}
        return {"success": True, "deliveries": self.deliveries}


class FakeNotificationClient:
    def __init__(self, notifications=None, error=None):
        self.notifications = notifications if notifications is not None else [
            {
                "id": 1,
                "user_id": 1,
                "type": "DELIVERY_CONFIRMED",
                "title": "Delivery #17: OUT_FOR_DELIVERY",
                "message": "Your delivery status is now OUT_FOR_DELIVERY.",
                "status": "SENT",
            },
            {
                "id": 2,
                "user_id": 1,
                "type": "WELCOME",
                "title": "Welcome to OrganicKart",
                "message": "Thank you for joining!",
                "status": "READ",
            },
        ]
        self.error = error
        self.calls = []

    async def get_my_notifications(self, token, user_id):
        self.calls.append((token, user_id))
        if self.error:
            return {"success": False, "error": self.error, "detail": f"Notification Service {self.error}."}
        return {"success": True, "notifications": self.notifications}


def run(coro):
    return asyncio.run(coro)


def test_web_search_success(monkeypatch):
    service = WebSearchService(enabled=True, api_key="test-key")

    async def fake_brave(query):
        return [{"title": "Organic farming", "url": "https://example.test/farming", "snippet": "Organic farming supports soil health."}]

    monkeypatch.setattr(service, "_search_brave", fake_brave)
    assert run(service.search("What is organic farming?"))[0]["title"] == "Organic farming"


def test_web_search_disabled():
    with pytest.raises(WebSearchUnavailable):
        run(WebSearchService(enabled=False).search("What is organic farming?"))


def test_web_search_timeout(monkeypatch):
    service = WebSearchService(enabled=True, api_key="test-key")

    class TimeoutClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, *args, **kwargs):
            raise httpx.TimeoutException("timed out")

    monkeypatch.setattr("app.services.web_search_service.httpx.AsyncClient", lambda **kwargs: TimeoutClient())
    with pytest.raises(WebSearchUnavailable, match="timed out"):
        run(service.search("What is organic farming?"))


def test_web_search_provider_failure(monkeypatch):
    service = WebSearchService(enabled=True, api_key="test-key")

    class FailureClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, *args, **kwargs):
            raise httpx.ConnectError("provider unavailable")

    monkeypatch.setattr("app.services.web_search_service.httpx.AsyncClient", lambda **kwargs: FailureClient())
    with pytest.raises(WebSearchUnavailable, match="unavailable"):
        run(service.search("What is organic farming?"))


def test_general_question_routes_to_web_search():
    llm = FakeLLM()
    web = FakeWebSearch([{"title": "Spinach", "url": "https://example.test/spinach", "snippet": "Spinach provides fibre and micronutrients."}])
    agent = CustomerAgent(retriever=FakeRetriever(), llm_service=llm, order_client=FakeOrderClient(), web_search_service=web)
    response = run(agent.handle_query("What are the benefits of organic spinach?"))
    assert "fibre" in response["answer"]
    assert response["sources"][0]["url"] == "https://example.test/spinach"
    assert web.calls == 1
    assert llm.calls == 0


@pytest.mark.parametrize("question", [
    "organic order policies",
    "What are OrganicKart's delivery policies?",
    "What is your return policy?",
    "How does OrganicKart work?",
    "What is OrganicKart?",
    "latest OrganicKart delivery policy",
])
def test_organickart_question_routes_to_rag(question):
    llm = FakeLLM()
    web = FakeWebSearch()
    agent = CustomerAgent(retriever=FakeRetriever(), llm_service=llm, order_client=FakeOrderClient(), web_search_service=web)
    response = run(agent.handle_query(question))
    assert response["answer"] == "OrganicKart is an organic marketplace."
    assert llm.calls == 1
    assert web.calls == 0


def test_order_question_routes_to_order_tool_without_llm():
    llm = FakeLLM()
    orders = FakeOrderClient()
    web = FakeWebSearch()
    agent = CustomerAgent(retriever=FakeRetriever(), llm_service=llm, order_client=orders, web_search_service=web)
    response = run(agent.handle_query("What is the status of order 123?", user_id=1, token="token"))
    assert "Order #123 Status" in response["answer"]
    assert orders.calls == 1
    assert llm.calls == 0
    assert web.calls == 0


def test_recent_order_question_routes_to_order_tool_without_llm():
    llm = FakeLLM()
    orders = FakeOrderClient()
    web = FakeWebSearch()
    agent = CustomerAgent(retriever=FakeRetriever(), llm_service=llm, order_client=orders, web_search_service=web)
    response = run(agent.handle_query("Show my recent orders", user_id=1, token="token"))
    assert "recent OrganicKart orders" in response["answer"]
    assert orders.calls == 1
    assert llm.calls == 0
    assert web.calls == 0


@pytest.mark.parametrize(
    ("question", "expected_intent", "expected_order_ids", "expected_recent_calls"),
    [
        ("What is the status of my order?", "ORDER_STATUS", [], 1),
        ("What is my order status?", "ORDER_STATUS", [], 1),
        ("Where is my order?", "ORDER_STATUS", [], 1),
        ("Show my recent orders", "RECENT_ORDERS", [], 1),
        ("What is the status of order 123?", "ORDER_BY_ID", [123], 0),
        ("Show order 123", "ORDER_BY_ID", [123], 0),
    ],
)
def test_natural_language_order_queries_use_the_expected_order_tool(
    question,
    expected_intent,
    expected_order_ids,
    expected_recent_calls,
):
    llm = FakeLLM()
    orders = FakeOrderClient()
    web = FakeWebSearch()
    agent = CustomerAgent(
        retriever=FakeRetriever(),
        llm_service=llm,
        order_client=orders,
        web_search_service=web,
    )

    is_order, intent, _ = agent._is_live_order_query(question)
    response = run(agent.handle_query(question, user_id=1, token="token"))

    assert is_order is True
    assert intent == expected_intent
    assert response["sources"] == [{"document": "Order Service API", "title": "Order Service", "score": 1.0}]
    assert orders.order_by_id_calls == expected_order_ids
    assert orders.recent_order_calls == expected_recent_calls
    assert orders.cart_calls == 0
    assert llm.calls == 0
    assert web.calls == 0


@pytest.mark.parametrize("question", [
    "Products in my cart?",
    "What's in my cart?",
    "Show my cart",
    "What items are in my cart?",
    "How many items are in my cart?",
    "What's my cart total?",
])
def test_cart_questions_route_to_live_cart_tool_without_llm_or_rag(question):
    llm = FakeLLM()
    orders = FakeOrderClient()
    deliveries = FakeDeliveryClient()
    web = FakeWebSearch()
    agent = CustomerAgent(
        retriever=FakeRetriever(),
        llm_service=llm,
        order_client=orders,
        delivery_client=deliveries,
        web_search_service=web,
    )

    response = run(agent.handle_query(question, user_id=1, token="token"))

    assert "Total quantity: 2" in response["answer"]
    assert "Cart total: ₹100.00" in response["answer"]
    assert orders.cart_calls == 1
    assert orders.recent_order_calls == 0
    assert orders.order_by_id_calls == []
    assert deliveries.calls == []
    assert llm.calls == 0
    assert web.calls == 0


@pytest.mark.parametrize("question", [
    "Where is my delivery?",
    "Track my delivery",
    "What is my delivery status?",
    "When will my delivery arrive?",
])
def test_general_delivery_questions_route_to_live_delivery_tool_without_llm_or_rag(question):
    llm = FakeLLM()
    orders = FakeOrderClient()
    deliveries = FakeDeliveryClient()
    web = FakeWebSearch()
    agent = CustomerAgent(
        retriever=FakeRetriever(), llm_service=llm, order_client=orders,
        product_client=FakeProductClient(), delivery_client=deliveries, web_search_service=web,
    )

    response = run(agent.handle_query(question, user_id=1, token="token"))

    assert "Your latest delivery:" in response["answer"]
    assert "• Status: OUT_FOR_DELIVERY" in response["answer"]
    assert "Estimated delivery: 2026-10-04" in response["answer"]
    assert deliveries.calls == [("token", 1)]
    assert orders.calls == 0
    assert llm.calls == 0
    assert web.calls == 0


def test_delivery_is_my_order_out_for_delivery_pending_status():
    deliveries = FakeDeliveryClient(deliveries=[{
        "id": 17,
        "order_id": 59,
        "user_id": 1,
        "tracking_number": "OK-24D525C31001",
        "status": "PENDING",
        "estimated_delivery_date": "2026-10-04T12:00:00",
    }])
    agent = CustomerAgent(
        retriever=FakeRetriever(), llm_service=FakeLLM(), order_client=FakeOrderClient(),
        product_client=FakeProductClient(), delivery_client=deliveries, web_search_service=FakeWebSearch(),
    )

    response = run(agent.handle_query("Is my order out for delivery?", user_id=1, token="token"))

    expected = (
        "No, your order is not out for delivery yet.\n\n"
        "• Delivery #17\n"
        "• Order #59\n"
        "• Current status: PENDING\n"
        "• Tracking number: OK-24D525C31001\n"
        "• Estimated delivery: 2026-10-04"
    )
    assert response["answer"] == expected


def test_delivery_is_my_order_out_for_delivery_out_for_delivery_status():
    deliveries = FakeDeliveryClient(deliveries=[{
        "id": 17,
        "order_id": 59,
        "user_id": 1,
        "tracking_number": "OK-24D525C31001",
        "status": "OUT_FOR_DELIVERY",
        "estimated_delivery_date": "2026-10-04T12:00:00",
    }])
    agent = CustomerAgent(
        retriever=FakeRetriever(), llm_service=FakeLLM(), order_client=FakeOrderClient(),
        product_client=FakeProductClient(), delivery_client=deliveries, web_search_service=FakeWebSearch(),
    )

    response = run(agent.handle_query("Is my order out for delivery?", user_id=1, token="token"))

    expected = (
        "Yes, your order is out for delivery.\n\n"
        "• Delivery #17\n"
        "• Order #59\n"
        "• Current status: OUT_FOR_DELIVERY\n"
        "• Tracking number: OK-24D525C31001\n"
        "• Estimated delivery: 2026-10-04"
    )
    assert response["answer"] == expected


def test_delivery_has_my_order_been_dispatched():
    deliveries_pending = FakeDeliveryClient(deliveries=[{
        "id": 17,
        "order_id": 59,
        "user_id": 1,
        "tracking_number": "OK-24D525C31001",
        "status": "PENDING",
        "estimated_delivery_date": "2026-10-04T12:00:00",
    }])
    agent_pending = CustomerAgent(
        retriever=FakeRetriever(), llm_service=FakeLLM(), order_client=FakeOrderClient(),
        product_client=FakeProductClient(), delivery_client=deliveries_pending, web_search_service=FakeWebSearch(),
    )
    res_pending = run(agent_pending.handle_query("Has my order been dispatched?", user_id=1, token="token"))
    assert "No, your order has not been dispatched yet." in res_pending["answer"]
    assert "• Current status: PENDING" in res_pending["answer"]

    deliveries_dispatched = FakeDeliveryClient(deliveries=[{
        "id": 17,
        "order_id": 59,
        "user_id": 1,
        "tracking_number": "OK-24D525C31001",
        "status": "IN_TRANSIT",
        "shipped_at": "2026-10-03T10:00:00",
        "estimated_delivery_date": "2026-10-04T12:00:00",
    }])
    agent_dispatched = CustomerAgent(
        retriever=FakeRetriever(), llm_service=FakeLLM(), order_client=FakeOrderClient(),
        product_client=FakeProductClient(), delivery_client=deliveries_dispatched, web_search_service=FakeWebSearch(),
    )
    res_dispatched = run(agent_dispatched.handle_query("Has my order been dispatched?", user_id=1, token="token"))
    assert "Yes, your order has been dispatched." in res_dispatched["answer"]
    assert "• Current status: IN_TRANSIT" in res_dispatched["answer"]


def test_delivery_query_handles_no_tracking_information():
    deliveries = FakeDeliveryClient(deliveries=[])
    agent = CustomerAgent(
        retriever=FakeRetriever(), llm_service=FakeLLM(), order_client=FakeOrderClient(),
        product_client=FakeProductClient(), delivery_client=deliveries, web_search_service=FakeWebSearch(),
    )

    response = run(agent.handle_query("Track my delivery", user_id=1, token="token"))

    assert response["answer"] == "There is no delivery tracking information available for your account yet."


@pytest.mark.parametrize("error", ["unavailable", "timeout"])
def test_delivery_query_handles_service_failures(error):
    deliveries = FakeDeliveryClient(error=error)
    agent = CustomerAgent(
        retriever=FakeRetriever(), llm_service=FakeLLM(), order_client=FakeOrderClient(),
        product_client=FakeProductClient(), delivery_client=deliveries, web_search_service=FakeWebSearch(),
    )

    response = run(agent.handle_query("Where is my delivery?", user_id=1, token="token"))

    assert response["answer"] == f"Delivery Service {error}."


def test_where_is_my_order_remains_an_order_query_not_delivery_tracking():
    orders = FakeOrderClient()
    deliveries = FakeDeliveryClient()
    agent = CustomerAgent(
        retriever=FakeRetriever(), llm_service=FakeLLM(), order_client=orders,
        product_client=FakeProductClient(), delivery_client=deliveries, web_search_service=FakeWebSearch(),
    )

    response = run(agent.handle_query("Where is my order?", user_id=1, token="token"))

    assert "Your latest order status:" in response["answer"]
    assert orders.recent_order_calls == 1
    assert deliveries.calls == []


@pytest.mark.parametrize(
    ("question", "expected_search"),
    [
        ("price of apples", "apples"),
        ("organic apples", "organic apples"),
        ("black grapes", "black grapes"),
        ("lime", "lime"),
        ("show me organic fruits", "organic fruits"),
        ("do you have apples?", "apples"),
        ("what products do you have?", None),
    ],
)
def test_product_questions_route_to_live_product_search_without_llm_or_rag(question, expected_search):
    llm = FakeLLM()
    orders = FakeOrderClient()
    products = FakeProductClient()
    deliveries = FakeDeliveryClient()
    web = FakeWebSearch()
    agent = CustomerAgent(
        retriever=FakeRetriever(),
        llm_service=llm,
        order_client=orders,
        product_client=products,
        delivery_client=deliveries,
        web_search_service=web,
    )

    response = run(agent.handle_query(question, user_id=1, token="token"))

    assert "Organic Apples — ₹120.00 / kg" in response["answer"]
    assert products.search_calls == [expected_search]
    assert products.product_calls == []
    assert orders.calls == 0
    assert deliveries.calls == []
    assert llm.calls == 0
    assert web.calls == 0


def test_product_search_formats_multiple_matching_products():
    products = FakeProductClient(products=[
        {"id": 1, "name": "Organic Apples", "price": "120.00", "stock_quantity": 10, "unit": "kg"},
        {"id": 2, "name": "Organic Green Apples", "price": "150.00", "stock_quantity": 0, "unit": "kg"},
    ])
    agent = CustomerAgent(
        retriever=FakeRetriever(), llm_service=FakeLLM(), order_client=FakeOrderClient(),
        product_client=products, web_search_service=FakeWebSearch(),
    )

    response = run(agent.handle_query("price of apples", user_id=1, token="token"))

    assert "Organic Apples" in response["answer"]
    assert "Organic Green Apples" in response["answer"]
    assert "Out of stock" in response["answer"]


def test_product_search_handles_no_matches():
    products = FakeProductClient(products=[])
    agent = CustomerAgent(
        retriever=FakeRetriever(), llm_service=FakeLLM(), order_client=FakeOrderClient(),
        product_client=products, web_search_service=FakeWebSearch(),
    )

    response = run(agent.handle_query("lime", user_id=1, token="token"))

    assert response["answer"] == "I couldn't find any currently available products matching “lime”."


@pytest.mark.parametrize("error", ["unavailable", "timeout"])
def test_product_search_handles_service_failures(error):
    products = FakeProductClient(error=error)
    agent = CustomerAgent(
        retriever=FakeRetriever(), llm_service=FakeLLM(), order_client=FakeOrderClient(),
        product_client=products, web_search_service=FakeWebSearch(),
    )

    response = run(agent.handle_query("organic apples", user_id=1, token="token"))

    assert response["answer"] == f"Product Service {error}."


@pytest.mark.parametrize(
    "question",
    [
        "What is OrganicKart's order policy?",
        "organic order policies",
    ],
)
def test_order_policy_questions_route_to_rag_not_order_tools(question):
    llm = FakeLLM()
    orders = FakeOrderClient()
    deliveries = FakeDeliveryClient()
    web = FakeWebSearch()
    agent = CustomerAgent(
        retriever=FakeRetriever(),
        llm_service=llm,
        order_client=orders,
        delivery_client=deliveries,
        web_search_service=web,
    )

    response = run(agent.handle_query(question, user_id=1, token="token"))

    assert response["answer"] == "OrganicKart is an organic marketplace."
    assert orders.calls == 0
    assert deliveries.calls == []
    assert llm.calls == 1
    assert web.calls == 0


@pytest.mark.parametrize("question", [
    "What are the latest organic farming practices?",
    "What are the current organic farming trends?",
    "latest organic pineapple prices in India",
])
def test_explicit_current_question_routes_to_web_search(question):
    llm = FakeLLM()
    deliveries = FakeDeliveryClient()
    web = FakeWebSearch([{"title": "Current information", "url": "https://example.test/current", "snippet": "Current web result."}])
    agent = CustomerAgent(retriever=FakeRetriever(), llm_service=llm, order_client=FakeOrderClient(), delivery_client=deliveries, web_search_service=web)
    response = run(agent.handle_query(question))
    assert response["answer"] == "Current web result."
    assert web.calls == 1
    assert llm.calls == 0
    assert deliveries.calls == []


def test_web_search_unavailable_does_not_hallucinate():
    agent = CustomerAgent(
        retriever=FakeRetriever(),
        llm_service=FakeLLM(),
        order_client=FakeOrderClient(),
        web_search_service=FakeWebSearch(error=WebSearchUnavailable("unavailable")),
    )
    response = run(agent.handle_query("What is organic farming?"))
    assert "couldn't access current web information" in response["answer"]
    assert response["sources"] == []


def test_web_search_unavailable_does_not_affect_organickart_rag():
    llm = FakeLLM()
    web = FakeWebSearch(error=WebSearchUnavailable("unavailable"))
    agent = CustomerAgent(
        retriever=FakeRetriever(),
        llm_service=llm,
        order_client=FakeOrderClient(),
        web_search_service=web,
    )
    response = run(agent.handle_query("organic order policies"))
    assert response["answer"] == "OrganicKart is an organic marketplace."
    assert llm.calls == 1
    assert web.calls == 0


@pytest.mark.parametrize("question", [
    "Show my notifications",
    "What are my notifications?",
    "Check my notifications",
    "List my notifications",
])
def test_notification_questions_route_to_live_notification_tool_without_llm_or_rag(question):
    llm = FakeLLM()
    notifications = FakeNotificationClient()
    agent = CustomerAgent(
        retriever=FakeRetriever(),
        llm_service=llm,
        order_client=FakeOrderClient(),
        product_client=FakeProductClient(),
        delivery_client=FakeDeliveryClient(),
        notification_client=notifications,
        web_search_service=FakeWebSearch(),
    )

    response = run(agent.handle_query(question, user_id=1, token="token"))

    assert "Here are your recent notifications:" in response["answer"]
    assert "Delivery #17: OUT_FOR_DELIVERY" in response["answer"]
    assert "Unread count: 1" in response["answer"]
    assert notifications.calls == [("token", 1)]
    assert llm.calls == 0


def test_unread_notification_count_query():
    notifications = FakeNotificationClient()
    agent = CustomerAgent(
        retriever=FakeRetriever(),
        llm_service=FakeLLM(),
        order_client=FakeOrderClient(),
        product_client=FakeProductClient(),
        delivery_client=FakeDeliveryClient(),
        notification_client=notifications,
        web_search_service=FakeWebSearch(),
    )

    response = run(agent.handle_query("How many unread notifications do I have?", user_id=1, token="token"))

    assert response["answer"] == "You have 1 unread notification(s)."
    assert notifications.calls == [("token", 1)]


def test_notification_tool_handles_empty_notifications():
    notifications = FakeNotificationClient(notifications=[])
    agent = CustomerAgent(
        retriever=FakeRetriever(),
        llm_service=FakeLLM(),
        order_client=FakeOrderClient(),
        product_client=FakeProductClient(),
        delivery_client=FakeDeliveryClient(),
        notification_client=notifications,
        web_search_service=FakeWebSearch(),
    )

    response = run(agent.handle_query("Show my notifications", user_id=1, token="token"))

    assert response["answer"] == "You currently have no notifications."


@pytest.mark.parametrize("question", [
    "What are current organic farming practices?",
    "current organic agriculture trends",
    "latest market prices for organic produce",
])
def test_current_organic_farming_and_market_queries_route_to_web_search(question):
    llm = FakeLLM()
    web = FakeWebSearch([{"title": "Organic Trends", "url": "https://example.test/trends", "snippet": "Latest organic trends snippet."}])
    agent = CustomerAgent(
        retriever=FakeRetriever(),
        llm_service=llm,
        order_client=FakeOrderClient(),
        product_client=FakeProductClient(),
        delivery_client=FakeDeliveryClient(),
        notification_client=FakeNotificationClient(),
        web_search_service=web,
    )

    response = run(agent.handle_query(question))

    assert "Latest organic trends snippet." in response["answer"]
    assert web.calls == 1
    assert llm.calls == 0

