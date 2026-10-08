import re
import logging
from decimal import Decimal, InvalidOperation
from time import perf_counter
from typing import Any

from app.rag.retriever import RAGRetriever
from app.services.llm_service import LLMService
from app.services.web_search_service import WebSearchService, WebSearchUnavailable
from app.tools.delivery_tools import DeliveryServiceClient
from app.tools.notification_tools import NotificationServiceClient
from app.tools.order_tools import OrderServiceClient
from app.tools.product_tools import ProductServiceClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are OrganicKart's AI Customer Assistant.
Your goal is to answer customer questions accurately and completely using ONLY the provided OrganicKart knowledge context.

Rules:
1. Read the full context carefully before responding.
2. If the context lists product categories, types, or items — enumerate them clearly in your answer.
3. If the context does not contain sufficient information to answer the question, respond with:
   "I'm sorry, I don't have information about that in the OrganicKart knowledge base. I can help with organic products, delivery, quality standards, and customer policies."
4. Do NOT speculate, invent prices, invent stock levels, or add details not present in the context.
5. Keep your answer helpful and concise: use 2–5 sentences or brief bullets.
"""

ORDER_SERVICE_SOURCE = [{"document": "Order Service API", "title": "Order Service", "score": 1.0}]
CART_SERVICE_SOURCE = [{"document": "Order Service Cart API", "title": "Your Cart", "score": 1.0}]
PRODUCT_SERVICE_SOURCE = [{"document": "Product Service API", "title": "Product Catalog", "score": 1.0}]
DELIVERY_SERVICE_SOURCE = [{"document": "Delivery Service API", "title": "Delivery Tracking", "score": 1.0}]
NOTIFICATION_SERVICE_SOURCE = [{"document": "Notification Service API", "title": "Notifications", "score": 1.0}]


class CustomerAgent:
    """
    Role-specific Assistant for OrganicKart CUSTOMER users.
    Supports RAG for knowledge base questions and Order Tools for live order data.
    """

    def __init__(
        self,
        retriever: RAGRetriever | None = None,
        llm_service: LLMService | None = None,
        order_client: OrderServiceClient | None = None,
        product_client: ProductServiceClient | None = None,
        delivery_client: DeliveryServiceClient | None = None,
        notification_client: NotificationServiceClient | None = None,
        web_search_service: WebSearchService | None = None,
    ):
        self.retriever = retriever or RAGRetriever()
        self.llm_service = llm_service or LLMService()
        self.order_client = order_client or OrderServiceClient()
        self.product_client = product_client or ProductServiceClient()
        self.delivery_client = delivery_client or DeliveryServiceClient()
        self.notification_client = notification_client or NotificationServiceClient()
        self.web_search_service = web_search_service or WebSearchService()

    @staticmethod
    def _to_decimal(value: Any) -> Decimal:
        """Safely convert JSON monetary values from Order Service to Decimal."""
        try:
            if value is None or isinstance(value, bool):
                return Decimal("0")
            if isinstance(value, Decimal):
                amount = value
            elif isinstance(value, (int, float)):
                amount = Decimal(str(value))
            elif isinstance(value, str):
                amount = Decimal(value.strip()) if value.strip() else Decimal("0")
            else:
                return Decimal("0")

            if not amount.is_finite():
                return Decimal("0")
            return amount
        except (InvalidOperation, TypeError, ValueError):
            return Decimal("0")

    @classmethod
    def _format_currency(cls, value: Any) -> str:
        """Format Order Service monetary values safely, including JSON strings."""
        amount = cls._to_decimal(value)

        return f"₹{amount:.2f}"

    def _extract_order_id(self, query: str) -> int | None:
        """
        Extract numeric order ID from user query if present.
        Examples: 'order 123', 'order #123', 'status of order 45', '#123'
        """
        match = re.search(r"(?:order\s*(?:id|#)?\s*|status\s+of\s+order\s*#?\s*|#)(\d+)", query, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
        return None

    def _is_live_order_query(self, query: str) -> tuple[bool, str, int | None]:
        """
        Determine if query requires live order data.
        Returns tuple: (is_order_query, intent_type, order_id)
        intent_type can be: 'ORDER_BY_ID', 'ORDER_STATUS', 'RECENT_ORDERS'
        """
        # Normalize whitespace before matching so natural-language phrasing is
        # routed consistently without involving the LLM.
        q = " ".join(query.lower().split())
        # Explicit delivery/tracking questions must not be swallowed by broad
        # order-history phrases such as "my orders".
        if self._is_live_delivery_query(q):
            return False, "NONE", None
        order_id = self._extract_order_id(q)
        if order_id is not None:
            return True, "ORDER_BY_ID", order_id

        order_status_patterns = [
            r"\b(?:what\s+is\s+)?(?:the\s+)?status\s+(?:of\s+)?my\s+order\b",
            r"\bmy\s+order\s+status\b",
            r"\bwhere\s+is\s+my\s+order\b",
            r"\btrack\s+my\s+order\b",
            r"\btrack\s+order\b",
            r"\border\s+status\b",
            r"\bstatus\s+of\s+(?:my\s+)?order\b",
            r"\bis\s+my\s+order\b(?!\s+out\s+for\s+delivery\b)",
        ]
        for pattern in order_status_patterns:
            if re.search(pattern, q):
                return True, "ORDER_STATUS", None

        recent_order_patterns = [
            r"\brecent\s+orders?\b",
            r"\blatest\s+orders?\b",
            r"\border\s+history\b",
            r"\bpast\s+orders?\b",
            r"\bshow\s+(?:my\s+)?orders?\b",
            r"\blist\s+(?:my\s+)?orders?\b",
            r"\bmy\s+orders?\b",
            r"\bprevious\s+orders?\b",
        ]
        for pattern in recent_order_patterns:
            if re.search(pattern, q):
                return True, "RECENT_ORDERS", None

        return False, "NONE", None

    @staticmethod
    def _is_live_cart_query(query: str) -> bool:
        """Detect authenticated customer cart questions without an LLM call."""
        q = " ".join(query.lower().split())
        patterns = (
            r"\bproducts?\s+in\s+my\s+cart\b",
            r"\bwhat(?:'|’)s\s+in\s+my\s+cart\b",
            r"\bshow\s+my\s+cart\b",
            r"\bwhat\s+items?\s+are\s+in\s+my\s+cart\b",
            r"\bhow\s+many\s+items?\s+are\s+in\s+my\s+cart\b",
            r"\bwhat(?:'|’)s\s+my\s+cart\s+total\b",
            r"\bmy\s+cart\s+total\b",
        )
        return any(re.search(pattern, q) for pattern in patterns)

    @staticmethod
    def _extract_product_id(query: str) -> int | None:
        match = re.search(r"\bproduct\s*(?:id|#)\s*(\d+)\b", query, re.IGNORECASE)
        return int(match.group(1)) if match else None

    def _live_product_query(self, query: str) -> tuple[bool, int | None, str | None]:
        """Return whether a query needs live catalog data and its search value."""
        q = " ".join(query.lower().split())
        product_id = self._extract_product_id(q)
        if product_id is not None:
            return True, product_id, None

        if re.search(r"\bwhat\s+products?\s+(?:do\s+you\s+have|are\s+available)\b", q):
            return True, None, None

        match = re.search(r"\b(?:price|cost)\s+(?:of|for)\s+(.+)$", q)
        if not match:
            match = re.search(r"\b(?:do\s+you\s+have|show\s+me|do\s+you\s+sell)\s+(.+)$", q)
        if match:
            term = re.sub(r"[?.!]+$", "", match.group(1)).strip()
            return (True, None, term) if term else (False, None, None)

        # Short product-name searches, while excluding policy and general-web terms.
        if re.fullmatch(r"(?:organic\s+)?[a-z]+(?:\s+[a-z]+)?", q) and not re.search(
            r"\b(?:farming|policy|policies|order|orders|delivery|return|refund|quality|standards?)\b", q
        ):
            return True, None, q
        return False, None, None

    @staticmethod
    def _is_live_delivery_query(query: str) -> bool:
        """Only delivery/tracking phrases use the live Delivery Service."""
        q = " ".join(query.lower().split())
        patterns = (
            r"\bwhere\s+is\s+my\s+delivery\b",
            r"\btrack\s+my\s+delivery\b",
            r"\b(?:what\s+is\s+)?my\s+delivery\s+status\b",
            r"\bwhen\s+will\s+my\s+delivery\s+arrive\b",
            r"\bhas\s+my\s+(?:order|delivery)\s+been\s+dispatched\b",
            r"\bis\s+my\s+(?:order|delivery)\s+dispatched\b",
            r"\bis\s+my\s+(?:order|delivery)\s+out\s+for\s+delivery\b",
            r"\bis\s+my\s+(?:order|delivery)\s+on\s+the\s+way\b",
        )
        return any(re.search(pattern, q) for pattern in patterns)

    @staticmethod
    def _is_live_notification_query(query: str) -> bool:
        """Detect customer notification queries."""
        q = " ".join(query.lower().split())
        patterns = (
            r"\bmy\s+notifications?\b",
            r"\bshow\s+(?:my\s+)?notifications?\b",
            r"\bcheck\s+(?:my\s+)?notifications?\b",
            r"\blist\s+(?:my\s+)?notifications?\b",
            r"\bwhat\s+are\s+my\s+notifications?\b",
            r"\bunread\s+notifications?\b",
            r"\bdo\s+i\s+have\s+(?:any\s+)?(?:new|unread)\s+notifications?\b",
            r"\bhow\s+many\s+(?:new|unread)\s+notifications?\b",
        )
        return any(re.search(pattern, q) for pattern in patterns)

    @staticmethod
    def _is_organickart_knowledge_query(query: str) -> bool:
        q = query.lower()
        # A current-market request such as "latest organic pineapple prices"
        # is external information, unless it explicitly names OrganicKart or
        # asks about one of its policies.
        if CustomerAgent._is_current_web_query(q) and not re.search(
            r"\borganickart\b|\b(?:organic\s+)?(?:order|delivery|return|refund|customer)\s+polic(?:y|ies)\b",
            q,
        ):
            return False
        patterns = (
            r"\borganickart\b",
            r"\b(?:your|organickart(?:'s)?)\s+(?:delivery|return|refund|quality|customer|order)\s+polic(?:y|ies)\b",
            r"\b(?:organic\s+)?(?:order|delivery|return|refund|customer)\s+polic(?:y|ies)\b",
            r"\b(?:your|organickart(?:'s)?)\s+quality\s+standards?\b",
            r"\b(?:your|organickart(?:'s)?)\s+(?:organic\s+)?products?\b",
            r"\b(?:what|which)\s+products?\s+(?:do\s+you\s+have|are\s+available)\b",
            r"\bdo\s+you\s+sell\b",
            r"\borganic\s+(?:pineapples?|vegetables?|fruits?|produce|products?)\b",
            r"\bhow\s+(?:does\s+)?organickart\s+work\b",
        )
        return any(re.search(pattern, q) for pattern in patterns)

    @staticmethod
    def _is_current_web_query(query: str) -> bool:
        """Only explicit external/current-information requests use web search."""
        q = query.lower()
        patterns = (
            r"\b(?:latest|current|recent)\b.*\b(?:farming|agriculture|trend|trends|news|price|prices|market|standards?|methods?|practices?)\b",
            r"\b(?:farming|agriculture|trend|trends|news|price|prices|market|standards?|methods?|practices?)\b.*\b(?:latest|current|recent)\b",
            r"\bwhat\s+is\s+organic\s+farming\b",
            r"\bbenefits?\s+of\s+(?:eating\s+)?organic\b",
        )
        return any(re.search(pattern, q) for pattern in patterns)

    async def _handle_live_order_tool(
        self,
        intent: str,
        order_id: int | None,
        user_id: int | None,
        token: str | None,
    ) -> dict[str, Any]:
        """
        Execute Order Service tool calls and format clean customer responses.
        """
        if not token or not user_id:
            return {
                "answer": "Authentication is required to view live order details.",
                "sources": [],
            }

        if intent == "ORDER_BY_ID" and order_id is not None:
            res = await self.order_client.get_order_by_id(order_id, token, user_id)
            if not res["success"]:
                return {
                    "answer": res["detail"],
                    "sources": ORDER_SERVICE_SOURCE,
                }

            order = res["order"]
            items_str = ""
            if order.get("items"):
                item_lines = [
                    f"  • {item['product_name']} x {item['quantity']} ({self._format_currency(item.get('subtotal'))})"
                    for item in order["items"]
                ]
                items_str = "\n" + "\n".join(item_lines)

            answer = (
                f"Order #{order['id']} Status:\n"
                f"• Status: {order.get('status')}\n"
                f"• Payment Status: {order.get('payment_status')}\n"
                f"• Total Amount: {self._format_currency(order.get('total_amount'))}\n"
                f"• Shipping Address: {order.get('shipping_address', 'N/A')}\n"
                f"• Date Placed: {order.get('created_at', 'N/A')[:10] if order.get('created_at') else 'N/A'}"
            )
            if items_str:
                answer += f"\n• Items:\n{items_str}"

            return {"answer": answer, "sources": ORDER_SERVICE_SOURCE}

        if intent == "ORDER_STATUS":
            res = await self.order_client.get_recent_orders(token, user_id)
            if not res["success"]:
                return {
                    "answer": res["detail"],
                    "sources": ORDER_SERVICE_SOURCE,
                }

            orders = res["orders"]
            if not orders:
                return {
                    "answer": "You currently have no orders placed with OrganicKart.",
                    "sources": ORDER_SERVICE_SOURCE,
                }

            latest = orders[0]
            items_summary = ", ".join([f"{item['product_name']} (x{item['quantity']})" for item in latest.get("items", [])])
            if not items_summary:
                items_summary = "N/A"

            answer = (
                f"Your latest order status:\n\n"
                f"• Order #{latest['id']}\n"
                f"• Status: {latest.get('status')}\n"
                f"• Payment Status: {latest.get('payment_status')}\n"
                f"• Total Amount: {self._format_currency(latest.get('total_amount'))}\n"
                f"• Date: {latest.get('created_at', 'N/A')[:10] if latest.get('created_at') else 'N/A'}\n"
                f"• Items: {items_summary}"
            )
            return {"answer": answer, "sources": ORDER_SERVICE_SOURCE}

        if intent == "RECENT_ORDERS":
            res = await self.order_client.get_recent_orders(token, user_id)
            if not res["success"]:
                return {
                    "answer": res["detail"],
                    "sources": ORDER_SERVICE_SOURCE,
                }

            orders = res["orders"]
            if not orders:
                return {
                    "answer": "You currently have no past orders in your OrganicKart account.",
                    "sources": ORDER_SERVICE_SOURCE,
                }

            lines = ["Here are your recent OrganicKart orders:\n"]
            for o in orders[:5]:
                items_summary = ", ".join([f"{item['product_name']} (x{item['quantity']})" for item in o.get("items", [])])
                lines.append(
                    f"• Order #{o['id']}\n"
                    f"  Status: {o.get('status')} | Payment: {o.get('payment_status')}\n"
                    f"  Total: {self._format_currency(o.get('total_amount'))} | Date: {o.get('created_at', 'N/A')[:10] if o.get('created_at') else 'N/A'}\n"
                    f"  Items: {items_summary if items_summary else 'N/A'}\n"
                )

            return {"answer": "\n".join(lines).strip(), "sources": ORDER_SERVICE_SOURCE}

        return {
            "answer": "Unable to process order query.",
            "sources": [],
        }

    async def _handle_live_cart_tool(self, user_id: int | None, token: str | None) -> dict[str, Any]:
        """Fetch and format only the authenticated customer's live cart."""
        if not token or not user_id:
            return {
                "answer": "Authentication is required to view your cart.",
                "sources": [],
            }

        res = await self.order_client.get_my_cart(token, user_id)
        if not res["success"]:
            return {"answer": res["detail"], "sources": CART_SERVICE_SOURCE}

        items = res["cart"]["items"]
        if not items:
            return {"answer": "Your cart is currently empty.", "sources": CART_SERVICE_SOURCE}

        lines = ["Your cart contains:"]
        total_items = 0
        total_amount = Decimal("0")
        for item in items:
            quantity = item.get("quantity", 0)
            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                quantity = 0
            unit_price = self._to_decimal(item.get("unit_price"))
            total_items += max(quantity, 0)
            total_amount += unit_price * max(quantity, 0)
            unit_suffix = f" / {item['unit']}" if item.get("unit") else ""
            lines.append(
                f"• {item.get('product_name', 'Product')} × {quantity} — "
                f"{self._format_currency(unit_price)}{unit_suffix}"
            )

        lines.extend([
            f"Total quantity: {total_items}",
            f"Cart total: {self._format_currency(total_amount)}",
        ])
        return {"answer": "\n".join(lines), "sources": CART_SERVICE_SOURCE}

    def _format_product(self, product: dict[str, Any]) -> str:
        name = product.get("name", "Product")
        unit = f" / {product['unit']}" if product.get("unit") else ""
        stock = product.get("stock_quantity")
        if isinstance(stock, int):
            availability = f"In stock ({stock} available)" if stock > 0 else "Out of stock"
        else:
            availability = "Availability not provided"
        category = product.get("category")
        category_name = category.get("name") if isinstance(category, dict) else None
        lines = [f"• {name} — {self._format_currency(product.get('price'))}{unit}", f"  Availability: {availability}"]
        if category_name:
            lines.append(f"  Category: {category_name}")
        if product.get("certification"):
            lines.append(f"  Certification: {product['certification']}")
        return "\n".join(lines)

    async def _handle_live_product_tool(self, product_id: int | None, search: str | None) -> dict[str, Any]:
        if product_id is not None:
            result = await self.product_client.get_product(product_id)
            if not result["success"]:
                return {"answer": result["detail"], "sources": PRODUCT_SERVICE_SOURCE}
            return {"answer": self._format_product(result["product"]), "sources": PRODUCT_SERVICE_SOURCE}

        result = await self.product_client.search_products(search)
        if not result["success"]:
            return {"answer": result["detail"], "sources": PRODUCT_SERVICE_SOURCE}
        products = result["products"]
        if not products:
            suffix = f" matching “{search}”" if search else ""
            return {"answer": f"I couldn't find any currently available products{suffix}.", "sources": PRODUCT_SERVICE_SOURCE}

        heading = "Currently available products:" if not search else f"Products matching “{search}”:"
        lines = [heading, *[self._format_product(product) for product in products[:5]]]
        if len(products) > 5:
            lines.append(f"Showing 5 of {len(products)} matching products.")
        return {"answer": "\n".join(lines), "sources": PRODUCT_SERVICE_SOURCE}

    async def _handle_live_delivery_tool(
        self,
        user_id: int | None,
        token: str | None,
        query: str = "",
    ) -> dict[str, Any]:
        if not token or not user_id:
            return {"answer": "Authentication is required to view delivery tracking.", "sources": []}

        result = await self.delivery_client.get_my_deliveries(token, user_id)
        if not result["success"]:
            return {"answer": result["detail"], "sources": DELIVERY_SERVICE_SOURCE}
        deliveries = result["deliveries"]
        if not deliveries:
            return {"answer": "There is no delivery tracking information available for your account yet.", "sources": DELIVERY_SERVICE_SOURCE}

        delivery = deliveries[0]
        delivery_id = delivery.get("id", "N/A")
        order_id = delivery.get("order_id", "N/A")
        status = str(delivery.get("status", "PENDING")).upper()
        tracking_number = delivery.get("tracking_number", "N/A")

        q = " ".join(query.lower().split())
        is_out_for_delivery_query = bool(
            re.search(r"\b(?:is\s+my\s+(?:order|delivery)\s+(?:out\s+for\s+delivery|on\s+the\s+way))\b", q)
        )
        is_dispatched_query = bool(
            re.search(
                r"\b(?:has\s+my\s+(?:order|delivery)\s+been\s+dispatched|is\s+my\s+(?:order|delivery)\s+dispatched)\b",
                q,
            )
        )

        if is_out_for_delivery_query:
            if status == "OUT_FOR_DELIVERY":
                header = "Yes, your order is out for delivery."
            elif status == "DELIVERED":
                header = "Your order has already been delivered."
            else:
                header = "No, your order is not out for delivery yet."

            lines = [
                header,
                "",
                f"• Delivery #{delivery_id}",
                f"• Order #{order_id}",
                f"• Current status: {status}",
                f"• Tracking number: {tracking_number}",
            ]
        elif is_dispatched_query:
            shipped_statuses = {"PICKED_UP", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED"}
            if status in shipped_statuses or delivery.get("shipped_at"):
                header = "Yes, your order has been dispatched."
            else:
                header = "No, your order has not been dispatched yet."

            lines = [
                header,
                "",
                f"• Delivery #{delivery_id}",
                f"• Order #{order_id}",
                f"• Current status: {status}",
                f"• Tracking number: {tracking_number}",
            ]
        else:
            lines = [
                "Your latest delivery:",
                f"• Delivery #{delivery_id}",
                f"• Order #{order_id}",
                f"• Status: {status}",
                f"• Tracking number: {tracking_number}",
            ]

        if delivery.get("estimated_delivery_date"):
            lines.append(f"• Estimated delivery: {str(delivery['estimated_delivery_date'])[:10]}")
        if delivery.get("shipped_at"):
            lines.append(f"• Dispatched: {str(delivery['shipped_at'])[:10]}")
        if delivery.get("delivered_at"):
            lines.append(f"• Delivered: {str(delivery['delivered_at'])[:10]}")
        return {"answer": "\n".join(lines), "sources": DELIVERY_SERVICE_SOURCE}

    async def _handle_live_notification_tool(
        self,
        user_id: int | None,
        token: str | None,
        query: str = "",
    ) -> dict[str, Any]:
        if not token or not user_id:
            return {"answer": "Authentication is required to view notifications.", "sources": []}

        result = await self.notification_client.get_my_notifications(token, user_id)
        if not result["success"]:
            return {"answer": result["detail"], "sources": NOTIFICATION_SERVICE_SOURCE}

        notifications = result["notifications"]
        if not notifications:
            return {"answer": "You currently have no notifications.", "sources": NOTIFICATION_SERVICE_SOURCE}

        unread_count = sum(1 for n in notifications if str(n.get("status", "")).upper() != "READ")
        q = " ".join(query.lower().split())
        is_unread_count_query = bool(
            re.search(
                r"\bhow\s+many\s+(?:new|unread)\s+notifications?\b|\bunread\s+notification\s+count\b|\bcount\s+of\s+unread\s+notifications?\b",
                q,
            )
        )

        if is_unread_count_query:
            if unread_count == 0:
                answer = "You have no unread notifications."
            else:
                answer = f"You have {unread_count} unread notification(s)."
            return {"answer": answer, "sources": NOTIFICATION_SERVICE_SOURCE}

        lines = ["Here are your recent notifications:\n"]
        for n in notifications[:5]:
            status_label = "UNREAD" if str(n.get("status", "")).upper() != "READ" else "READ"
            title = n.get("title", "Notification")
            msg = n.get("message", "")
            lines.append(f"• [{status_label}] {title} — {msg}")

        lines.append(f"\nUnread count: {unread_count}")
        return {"answer": "\n".join(lines), "sources": NOTIFICATION_SERVICE_SOURCE}

    async def _handle_web_query(self, query: str) -> dict[str, Any]:
        try:
            results = await self.web_search_service.search(query)
        except WebSearchUnavailable:
            return {
                "answer": "I couldn't access current web information right now. Please try again shortly.",
                "sources": [],
            }

        if not results:
            return {
                "answer": "I couldn't find reliable current web information for that question.",
                "sources": [],
            }

        snippets = [result["snippet"] for result in results if result.get("snippet")]
        answer = "\n\n".join(snippets[:2])
        sources = [
            {"document": "Web Search", "title": result["title"], "url": result["url"], "score": None}
            for result in results
        ]
        return {"answer": answer, "sources": sources}

    async def _handle_rag_query(self, query: str, started_at: float) -> dict[str, Any]:
        retrieval_started_at = perf_counter()
        retrieval_data = self.retriever.retrieve(query)
        retrieval_duration = perf_counter() - retrieval_started_at
        context_text = retrieval_data.get("context", "")
        sources = retrieval_data.get("sources", [])

        if not context_text:
            logger.info("AI route=rag retrieval=%.3fs llm=0s total=%.3fs", retrieval_duration, perf_counter() - started_at)
            return {
                "answer": "I'm sorry, I don't have information about that in the OrganicKart knowledge base. I can help with organic products, delivery, quality standards, and customer policies.",
                "sources": [],
            }

        user_prompt = f"""OrganicKart Knowledge Context:
{context_text}

Customer Question:
{query}

Answer using only the above OrganicKart context:"""

        llm_started_at = perf_counter()
        answer = await self.llm_service.generate(user_prompt, system_prompt=SYSTEM_PROMPT)
        logger.info(
            "AI route=rag retrieval=%.3fs llm=%.3fs total=%.3fs",
            retrieval_duration,
            perf_counter() - llm_started_at,
            perf_counter() - started_at,
        )
        return {"answer": answer, "sources": sources}

    async def handle_query(
        self,
        query: str,
        user_id: int | None = None,
        token: str | None = None,
    ) -> dict[str, Any]:
        """
        Deterministically route order data, OrganicKart knowledge, explicit web queries, then RAG fallback.
        """
        started_at = perf_counter()
        is_order, intent, order_id = self._is_live_order_query(query)
        if is_order:
            logger.warning(
                "AI_CHAT_TRACE step=route user_id=%s route=order intent=%s order_id=%s",
                user_id,
                intent,
                order_id,
            )
            response = await self._handle_live_order_tool(intent, order_id, user_id, token)
            logger.info("AI route=order duration=%.3fs", perf_counter() - started_at)
            return response

        if self._is_live_cart_query(query):
            logger.info("AI route=cart user_id=%s", user_id)
            response = await self._handle_live_cart_tool(user_id, token)
            logger.info("AI route=cart duration=%.3fs", perf_counter() - started_at)
            return response

        is_product, product_id, search = self._live_product_query(query)
        if is_product:
            response = await self._handle_live_product_tool(product_id, search)
            logger.info("AI route=product duration=%.3fs", perf_counter() - started_at)
            return response

        if self._is_live_delivery_query(query):
            response = await self._handle_live_delivery_tool(user_id, token, query)
            logger.info("AI route=delivery duration=%.3fs", perf_counter() - started_at)
            return response

        if self._is_live_notification_query(query):
            response = await self._handle_live_notification_tool(user_id, token, query)
            logger.info("AI route=notification duration=%.3fs", perf_counter() - started_at)
            return response

        if self._is_organickart_knowledge_query(query):
            return await self._handle_rag_query(query, started_at)

        if self._is_current_web_query(query):
            web_started_at = perf_counter()
            response = await self._handle_web_query(query)
            logger.info("AI route=web search=%.3fs llm=0s total=%.3fs", perf_counter() - web_started_at, perf_counter() - started_at)
            return response

        return await self._handle_rag_query(query, started_at)
