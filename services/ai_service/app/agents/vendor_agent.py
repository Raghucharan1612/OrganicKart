import logging
import re
from decimal import Decimal, InvalidOperation
from time import perf_counter
from typing import Any

from app.rag.retriever import RAGRetriever
from app.services.llm_service import LLMService
from app.tools.product_tools import ProductServiceClient

logger = logging.getLogger(__name__)

VENDOR_PRODUCT_SERVICE_SOURCE = [{"document": "Product Service Mine API", "title": "Vendor Products", "score": 1.0}]

SYSTEM_PROMPT = """You are OrganicKart's AI Vendor/Farmer Assistant.
Your goal is to assist organic vendors and farmers with catalog standards, organic farming queries, and platform guidance using ONLY the provided knowledge context.

Rules:
1. Provide accurate, professional, and helpful guidance for vendors and farmers.
2. Do NOT invent prices, inventory levels, or approval statuses.
3. Keep your response concise and structured.
"""


class VendorAgent:
    """
    Role-specific Assistant for OrganicKart VENDOR and FARMER users.
    Supports live product/inventory tools for vendor-owned products,
    and RAG for general vendor/farming knowledge questions.
    """

    def __init__(
        self,
        product_client: ProductServiceClient | None = None,
        retriever: RAGRetriever | None = None,
        llm_service: LLMService | None = None,
    ):
        self.product_client = product_client or ProductServiceClient()
        self.retriever = retriever or RAGRetriever()
        self.llm_service = llm_service or LLMService()

    @staticmethod
    def _to_decimal(value: Any) -> Decimal:
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
        amount = cls._to_decimal(value)
        return f"₹{amount:.2f}"

    def _is_live_vendor_query(self, query: str) -> tuple[bool, str]:
        """
        Determine if query requires live vendor product/inventory data.
        Returns tuple: (is_live_query, intent_type)
        intent_type can be: 'MY_PRODUCTS', 'INVENTORY_STOCK', 'LOW_STOCK', 'CERTIFICATION_STATUS'
        """
        q = " ".join(query.lower().split())

        low_stock_patterns = [
            r"\blow\s+(?:on\s+)?stock\b",
            r"\bout\s+of\s+stock\b",
            r"\brunning\s+low\b",
            r"\brestock\b",
            r"\blow\s+inventory\b",
            r"\bstock\s+(?:is\s+)?low\b",
        ]

        for pattern in low_stock_patterns:
            if re.search(pattern, q):
                return True, "LOW_STOCK"

        stock_patterns = [
            r"\binventory\b",
            r"\bstock\s+(?:level|levels|count|quantity)\b",
            r"\bmy\s+stock\b",
            r"\bcheck\s+(?:my\s+)?stock\b",
            r"\bproduct\s+stock\b",
        ]
        for pattern in stock_patterns:
            if re.search(pattern, q):
                return True, "INVENTORY_STOCK"

        cert_patterns = [
            r"\bcertification\b",
            r"\bapproval\s+status\b",
            r"\bproduct\s+status\b",
            r"\bapproved\s+products\b",
            r"\bpending\s+products?\b",
            r"\brejected\s+products?\b",
        ]
        for pattern in cert_patterns:
            if re.search(pattern, q):
                return True, "CERTIFICATION_STATUS"

        my_products_patterns = [
            r"\bmy\s+products?\b",
            r"\bshow\s+(?:my\s+)?products?\b",
            r"\blist\s+(?:my\s+)?products?\b",
            r"\bmy\s+catalog\b",
            r"\bproducts?\s+i\s+sell\b",
            r"\bwhat\s+products\b",
        ]
        for pattern in my_products_patterns:
            if re.search(pattern, q):
                return True, "MY_PRODUCTS"

        return False, "NONE"

    async def handle_query(
        self,
        query: str,
        user_id: int,
        token: str | None = None,
    ) -> dict[str, Any]:
        """
        Process a vendor/farmer query.
        Routes to live product/inventory tools or RAG knowledge.
        """
        start_time = perf_counter()

        is_live, intent = self._is_live_vendor_query(query)
        if is_live:
            answer = await self._handle_live_vendor_query(intent=intent, token=token)
            latency = (perf_counter() - start_time) * 1000.0
            return {
                "answer": answer,
                "sources": VENDOR_PRODUCT_SERVICE_SOURCE,
                "latency_ms": round(latency, 2),
            }

        # Fallback to RAG knowledge for vendor/farming context
        retrieval_data = self.retriever.retrieve(query)
        context_text = retrieval_data.get("context", "")
        sources = retrieval_data.get("sources", [])

        if not context_text:
            answer = (
                "I'm sorry, I don't have information about that in the OrganicKart knowledge base. "
                "I can help with your product catalog, stock inventory, low-stock alerts, certification status, and organic farming guidelines."
            )
        else:
            prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"Knowledge Context:\n{context_text}\n\n"
                f"Vendor/Farmer Question: {query}\nAnswer:"
            )
            answer = await self.llm_service.generate(prompt, system_prompt=SYSTEM_PROMPT)

        latency = (perf_counter() - start_time) * 1000.0
        return {
            "answer": answer,
            "sources": sources,
            "latency_ms": round(latency, 2),
        }


    async def _handle_live_vendor_query(self, intent: str, token: str | None) -> str:
        """Fetch and format live product/inventory data for the authenticated vendor."""
        result = await self.product_client.get_my_products(token=token)
        if not result["success"]:
            detail = result.get("detail", "Unable to retrieve your products at this time.")
            return f"Unable to fetch product data from Product Service: {detail}"

        products = result.get("products", [])
        if not products:
            return "You do not have any products listed in your catalog yet."

        if intent == "MY_PRODUCTS":
            lines = ["Here are your listed products:"]
            for p in products:
                name = p.get("name", "Unknown Product")
                p_id = p.get("id", "N/A")
                price = self._format_currency(p.get("price"))
                unit = p.get("unit", "unit")
                stock = p.get("stock_quantity", 0)
                cert = p.get("certification", "PENDING")
                lines.append(f"• {name} (ID: {p_id}) - {price} / {unit} - Stock: {stock} - Certification: {cert}")
            return "\n".join(lines)

        elif intent == "INVENTORY_STOCK":
            lines = ["Here is your current inventory stock:"]
            for p in products:
                name = p.get("name", "Unknown Product")
                stock = p.get("stock_quantity", 0)
                unit = p.get("unit", "units")
                lines.append(f"• {name}: {stock} {unit}")
            return "\n".join(lines)

        elif intent == "LOW_STOCK":
            low_stock_items = [p for p in products if p.get("stock_quantity", 0) <= 10]
            if not low_stock_items:
                return "All your products currently have sufficient stock levels (more than 10 units available)."

            lines = ["Here are your low-stock products (10 or fewer remaining):"]
            for p in low_stock_items:
                name = p.get("name", "Unknown Product")
                p_id = p.get("id", "N/A")
                stock = p.get("stock_quantity", 0)
                unit = p.get("unit", "units")
                lines.append(f"• {name} (ID: {p_id}): {stock} {unit} remaining")
            return "\n".join(lines)

        elif intent == "CERTIFICATION_STATUS":
            lines = ["Here is the certification and approval status for your products:"]
            for p in products:
                name = p.get("name", "Unknown Product")
                cert = p.get("certification", "PENDING")
                active = "Yes" if p.get("is_active", True) else "No"
                lines.append(f"• {name}: {cert} (Active: {active})")
            return "\n".join(lines)

        return "Unable to process live vendor product request."
