import re
from decimal import Decimal, InvalidOperation
from time import perf_counter
from typing import Any

from app.config import settings
from app.rag.retriever import RAGRetriever
from app.services.llm_service import LLMService
from app.tools.admin_order_tools import AdminOrderServiceClient
from app.tools.product_tools import ProductServiceClient


ADMIN_SYSTEM_PROMPT = """You are OrganicKart's AI Admin Assistant.
Answer only from the supplied OrganicKart admin knowledge context.
Use supplied live catalog and aggregate order information only when available.
Do not expose customer personal information.
Keep answers concise and professional.
"""

ADMIN_PRODUCT_SOURCE = [{"document": "Product Service Admin Catalog API", "title": "Admin Product Catalog", "score": 1.0}]
ADMIN_ORDER_SOURCE = [{"document": "Order Service Admin Analytics API", "title": "Admin Order Analytics", "score": 1.0}]


class AdminAgent:
    """ADMIN-only assistant with read-only catalog data and RAG fallback."""

    def __init__(
        self,
        retriever: RAGRetriever | None = None,
        llm_service: LLMService | None = None,
        product_client: ProductServiceClient | None = None,
        order_client: AdminOrderServiceClient | None = None,
    ):
        self.retriever = retriever or RAGRetriever(
            vector_store_path=settings.ADMIN_VECTOR_STORE_PATH,
            knowledge_base_dir=settings.ADMIN_KNOWLEDGE_BASE_DIR,
        )
        self.llm_service = llm_service or LLMService()
        self.product_client = product_client or ProductServiceClient()
        self.order_client = order_client or AdminOrderServiceClient()

    @staticmethod
    def _order_analytics_intent(query: str) -> str:
        q = " ".join(query.lower().split())
        if re.search(r"\b(?:show\s+)?(?:recent|latest)\s+orders?\b", q):
            return "RECENT_ORDERS"
        if re.search(r"\b(?:sales\s+statistics|total\s+sales|monthly\s+sales|sales\s+this\s+month|monthly\s+revenue|how\s+much\s+revenue|revenue)\b", q):
            return "SALES_ANALYTICS"
        if re.search(
            r"\b(?:order\s+statistics|how\s+many\s+orders?|total\s+orders?|order\s+count|order\s+status\s+breakdown|today'?s\s+order\s+statistics|how\s+many\s+orders?\s+(?:were\s+)?cancelled|how\s+many\s+orders?\s+are\s+pending)\b",
            q,
        ):
            return "ORDER_STATISTICS"
        return "NONE"

    @staticmethod
    def _business_insights_intent(query: str) -> str:
        q = " ".join(query.lower().split())
        if re.search(r"\b(?:highest\s+selling\s+vendors?|which\s+vendor\s+has\s+the\s+highest\s+sales|top\s+vendors?|vendor\s+sales|compare\s+vendor\s+(?:sales|performance))\b", q):
            return "VENDOR_SALES_INSIGHTS"
        if re.search(r"\b(?:which\s+products?\s+sell\s+the\s+most|best\s+selling\s+products?|top\s+selling\s+products?|product\s+sales)\b", q):
            return "PRODUCT_SALES_INSIGHTS"
        if re.search(r"\b(?:low\s+stock\s+products?|which\s+products?\s+need\s+restocking|show\s+products?\s+running\s+low)\b", q):
            return "LOW_STOCK_INSIGHTS"
        if re.search(r"\b(?:sales\s+declining|which\s+products?\s+have\s+declining\s+sales|products?\s+with\s+declining\s+sales|which\s+products?\s+are\s+performing\s+poorly)\b", q):
            return "SALES_DECLINE_INSIGHTS"
        return "NONE"

    @staticmethod
    def _format_currency(value: Any) -> str:
        try:
            return f"₹{Decimal(str(value if value is not None else 0)).quantize(Decimal('0.01'))}"
        except (InvalidOperation, ValueError, TypeError):
            return "N/A"

    async def _handle_order_analytics_query(self, intent: str, token: str | None) -> dict[str, Any]:
        result = await self.order_client.get_order_analytics(token)
        if not result["success"]:
            return {"answer": result["detail"], "sources": ADMIN_ORDER_SOURCE}

        analytics = result["analytics"]
        total_orders = analytics["total_orders"]
        if total_orders == 0:
            return {"answer": "No orders are available yet.", "sources": ADMIN_ORDER_SOURCE}

        if intent == "RECENT_ORDERS":
            recent_orders = analytics.get("recent_orders")
            if not isinstance(recent_orders, list) or not recent_orders:
                return {"answer": "No recent orders are available yet.", "sources": ADMIN_ORDER_SOURCE}
            lines = ["Recent orders:"]
            for order in recent_orders[:10]:
                if not isinstance(order, dict):
                    continue
                lines.append(
                    f"• Order #{order.get('order_id', 'N/A')} — {order.get('status', 'N/A')} "
                    f"| Payment: {order.get('payment_status', 'N/A')} "
                    f"| Items: {order.get('items_count', 'N/A')} "
                    f"| Total: {self._format_currency(order.get('total_amount'))}"
                )
            return {"answer": "\n".join(lines), "sources": ADMIN_ORDER_SOURCE}

        if intent == "SALES_ANALYTICS":
            lines = [
                "Sales analytics:",
                f"• Paid, non-cancelled revenue: {self._format_currency(analytics.get('total_revenue'))}",
            ]
            monthly = analytics.get("monthly_sales_summary")
            if isinstance(monthly, list) and monthly:
                lines.append("• Monthly sales:")
                for entry in monthly[:12]:
                    if isinstance(entry, dict):
                        lines.append(
                            f"  • {entry.get('month', 'N/A')}: {entry.get('orders', 'N/A')} orders, "
                            f"{self._format_currency(entry.get('revenue'))}"
                        )
            return {"answer": "\n".join(lines), "sources": ADMIN_ORDER_SOURCE}

        lines = [f"Order statistics:\n• Total orders: {total_orders}"]
        statuses = analytics.get("orders_by_status")
        if isinstance(statuses, dict):
            for status_name, count in sorted(statuses.items()):
                lines.append(f"• {status_name}: {count}")
        lines.append(f"• Cancelled: {analytics.get('cancelled_orders', 0)}")
        payment_statuses = analytics.get("payment_status_breakdown")
        if isinstance(payment_statuses, dict) and payment_statuses:
            lines.append("• Payment status:")
            for status_name, count in sorted(payment_statuses.items()):
                lines.append(f"  • {status_name}: {count}")
        return {"answer": "\n".join(lines), "sources": ADMIN_ORDER_SOURCE}

    async def _handle_business_insights_query(self, intent: str, token: str | None) -> dict[str, Any]:
        if intent == "LOW_STOCK_INSIGHTS":
            result = await self.product_client.get_admin_low_stock_products(token)
            if not result["success"]:
                return {"answer": result["detail"], "sources": ADMIN_PRODUCT_SOURCE}
            products = result["products"]
            if not products:
                return {
                    "answer": f"No active products are at or below the low-stock threshold of {result['threshold']}.",
                    "sources": ADMIN_PRODUCT_SOURCE,
                }
            lines = [f"Active products at or below {result['threshold']} units:"]
            for product in products[:10]:
                lines.append(
                    f"• Product #{product.get('id', 'N/A')} — {product.get('name', 'N/A')} "
                    f"| Stock: {product.get('stock_quantity', 'N/A')} {product.get('unit', '')} "
                    f"| Seller #{product.get('seller_id', 'N/A')} "
                    f"| Certification: {product.get('certification', 'N/A')} "
                    f"| Active: {'Yes' if product.get('is_active') else 'No'}"
                )
            return {"answer": "\n".join(lines), "sources": ADMIN_PRODUCT_SOURCE}

        result = await self.order_client.get_business_insights(token)
        if not result["success"]:
            return {"answer": result["detail"], "sources": ADMIN_ORDER_SOURCE}
        insights = result["insights"]

        if intent == "VENDOR_SALES_INSIGHTS":
            vendors = insights["vendor_sales"]
            if not vendors:
                return {"answer": "No paid, non-cancelled vendor sales are available yet.", "sources": ADMIN_ORDER_SOURCE}
            lines = ["Vendor sales (paid, non-cancelled orders):"]
            for vendor in vendors:
                if isinstance(vendor, dict):
                    lines.append(
                        f"• Seller #{vendor.get('seller_id', 'N/A')} — {self._format_currency(vendor.get('revenue'))} "
                        f"| {vendor.get('units_sold', 'N/A')} units | {vendor.get('orders_count', 'N/A')} orders"
                    )
            return {"answer": "\n".join(lines), "sources": ADMIN_ORDER_SOURCE}

        if intent == "PRODUCT_SALES_INSIGHTS":
            products = insights["product_sales"]
            if not products:
                return {"answer": "No paid, non-cancelled product sales are available yet.", "sources": ADMIN_ORDER_SOURCE}
            lines = ["Best-selling products (paid, non-cancelled orders):"]
            for product in products:
                if isinstance(product, dict):
                    lines.append(
                        f"• Product #{product.get('product_id', 'N/A')} — {product.get('product_name', 'N/A')} "
                        f"| {product.get('units_sold', 'N/A')} units | {self._format_currency(product.get('revenue'))}"
                    )
            return {"answer": "\n".join(lines), "sources": ADMIN_ORDER_SOURCE}

        if not insights["sales_decline_available"]:
            return {
                "answer": (
                    f"There is insufficient paid order history to compare {insights['current_period']} with "
                    f"{insights['previous_period']}."
                ),
                "sources": ADMIN_ORDER_SOURCE,
            }
        declines = insights["sales_declines"]
        if not declines:
            return {
                "answer": (
                    f"No products have declining paid sales when comparing {insights['current_period']} with "
                    f"{insights['previous_period']}."
                ),
                "sources": ADMIN_ORDER_SOURCE,
            }
        lines = [f"Product sales declines: {insights['current_period']} vs {insights['previous_period']}"]
        for product in declines:
            if isinstance(product, dict):
                lines.append(
                    f"• Product #{product.get('product_id', 'N/A')} — {product.get('product_name', 'N/A')} "
                    f"| {product.get('previous_period_quantity', 'N/A')} → {product.get('current_period_quantity', 'N/A')} units "
                    f"({product.get('percentage_change', 'N/A')}%)"
                )
        return {"answer": "\n".join(lines), "sources": ADMIN_ORDER_SOURCE}

    @staticmethod
    def _catalog_intent(query: str) -> tuple[str, str | int | None]:
        q = " ".join(query.lower().split())
        product_match = re.search(r"\bproduct\s*(?:id|#)\s*(\d+)\b", q)
        if product_match:
            return "PRODUCT_DETAIL", int(product_match.group(1))
        pending_certification_patterns = (
            r"\bshow\s+pending\s+certifications?\b",
            r"\bwhich\s+products?\s+(?:are\s+)?waiting\s+for\s+approval\b",
            r"\bhow\s+many\s+products?\s+are\s+pending\s+certification\b",
            r"\bshow\s+pending\s+products?\b",
            r"\bgive\s+me\s+the\s+pending\s+certification\s+list\b",
            r"\bwhich\s+products?\s+need\s+admin\s+review\b",
        )
        if any(re.search(pattern, q) for pattern in pending_certification_patterns):
            return "PENDING_CERTIFICATIONS", None
        for certification in ("PENDING", "APPROVED", "REJECTED"):
            if re.search(rf"\b{certification.lower()}\s+products?\b", q):
                return "CERTIFICATION", certification
        if re.search(r"\b(?:total\s+products?|product\s+catalog|catalog\s+summary|product\s+statuses?|active\s+products?|inactive\s+products?)\b", q):
            return "SUMMARY", None
        return "NONE", None

    @staticmethod
    def _format_product(product: dict[str, Any]) -> str:
        text = (
            f"Product #{product.get('id', 'N/A')}: {product.get('name', 'N/A')}\n"
            f"• Certification: {product.get('certification', 'N/A')}\n"
            f"• Active: {'Yes' if product.get('is_active') else 'No'}\n"
            f"• Price: ₹{product.get('price', 'N/A')} / {product.get('unit', 'N/A')}\n"
            f"• Stock: {product.get('stock_quantity', 'N/A')}\n"
            f"• Seller ID: {product.get('seller_id', 'N/A')}"
        )
        category = product.get("category")
        if isinstance(category, dict) and category.get("name"):
            text += f"\n• Category: {category['name']}"
        return text

    async def _handle_catalog_query(self, intent: str, value: str | int | None, token: str | None) -> dict[str, Any]:
        if intent == "PRODUCT_DETAIL":
            result = await self.product_client.get_admin_product(int(value), token)
            if not result["success"]:
                return {"answer": result["detail"], "sources": ADMIN_PRODUCT_SOURCE}
            return {"answer": self._format_product(result["product"]), "sources": ADMIN_PRODUCT_SOURCE}

        if intent == "PENDING_CERTIFICATIONS":
            result = await self.product_client.get_pending_certification_products(token)
            if not result["success"]:
                return {"answer": result["detail"], "sources": ADMIN_PRODUCT_SOURCE}
            if not result["products"]:
                return {
                    "answer": "There are no active products pending certification review.",
                    "sources": ADMIN_PRODUCT_SOURCE,
                }
            lines = [f"Active pending products: {result['total']}"]
            for product in result["products"][:10]:
                lines.append(self._format_product(product))
            if result["total"] > len(result["products"]):
                lines.append(f"Showing {len(result['products'])} of {result['total']} pending products.")
            return {"answer": "\n".join(lines), "sources": ADMIN_PRODUCT_SOURCE}

        if intent == "CERTIFICATION":
            result = await self.product_client.get_admin_products(token, certification=str(value))
            if not result["success"]:
                return {"answer": result["detail"], "sources": ADMIN_PRODUCT_SOURCE}
            lines = [f"Active {value.lower()} products: {result['total']}"]
            for product in result["products"][:5]:
                lines.append(f"• #{product.get('id', 'N/A')} {product.get('name', 'N/A')}")
            return {"answer": "\n".join(lines), "sources": ADMIN_PRODUCT_SOURCE}

        counts: dict[str, int] = {}
        for certification in ("PENDING", "APPROVED", "REJECTED"):
            result = await self.product_client.get_admin_products(token, certification=certification)
            if not result["success"]:
                return {"answer": result["detail"], "sources": ADMIN_PRODUCT_SOURCE}
            counts[certification] = result["total"]
        total = sum(counts.values())
        return {
            "answer": (
                "Active catalog summary:\n"
                f"• Total active products: {total}\n"
                f"• PENDING: {counts['PENDING']}\n"
                f"• APPROVED: {counts['APPROVED']}\n"
                f"• REJECTED: {counts['REJECTED']}\n"
                "Inactive aggregate counts are not exposed by the current Product Service catalog API."
            ),
            "sources": ADMIN_PRODUCT_SOURCE,
        }

    async def handle_query(self, query: str, token: str | None = None) -> dict[str, Any]:
        started_at = perf_counter()
        business_intent = self._business_insights_intent(query)
        if business_intent != "NONE":
            response = await self._handle_business_insights_query(business_intent, token)
            response["latency_ms"] = round((perf_counter() - started_at) * 1000.0, 2)
            return response
        order_intent = self._order_analytics_intent(query)
        if order_intent != "NONE":
            response = await self._handle_order_analytics_query(order_intent, token)
            response["latency_ms"] = round((perf_counter() - started_at) * 1000.0, 2)
            return response
        intent, value = self._catalog_intent(query)
        if intent != "NONE":
            response = await self._handle_catalog_query(intent, value, token)
            response["latency_ms"] = round((perf_counter() - started_at) * 1000.0, 2)
            return response
        retrieval_data = self.retriever.retrieve(query)
        context = retrieval_data.get("context", "")
        sources = retrieval_data.get("sources", [])

        if not context:
            return {
                "answer": "I don't have that information in the OrganicKart admin knowledge base yet.",
                "sources": [],
            }

        prompt = f"""OrganicKart Admin Knowledge Context:
{context}

Admin Question:
{query}

Answer using only the context above:"""
        answer = await self.llm_service.generate(prompt, system_prompt=ADMIN_SYSTEM_PROMPT)
        return {
            "answer": answer,
            "sources": sources,
            "latency_ms": round((perf_counter() - started_at) * 1000.0, 2),
        }
