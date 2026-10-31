import re
import logging
from decimal import Decimal, InvalidOperation
from enum import Enum
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


class CustomerIntent(str, Enum):
    POLICY_KB = "POLICY_KB"
    GENERAL_KNOWLEDGE = "GENERAL_KNOWLEDGE"
    PRODUCT_QUERY = "PRODUCT_QUERY"
    ORDER_QUERY = "ORDER_QUERY"
    MULTI_INTENT = "MULTI_INTENT"
    GREETING_OR_CHITCHAT = "GREETING_OR_CHITCHAT"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"


SYSTEM_PROMPT = """You are OrganicKart's AI Customer Assistant.
Your goal is to answer customer questions accurately and completely using ONLY the provided OrganicKart knowledge context.

Rules:
1. Read the full context carefully before responding.
2. If the context lists product categories, types, or items — enumerate them clearly in your answer.
3. For unsupported policy requests or services not permitted by OrganicKart (such as cryptocurrency payments, returns after the allowed window, or unapproved delivery regions), clearly state that they are not supported by official OrganicKart policies. Do NOT fabricate exceptions or invent policy details.
4. If the context does not contain sufficient information to answer the question, respond with:
   "I'm sorry, I don't have information about that in the OrganicKart knowledge base. I can help with organic products, delivery, quality standards, and customer policies."
5. Do NOT speculate, invent prices, invent stock levels, or add details not present in the context.
6. Keep your answer helpful and concise: use 2–5 sentences or brief bullets.
7. Format your output strictly in clean, standard Markdown (tables, lists, bold text). Do NOT use raw HTML tags such as <br>, <p>, <table>, or <div>. Use Markdown line breaks and paragraphs instead.
"""

GENERAL_KNOWLEDGE_SYSTEM_PROMPT = """You are OrganicKart's AI Educational Assistant.
Your goal is to provide accurate, objective, and helpful general educational explanations about organic agriculture, produce, and nutrition.

Rules:
1. Answer the general educational question clearly and concisely (2–4 sentences or structured bullet points).
2. Use established agricultural and nutritional knowledge.
3. Clearly distinguish general educational explanations from verified OrganicKart-specific claims or store policies.
4. Do NOT invent OrganicKart prices, inventory, or official company policies.
5. If OrganicKart knowledge context is provided, use it as supporting evidence and clearly indicate OrganicKart's verified practices versus general facts.
6. Format your output strictly in clean, standard Markdown (bold text, bullet points). Do NOT use raw HTML tags such as <br>, <p>, <table>, or <div>. Use Markdown line breaks and paragraphs instead.
"""

ORDER_SERVICE_SOURCE = [{"document": "Order Service API", "title": "Order Service", "score": 1.0}]
CART_SERVICE_SOURCE = [{"document": "Order Service Cart API", "title": "Your Cart", "score": 1.0}]
PRODUCT_SERVICE_SOURCE = [{"document": "Product Service API", "title": "Product Catalog", "score": 1.0}]
DELIVERY_SERVICE_SOURCE = [{"document": "Delivery Service API", "title": "Delivery Tracking", "score": 1.0}]
NOTIFICATION_SERVICE_SOURCE = [{"document": "Notification Service API", "title": "Notifications", "score": 1.0}]
GENERAL_KNOWLEDGE_SOURCE = [{"document": "General Knowledge", "title": "General Knowledge", "score": 1.0}]


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
        Extract the first numeric order ID from user query if present.
        Examples: 'order 123', 'order #123', 'status of order 45', '#123'
        """
        ids = self._extract_all_order_ids(query)
        return ids[0] if ids else None

    @staticmethod
    def _extract_all_order_ids(query: str) -> list[int]:
        """
        Extract all distinct integer order IDs from a query, preserving first-appearance order.
        Handles:
          - 'Show orders 77 and 88'
          - 'Show order 77 and order 88'
          - 'Status of order #12 and #34'
          - 'order 1, order 2, order 3'
          - 'orders 10, 20 and 30'
          - 'order 55 and order 55' (deduplicated)
        Recognizes subsequent bare IDs connected by commas, 'and', or '&' once order context is established.
        Does not interpret arbitrary numbers in unrelated messages as order IDs.
        """
        ORDER_START_RE = re.compile(
            r"(?:status\s+of\s+ord(?:er|r)s?\s*#?|ord(?:er|r)s?\s*(?:ids?|#)?|#)\s*(-?\d+)\b"
            r"(?!\s+(?:apples?|bananas?|oranges?|fruits?|vegetables?|items?|products?|kgs?|grams?|gms?|litres?|liters?|boxes?|packets?|packs?|pieces?|pcs?|units?|bottles?))",
            re.IGNORECASE,
        )
        CHAINED_ID_RE = re.compile(
            r"^(?:,\s*(?:and|&)\s*|,\s*|\s+(?:and|&)\s+)"
            r"(?:(?:ord(?:er|r)s?\s*(?:ids?|#)?|#)\s*)?(-?\d+)\b"
            r"(?!\s+(?:apples?|bananas?|oranges?|fruits?|vegetables?|items?|products?|kgs?|grams?|gms?|litres?|liters?|boxes?|packets?|packs?|pieces?|pcs?|units?|bottles?))",
            re.IGNORECASE,
        )

        seen: set[int] = set()
        result: list[int] = []

        pos = 0
        while pos < len(query):
            m = ORDER_START_RE.search(query, pos)
            if not m:
                break
            try:
                oid = int(m.group(1))
                if oid not in seen:
                    seen.add(oid)
                    result.append(oid)
            except ValueError:
                pass

            pos = m.end()

            # Chain any subsequent bare or prefixed IDs connected by commas, 'and', '&'
            while pos < len(query):
                chained = CHAINED_ID_RE.match(query[pos:])
                if not chained:
                    break
                try:
                    coid = int(chained.group(1))
                    if coid not in seen:
                        seen.add(coid)
                        result.append(coid)
                except ValueError:
                    pass
                pos += chained.end()

        return result

    @staticmethod
    def _detect_order_filter(query: str) -> dict[str, Any]:
        """
        Detect explicit client-side filter requests against the Order Service response.

        Supported filters (applied on the full order list returned for the customer):
          - payment_status: one of PAID, PAYMENT_PENDING, FAILED (from PaymentStatus enum)
          - month: calendar month name (e.g. 'august') or YYYY-MM string

        Returns a dict with keys 'payment_status', 'month', 'unsupported', and 'ambiguous'.
        """
        q = query.lower()

        # --- payment_status filter ---
        # Valid values from Order Service PaymentStatus enum
        VALID_PAYMENT_STATUSES = {"PAID", "PAYMENT_PENDING", "FAILED"}
        payment_status: str | None = None
        unsupported: str | None = None
        ambiguous: bool = False

        if re.search(r"\bpaid\b", q) and not re.search(r"\bunpaid\b", q):
            payment_status = "PAID"
        elif re.search(r"\bunpaid\b|\bpayment.?pending\b|\bpending.?payment\b", q):
            payment_status = "PAYMENT_PENDING"
        elif re.search(r"\bfailed\b", q):
            payment_status = "FAILED"
        elif re.search(r"\brefunded\b", q):
            unsupported = "Refunded payment status is not a supported order payment filter."
        elif re.search(r"\bpayment\s+status\s+(?:of\s+)?(\w+)\b", q):
            m = re.search(r"\bpayment\s+status\s+(?:of\s+)?(\w+)\b", q)
            if m:
                val = m.group(1).upper()
                if val in VALID_PAYMENT_STATUSES:
                    payment_status = val
                else:
                    unsupported = f"Payment status '{val}' is not recognized."

        # --- month filter ---
        month: str | None = None
        month_names = {
            "january": "01", "jan": "01",
            "february": "02", "feb": "02",
            "march": "03", "mar": "03",
            "april": "04", "apr": "04",
            "may": "05",
            "june": "06", "jun": "06",
            "july": "07", "jul": "07",
            "august": "08", "aug": "08",
            "september": "09", "sept": "09", "sep": "09",
            "october": "10", "oct": "10",
            "november": "11", "nov": "11",
            "december": "12", "dec": "12",
        }
        for name, num in month_names.items():
            if re.search(r"\b" + name + r"\b", q):
                year_match = re.search(r"\b(20\d{2})\b", q)
                year = year_match.group(1) if year_match else None
                month = f"{year}-{num}" if year else num  # e.g. '2026-08' or just '08'
                break
        if not month:
            ym_match = re.search(r"\b(20\d{2})-(0[1-9]|1[0-2])\b", q)
            if ym_match:
                month = ym_match.group(0)

        # Ambiguous filter detection (asked to filter without recognized criteria)
        if (
            not payment_status
            and not month
            and not unsupported
            and re.search(r"\bfilter(?:ed)?\b|\bby\s+(?:status|payment|month|date)\b", q)
            and not re.search(r"\b(?:recent|latest|all|history|past)\b", q)
        ):
            ambiguous = True

        return {
            "payment_status": payment_status,
            "month": month,
            "unsupported": unsupported,
            "ambiguous": ambiguous,
        }

    @staticmethod
    def _is_policy_or_general_query(query: str) -> bool:
        """Detect general policy, FAQ, cancellation, refund, return questions that should use RAG."""
        q = query.lower()
        patterns = (
            r"\bpolic(?:y|ies)\b",
            r"\b(?:cancellation|cancel|cancelling)\b",
            r"\b(?:refund|refunds|refunding)\b",
            r"\b(?:returns?|returning)\b",
            r"\b(?:faq|terms|rules|guidelines|standards?)\b",
            r"\bhow\s+(?:does|do)\s+(?:delivery|ord(?:er|r)s?|returns?|refunds?|organickart)\s+work\b",
            r"\b(?:delivery|operating)\s+hours\b",
            r"\bpayment\s+methods?\b",
        )
        return any(re.search(pattern, q) for pattern in patterns)

    def _is_live_order_query(self, query: str) -> tuple[bool, str, list[int]]:
        """
        Determine if query requires live order data or asks for clarification.

        Returns tuple: (is_order_query, intent_type, order_ids)
          intent_type values:
            'ORDER_BY_ID'         – single explicit order ID
            'MULTIPLE_ORDERS_BY_ID' – two or more distinct explicit order IDs
            'ORDER_STATUS'        – wants latest-order status, no ID
            'RECENT_ORDERS'       – wants recent order list
            'FILTERED_ORDERS'     – wants filtered order list (payment_status or month)
            'AMBIGUOUS_ORDER'     – order-related but not enough info to act
          order_ids: extracted positive integer IDs (empty list when not applicable)
        """
        # Normalize whitespace before matching so natural-language phrasing is
        # routed consistently without involving the LLM.
        q = " ".join(query.lower().split())

        # Explicit delivery/tracking questions must not be swallowed by broad
        # order-history phrases such as "my orders".
        if self._is_live_delivery_query(q):
            return False, "NONE", []

        # General policy questions (cancellation, refunds, returns, order policy)
        # must use RAG knowledge, not live order tools.
        if self._is_policy_or_general_query(q):
            return False, "NONE", []

        # --- Explicit order ID(s) ---
        all_ids = self._extract_all_order_ids(q)
        if len(all_ids) > 1:
            return True, "MULTIPLE_ORDERS_BY_ID", all_ids
        if len(all_ids) == 1:
            return True, "ORDER_BY_ID", all_ids

        # --- Filter requests (payment_status / month / ambiguous) ---
        if re.search(r"\bord(?:er|r)s?\b", q):
            flt = self._detect_order_filter(q)
            if flt["payment_status"] or flt["month"] or flt.get("unsupported") or flt.get("ambiguous"):
                return True, "FILTERED_ORDERS", []

        # Clear intent for current/latest order status
        order_status_patterns = [
            r"\b(?:what\s+is\s+)?(?:the\s+)?status\s+(?:of\s+)?(?:my\s+)?(?:latest\s+|last\s+)?ord(?:er|r)\b",
            r"\bmy\s+ord(?:er|r)\s+status\b",
            r"\bwhere(?:\s+is|['’]s)\s+my\s+ord(?:er|r)\b",
            r"\btrack\s+(?:my\s+)?ord(?:er|r)s?\b",
            r"\bord(?:er|r)\s+status\b",
            r"\bstatus\s+of\s+(?:my\s+)?(?:latest\s+|last\s+)?ord(?:er|r)\b",
            r"\bis\s+my\s+ord(?:er|r)\b(?!\s+out\s+for\s+delivery\b)",
            r"\b(?:any\s+)?updates?\s+(?:on|about)\s+(?:my\s+)?ord(?:er|r)\b",
            r"\b(?:my\s+)?(?:latest|last)\s+ord(?:er|r)(?:\s+status)?\b",
        ]
        for pattern in order_status_patterns:
            if re.search(pattern, q):
                return True, "ORDER_STATUS", []

        # Clear intent for recent orders or order history
        recent_order_patterns = [
            r"\brecent\s+ord(?:er|r)s?\b",
            r"\blatest\s+ord(?:er|r)s\b",
            r"\bord(?:er|r)\s+history\b",
            r"\bpast\s+ord(?:er|r)s?\b",
            r"\bshow\s+(?:my\s+)?ord(?:er|r)s\b",
            r"\blist\s+(?:my\s+)?ord(?:er|r)s\b",
            r"\bmy\s+ord(?:er|r)s\b",
            r"\bprevious\s+ord(?:er|r)s?\b",
            r"\ball\s+(?:my\s+)?ord(?:er|r)s\b",
            r"\bord(?:er|r)s\s+(?:please|pls)\b",
            r"\bview\s+(?:my\s+)?ord(?:er|r)s\b",
            r"\bcheck\s+(?:my\s+)?ord(?:er|r)s\b",
        ]
        for pattern in recent_order_patterns:
            if re.search(pattern, q):
                return True, "RECENT_ORDERS", []

        # Ambiguous order queries: asks about an order without an order ID and
        # without clearly requesting recent orders or latest status.
        ambiguous_order_patterns = [
            r"\b(?:check|look\s*up|find|search|inquire|tell\s+me\s+about)\s+(?:an|the|my)?\s*ord(?:er|r)s?\b",
            r"\b(?:help\s+(?:me\s+)?with|question\s+about)\s+(?:an|the|my)?\s*ord(?:er|r)s?\b",
            r"\b(?:my\s+)?ord(?:er|r)\s+(?:details|info|information|inquiry|help|query)\b",
            r"\babout\s+(?:an|the|my)\s+ord(?:er|r)\b",
            r"\b(?:i\s+have\s+)?(?:an\s+)?ord(?:er|r)\s+question\b",
            r"\bshow\s+(?:my\s+)?ord(?:er|r)\b",
        ]
        for pattern in ambiguous_order_patterns:
            if re.search(pattern, q):
                return True, "AMBIGUOUS_ORDER", []

        return False, "NONE", []

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

        if re.search(
            r"\b(?:what|which)\s+(?:organic\s+)?(?:products?|items?)\s+"
            r"(?:do\s+you\s+(?:have|sell)|(?:are\s+(?:currently\s+)?(?:available|in\s+stock)))\b"
            r"|\b(?:show|list)\s+(?:all\s+)?(?:available\s+)?products\b"
            r"|\bwhat\s+(?:is|do\s+you\s+have)\s+(?:currently\s+)?(?:available|in\s+stock)\b",
            q,
        ):
            return True, None, None

        # 1. price of / cost of X
        match = re.search(r"\b(?:price|cost)\s+(?:of|for)\s+(.+)$", q)
        if not match:
            # 2. price and stock of X / price/stock of X
            match = re.search(r"\b(?:price|cost)\s*(?:and|&|\/)\s*stock\s+(?:of|for)\s+(.+)$", q)
        if not match:
            # 3. do you have X / show me X / do you sell X
            match = re.search(r"\b(?:do\s+you\s+have|show\s+me|do\s+you\s+sell)\s+(.+)$", q)
        if not match:
            # 4. X price/stock or X price and stock or X stock (e.g. "apple price/stock")
            match = re.search(
                r"^(?:what\s+is\s+)?(?:the\s+)?(.+?)\s+(?:price\s*(?:and|&|\/)\s*stock|price\/stock|price\s+and\s+stock|price|stock|availability)[?.!]*$",
                q,
            )
            if match and re.search(r"\b(?:delivery|ord(?:er|r)s?|refund|return|policy|status|notification|cart)\b", match.group(1)):
                match = None
        if not match:
            # 5. is/are X in stock / available
            match = re.search(r"\b(?:is|are)\s+(.+?)\s+(?:currently\s+|now\s+)?(?:in\s+stock|available)\b", q)
        if not match:
            # 6. how much is/are X
            match = re.search(r"\bhow\s+much\s+(?:is|are)\s+(?:the\s+)?(.+)$", q)

        if match:
            raw_term = match.group(1)
            term = re.sub(r"\b(?:please|pls|currently|now)\b", "", raw_term, flags=re.IGNORECASE)
            term = re.sub(r"[?.!]+$", "", term).strip()
            # If extracted term is a pronoun or generic placeholder, not a standalone product query
            if term.lower() in {
                "them", "it", "this", "that", "any", "anything", "products", "items", "stuff",
                "things", "currently", "now", "organic products", "organic items",
            }:
                if re.search(r"\b(?:available|in\s+stock)\b", q):
                    return True, None, None
                return False, None, None
            # If extracted term contains policy or order keywords, do not treat as a single product query
            if re.search(r"\b(?:polic(?:y|ies)|returns?|refunds?|ord(?:er|r)s?|deliver(?:y|ies)|notifications?)\b", term):
                return False, None, None
            return (True, None, term) if term else (False, None, None)

        # Short product-name searches, while excluding policy and general-web terms.
        if re.fullmatch(r"(?:organic\s+)?[a-z]+(?:\s+[a-z]+)?", q) and not re.search(
            r"\b(?:farming|policy|policies|ord(?:er|r)s?|delivery|return|refund|quality|standards?)\b", q
        ):
            return True, None, q
        return False, None, None

    @staticmethod
    def _is_greeting_or_chitchat(query: str) -> tuple[bool, str]:
        """Detect pure greetings and conversational pleasantries."""
        q = " ".join(query.lower().strip().split())
        cleaned = re.sub(r"[?!.,;:]+$", "", q).strip()

        if cleaned in {
            "hi", "hello", "hey", "hey there", "hello there", "hi there",
            "good morning", "good afternoon", "good evening", "good day",
            "greetings", "namaste", "howdy",
        }:
            return True, "GREETING"

        if cleaned in {
            "thank you", "thanks", "thanks a lot", "thank you so much",
            "thanks so much", "thx", "appreciate it", "many thanks",
        }:
            return True, "THANKS"

        if cleaned in {
            "bye", "goodbye", "see you", "see ya", "cya", "have a good day", "have a nice day",
        }:
            return True, "FAREWELL"

        if cleaned in {
            "who are you", "what are you", "what is your name",
            "what can you do", "help", "help me", "how can you help", "how can you help me",
        } or bool(re.match(r"^who\s+(?:are\s+you|created\s+you)\b", cleaned)):
            return True, "INTRO"

        return False, ""

    @staticmethod
    def _is_general_knowledge_query(query: str) -> bool:
        """
        Detect general educational, agricultural, and nutritional questions
        that do not ask about OrganicKart store policies or live customer data.
        """
        q = " ".join(query.lower().split())

        # Exclude questions explicitly naming OrganicKart or store policies/operations
        if re.search(r"\borganickart\b", q):
            return False
        if re.search(r"\b(?:your|store|company)\s+(?:polic(?:y|ies)|delivery|returns?|refunds?|hours?|standards?|products?|fruits?|vegetables?|produce|items?)\b", q):
            return False
        if re.search(r"\b(?:do\s+you\s+(?:use|spray|apply|sell|have|carry|deliver)|can\s+i\s+order)\b", q):
            return False
        if re.search(r"\b(?:delivery\s+hours|operating\s+hours|shipping\s+(?:fee|cost|charge)|return\s+window)\b", q):
            return False
        if re.search(r"\b(?:cancellation|refund|return)\s+polic(?:y|ies)\b", q):
            return False

        patterns = (
            # Comparison: organic vs hybrid, conventional, fruit vs vegetable, etc.
            r"\b(?:difference|distinction|comparison)\s+(?:between|of)\b",
            r"\b(?:organic|hybrid|conventional|gmo|fruit|vegetable)\s+(?:vs\.?|versus)\b",
            # Benefits / advantages
            r"\b(?:benefits?|advantages?|health\s+benefits?|pros\s+and\s+cons|nutritional\s+(?:value|benefits?))\s+of\b",
            # Nutrition, calories, vitamins, minerals
            r"\b(?:how\s+many\s+)?calories\b",
            r"\b(?:nutrition|nutrients?|vitamins?|minerals?)\b",
            # Concepts: cold-pressed, crop rotation, compost, heirloom, gmo, etc.
            r"\bwhat\s+(?:is|are)\s+(?:the\s+difference|cold[- ]pressed|hybrid|gmos?|pesticides?|composting?|heirloom|crop\s+rotation)\b",
            r"\bhow\s+(?:is|are|does|do)\s+(?:cold[- ]pressed|crop\s+rotation|composting?|organic\s+farming|plants?|photosynthesis)\b",
            r"\bwhy\s+(?:is|are|should(?:\s+(?:we|i|one|you))?(?:\s+(?:choose|buy|eat|consume|use))?)\s+(?:organic|cold[- ]pressed)\b",
            r"\bexplain\s+(?:the\s+difference|organic|cold[- ]pressed|hybrid|photosynthesis)\b",
            # General science and curiosity questions
            r"\bphotosynthesis\b",
            r"\bwhy\s+is\s+the\s+sky\b",
            r"\bwhat\s+(?:is|are)\s+the\s+difference\s+between\s+(?:a\s+)?fruit\s+and\s+(?:a\s+)?vegetable\b",
            r"\bexplain\b",
        )
        return any(re.search(p, q) for p in patterns)

    def _detect_multi_intent(self, query: str) -> list[tuple[CustomerIntent, str]] | None:
        """
        Check if query combines multiple distinct capability intents.
        Returns a list of (CustomerIntent, sub_query) tuples if multi-intent, otherwise None.
        """
        # Single order queries (including multiple order ID lists) are not multi-intent
        if self._is_live_order_query(query)[0]:
            return None

        # Clean single product queries (e.g. "What is the price and stock of apples?") are not multi-intent
        if self._live_product_query(query)[0]:
            return None

        # Split on sentence boundaries or conjunctions
        parts = []
        sentence_parts = [p.strip() for p in re.split(r"[?.!]+\s+", query) if p.strip()]
        if len(sentence_parts) > 1:
            parts = sentence_parts
        else:
            clause_split = re.split(
                r"\s+and\s+(?=(?:do\s+you|can\s+you|could\s+you|what\s+is|what\s+are|where\s+is|how\s+much|how\s+is|tell\s+me|also)\b)|\s+(?:and\s+also|as\s+well\s+as|also)\s+",
                query,
                flags=re.IGNORECASE,
            )
            if len(clause_split) > 1:
                parts = [p.strip() for p in clause_split if p.strip()]
            else:
                and_split = [p.strip() for p in re.split(r"\s+and\s+", query, flags=re.IGNORECASE) if p.strip()]
                if len(and_split) == 2 and all(len(p.split()) >= 3 for p in and_split):
                    parts = and_split

        if len(parts) < 2:
            return None

        # Contextual pronoun queries (e.g. "What are the benefits of cold-pressed oils and do you sell them?")
        has_pronoun_product_clause = any(
            re.search(r"\b(?:do\s+you\s+)?(?:sell|have|carry)\s+(?:them|it|these|any)\b", p, re.I) for p in parts
        )
        if has_pronoun_product_clause and len(parts) >= 2:
            entity = None
            for p in parts:
                m = re.search(r"\b(?:benefits\s+of|about|on|for|difference\s+between)\s+(.+?)(?:[?.!]|$)", p, re.I)
                if m:
                    entity = m.group(1).strip()
                    break
            context_resolved = []
            for part in parts:
                if re.search(r"\b(?:do\s+you\s+)?(?:sell|have|carry)\s+(?:them|it|these|any)\b", part, re.I):
                    sub_q = f"do you sell {entity}" if entity else part
                    context_resolved.append((CustomerIntent.PRODUCT_QUERY, sub_q))
                else:
                    intnt, _ = self._classify_single_intent(part)
                    context_resolved.append((intnt, part))
            if len({i for i, _ in context_resolved}) >= 2:
                return context_resolved

        sub_intents = []
        distinct_intents = set()
        for part in parts:
            intent, _ = self._classify_single_intent(part)
            if intent == CustomerIntent.GREETING_OR_CHITCHAT:
                continue
            sub_intents.append((intent, part))
            distinct_intents.add(intent)

        if len(distinct_intents) >= 2:
            return sub_intents

        return None

    def _classify_single_intent(self, query: str) -> tuple[CustomerIntent, dict[str, Any]]:
        """Classify a single query into its capability intent without multi-intent splitting."""
        is_greeting, kind = self._is_greeting_or_chitchat(query)
        if is_greeting:
            return CustomerIntent.GREETING_OR_CHITCHAT, {"kind": kind}

        is_order, order_intent, order_ids = self._is_live_order_query(query)
        if order_intent == "AMBIGUOUS_ORDER":
            return CustomerIntent.CLARIFICATION_REQUIRED, {"type": "order_ambiguous"}
        if order_intent == "FILTERED_ORDERS":
            flt = self._detect_order_filter(query)
            if flt.get("ambiguous") or flt.get("unsupported"):
                return CustomerIntent.CLARIFICATION_REQUIRED, {"type": "filter_clarification", "filter": flt}
            return CustomerIntent.ORDER_QUERY, {"order_intent": order_intent, "order_ids": order_ids}
        if is_order:
            return CustomerIntent.ORDER_QUERY, {"order_intent": order_intent, "order_ids": order_ids}

        if self._is_live_cart_query(query):
            return CustomerIntent.ORDER_QUERY, {"sub_type": "cart"}

        if self._is_live_delivery_query(query):
            return CustomerIntent.ORDER_QUERY, {"sub_type": "delivery"}

        if self._is_live_notification_query(query):
            return CustomerIntent.ORDER_QUERY, {"sub_type": "notification"}

        is_product, product_id, search = self._live_product_query(query)
        if is_product:
            return CustomerIntent.PRODUCT_QUERY, {"product_id": product_id, "search": search}

        if self._is_current_web_query(query):
            return CustomerIntent.POLICY_KB, {"web": True}

        # Check official policy keywords explicitly before general knowledge fallback
        if self._is_policy_query(query):
            return CustomerIntent.POLICY_KB, {}

        if self._is_general_knowledge_query(query):
            return CustomerIntent.GENERAL_KNOWLEDGE, {}

        if self._is_organickart_knowledge_query(query):
            return CustomerIntent.POLICY_KB, {}

        # Fallback: questions about organic/food concepts or general education/knowledge
        # that do not ask about store policies or OrganicKart company operations are GENERAL_KNOWLEDGE
        return CustomerIntent.GENERAL_KNOWLEDGE, {}

    @staticmethod
    def _is_policy_query(query: str) -> bool:
        """Detect official store policy questions regarding delivery, returns, refunds, payment methods, cancellations."""
        q = " ".join(query.lower().split())
        patterns = (
            r"\b(?:return|refund|exchange)\b",
            r"\b(?:cancellation|cancel)\b",
            r"\b(?:delivery\s+hours|shipping|delivery\s+fee|delivery\s+time|deliveries|delivery\s+speed|how\s+fast\s+is\s+delivery|10[- ]minute\s+delivery)\b",
            r"\bpayment\s+methods?\b",
            r"\bquality\s+standards?\b",
            r"\b(?:your|store|company)\s+polic(?:y|ies)\b",
        )
        return any(re.search(pattern, q) for pattern in patterns)

    def classify_intent(self, query: str) -> tuple[CustomerIntent, dict[str, Any]]:
        """
        Classify a customer query into one of the supported capability intents:
          - POLICY_KB
          - GENERAL_KNOWLEDGE
          - PRODUCT_QUERY
          - ORDER_QUERY
          - MULTI_INTENT
          - GREETING_OR_CHITCHAT
          - CLARIFICATION_REQUIRED
        """
        multi = self._detect_multi_intent(query)
        if multi:
            return CustomerIntent.MULTI_INTENT, {"sub_tasks": multi}
        return self._classify_single_intent(query)


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
            r"\b(?:your|organickart(?:'s)?)\s+(?:fruits?|vegetables?|produce|items?)\b",
            r"\b(?:what|which)\s+products?\s+(?:do\s+you\s+have|are\s+available)\b",
            r"\bdo\s+you\s+sell\b",
            r"\bdo\s+you\s+use\b",
            r"\bcan\s+i\s+order\b.*\bweight\b",
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

    @staticmethod
    def _format_order_block(o: dict[str, Any]) -> str:
        """Format a single order dict into a readable bullet block."""
        raw_items = o.get("items")
        items = raw_items if isinstance(raw_items, list) else []
        items_summary = ", ".join([
            f"{item.get('product_name') or 'Item'} (x{item.get('quantity') or 1})"
            for item in items
            if isinstance(item, dict)
        ]) or "N/A"
        order_id_val = o.get("id") if o.get("id") is not None else "N/A"
        status_val = o.get("status") or "N/A"
        payment_val = o.get("payment_status") or "N/A"
        total_val = CustomerAgent._format_currency(o.get("total_amount"))
        raw_date = o.get("created_at")
        date_val = str(raw_date).strip()[:10] if raw_date and str(raw_date).strip() else "N/A"
        return (
            f"• Order #{order_id_val}\n"
            f"  Status: {status_val} | Payment: {payment_val}\n"
            f"  Total: {total_val} | Date: {date_val}\n"
            f"  Items: {items_summary}"
        )

    async def _handle_live_order_tool(
        self,
        intent: str,
        order_ids: list[int],
        user_id: int | None,
        token: str | None,
        query: str = "",
    ) -> dict[str, Any]:
        """
        Execute Order Service tool calls and format clean customer responses.
        """
        if not token or not user_id:
            return {
                "answer": "Authentication is required to view live order details.",
                "sources": [],
            }

        if intent == "AMBIGUOUS_ORDER":
            return {
                "answer": (
                    "Could you please provide your order ID (for example, Order #123), "
                    "or would you like to see your recent orders?"
                ),
                "sources": ORDER_SERVICE_SOURCE,
            }

        # ── Single order by ID ────────────────────────────────────────────────
        if intent == "ORDER_BY_ID":
            order_id = order_ids[0] if order_ids else None
            if order_id is None or order_id <= 0:
                display_id = order_id if order_id is not None else "(unknown)"
                return {
                    "answer": f"Order ID {display_id} is invalid. Please provide a valid numeric order ID.",
                    "sources": ORDER_SERVICE_SOURCE,
                }

            res = await self.order_client.get_order_by_id(order_id, token, user_id)
            if not res["success"]:
                return {
                    "answer": res["detail"],
                    "sources": ORDER_SERVICE_SOURCE,
                }

            order = res["order"]
            items_str = ""
            raw_items = order.get("items")
            items = raw_items if isinstance(raw_items, list) else []
            if items:
                item_lines = [
                    f"  • {item.get('product_name') or 'Item'} x {item.get('quantity') or 1}"
                    f" ({self._format_currency(item.get('subtotal'))})"
                    for item in items
                    if isinstance(item, dict)
                ]
                if item_lines:
                    items_str = "\n" + "\n".join(item_lines)

            display_order_id = order.get("id") if order.get("id") is not None else order_id
            status_val = order.get("status") or "N/A"
            payment_val = order.get("payment_status") or "N/A"
            total_val = self._format_currency(order.get("total_amount"))
            address_val = order.get("shipping_address") or "N/A"
            raw_date = order.get("created_at")
            date_val = str(raw_date).strip()[:10] if raw_date and str(raw_date).strip() else "N/A"

            answer = (
                f"Order #{display_order_id} Status:\n"
                f"• Status: {status_val}\n"
                f"• Payment Status: {payment_val}\n"
                f"• Total Amount: {total_val}\n"
                f"• Shipping Address: {address_val}\n"
                f"• Date Placed: {date_val}"
            )
            if items_str:
                answer += f"\n• Items:\n{items_str}"

            return {"answer": answer, "sources": ORDER_SERVICE_SOURCE}

        # ── Multiple orders by ID ─────────────────────────────────────────────
        if intent == "MULTIPLE_ORDERS_BY_ID":
            invalid_ids = [oid for oid in order_ids if oid <= 0]
            valid_ids = [oid for oid in order_ids if oid > 0]

            if not valid_ids:
                id_list = ", ".join(f"#{oid}" for oid in order_ids)
                return {
                    "answer": f"None of the provided order IDs ({id_list}) are valid. Please use positive numeric IDs.",
                    "sources": ORDER_SERVICE_SOURCE,
                }

            blocks: list[str] = []
            for oid in valid_ids:
                res = await self.order_client.get_order_by_id(oid, token, user_id)
                if not res["success"]:
                    blocks.append(f"• Order #{oid}: {res['detail']}")
                else:
                    blocks.append(self._format_order_block(res["order"]))

            if invalid_ids:
                id_list = ", ".join(f"#{oid}" for oid in invalid_ids)
                blocks.append(f"Note: {id_list} {'was' if len(invalid_ids) == 1 else 'were'} skipped (invalid ID).")

            header = f"Here are the details for {len(valid_ids)} order{'s' if len(valid_ids) > 1 else ''}:\n"
            return {"answer": header + "\n\n".join(blocks), "sources": ORDER_SERVICE_SOURCE}

        # ── Latest order status (no ID) ───────────────────────────────────────
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
                    "answer": "You don't have any orders yet.",
                    "sources": ORDER_SERVICE_SOURCE,
                }

            latest = orders[0]
            raw_items = latest.get("items")
            items = raw_items if isinstance(raw_items, list) else []
            items_summary = ", ".join([
                f"{item.get('product_name') or 'Item'} (x{item.get('quantity') or 1})"
                for item in items
                if isinstance(item, dict)
            ]) or "N/A"

            display_id = latest.get("id") if latest.get("id") is not None else "N/A"
            status_val = latest.get("status") or "N/A"
            payment_val = latest.get("payment_status") or "N/A"
            total_val = self._format_currency(latest.get("total_amount"))
            raw_date = latest.get("created_at")
            date_val = str(raw_date).strip()[:10] if raw_date and str(raw_date).strip() else "N/A"

            answer = (
                f"Your latest order status:\n\n"
                f"• Order #{display_id}\n"
                f"• Status: {status_val}\n"
                f"• Payment Status: {payment_val}\n"
                f"• Total Amount: {total_val}\n"
                f"• Date: {date_val}\n"
                f"• Items: {items_summary}"
            )
            return {"answer": answer, "sources": ORDER_SERVICE_SOURCE}

        # ── Recent orders list ────────────────────────────────────────────────
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
                    "answer": "You don't have any orders yet.",
                    "sources": ORDER_SERVICE_SOURCE,
                }

            DISPLAY_LIMIT = 5
            displayed = orders[:DISPLAY_LIMIT]
            lines = ["Here are your recent OrganicKart orders:\n"]
            lines.extend(self._format_order_block(o) for o in displayed)
            if len(orders) > DISPLAY_LIMIT:
                lines.append(
                    f"\n(Showing the {DISPLAY_LIMIT} most recent orders out of {len(orders)} total."
                    " Ask about a specific order ID for full details.)"
                )

            return {"answer": "\n\n".join(lines).strip(), "sources": ORDER_SERVICE_SOURCE}

        # ── Filtered orders ───────────────────────────────────────────────────
        if intent == "FILTERED_ORDERS":
            flt = self._detect_order_filter(query)
            if flt.get("unsupported"):
                return {
                    "answer": (
                        "I can filter orders by payment status (PAID, PAYMENT_PENDING, FAILED) "
                        f"or by month (e.g., September). {flt['unsupported']}"
                    ),
                    "sources": ORDER_SERVICE_SOURCE,
                }
            if flt.get("ambiguous"):
                return {
                    "answer": (
                        "Could you please specify how you would like to filter your orders? "
                        "You can filter by payment status (PAID, PAYMENT_PENDING, FAILED) or by month (e.g., September)."
                    ),
                    "sources": ORDER_SERVICE_SOURCE,
                }

            payment_status_filter = flt["payment_status"]
            month_filter = flt["month"]  # e.g. '2026-08' or '08'

            res = await self.order_client.get_recent_orders(token, user_id)
            if not res["success"]:
                return {
                    "answer": res["detail"],
                    "sources": ORDER_SERVICE_SOURCE,
                }

            all_orders = res["orders"]
            if not all_orders:
                return {
                    "answer": "You don't have any orders yet.",
                    "sources": ORDER_SERVICE_SOURCE,
                }

            filtered = all_orders
            applied_filters: list[str] = []

            if payment_status_filter:
                filtered = [
                    o for o in filtered
                    if (o.get("payment_status") or "").upper() == payment_status_filter
                ]
                applied_filters.append(f"payment status = {payment_status_filter}")

            if month_filter:
                # month_filter is either 'YYYY-MM' or 'MM'
                def _matches_month(order_obj: dict[str, Any]) -> bool:
                    created_raw = str(order_obj.get("created_at") or "").strip()
                    if not created_raw:
                        return False
                    if len(month_filter) == 7:  # 'YYYY-MM'
                        return created_raw.startswith(month_filter)
                    # Month-only 'MM': check standard date separator positions (YYYY-MM-...)
                    if len(created_raw) >= 7 and created_raw[4] in ("-", "/"):
                        return created_raw[5:7] == month_filter
                    return False

                filtered = [o for o in filtered if _matches_month(o)]
                applied_filters.append(f"month = {month_filter}")

            filter_desc = " and ".join(applied_filters)
            if not filtered:
                return {
                    "answer": f"No orders found matching the filter ({filter_desc}).",
                    "sources": ORDER_SERVICE_SOURCE,
                }

            DISPLAY_LIMIT = 5
            displayed = filtered[:DISPLAY_LIMIT]
            lines = [f"Filtered orders ({filter_desc}):\n"]
            lines.extend(self._format_order_block(o) for o in displayed)
            if len(filtered) > DISPLAY_LIMIT:
                lines.append(
                    f"\n(Showing {DISPLAY_LIMIT} of {len(filtered)} matching orders."
                    " Ask about a specific order ID for full details.)"
                )

            return {"answer": "\n\n".join(lines).strip(), "sources": ORDER_SERVICE_SOURCE}

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

    @staticmethod
    def _handle_greeting_or_chitchat(kind: str) -> dict[str, Any]:
        if kind == "THANKS":
            answer = "You're very welcome! Please let me know if you need any other help with OrganicKart products, your orders, or our store policies."
        elif kind == "FAREWELL":
            answer = "Goodbye! Thank you for visiting OrganicKart. Have a wonderful and healthy day!"
        elif kind == "INTRO":
            answer = (
                "I am **OrganicKart's AI Customer Assistant**. Here is how I can assist you:\n"
                "- **Live Product Catalog**: Check real-time prices, stock availability, and organic certifications.\n"
                "- **Order & Delivery Tracking**: View your recent orders, check delivery status, and review cart items.\n"
                "- **Store Policies**: Learn about our delivery hours, returns, refunds, cancellations, and quality standards.\n"
                "- **Organic Education**: Ask general questions about organic farming, nutrition, and produce.\n\n"
                "How can I help you today?"
            )
        else:
            answer = (
                "Hello! Welcome to **OrganicKart**. I am your AI assistant, ready to help you with:\n"
                "- Checking product prices, stock, and availability\n"
                "- Tracking your orders, order history, and delivery status\n"
                "- Official OrganicKart policies on delivery, returns, and refunds\n"
                "- General educational questions about organic food and agriculture\n\n"
                "What can I help you with today?"
            )
        return {"answer": answer, "sources": []}

    @staticmethod
    def _handle_clarification(query: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
        meta = meta or {}
        clarification_type = meta.get("type", "")
        if clarification_type == "filter_clarification":
            flt = meta.get("filter", {})
            if flt.get("unsupported"):
                answer = (
                    "I can filter orders by payment status (PAID, PAYMENT_PENDING, FAILED) "
                    f"or by month (e.g., September). {flt['unsupported']}"
                )
            else:
                answer = (
                    "Could you please specify how you would like to filter your orders? "
                    "You can filter by payment status (PAID, PAYMENT_PENDING, FAILED) or by month (e.g., September)."
                )
            return {"answer": answer, "sources": ORDER_SERVICE_SOURCE}

        if clarification_type == "order_ambiguous":
            return {
                "answer": (
                    "Could you please provide your order ID to check its details, or "
                    "would you like to see your recent orders?"
                ),
                "sources": ORDER_SERVICE_SOURCE,
            }

        return {
            "answer": (
                "Could you please provide more details? I can help you with checking "
                "product prices and availability, tracking orders, store policies (delivery, returns, refunds), "
                "or general organic food questions."
            ),
            "sources": [],
        }

    async def _handle_general_knowledge_query(self, query: str, started_at: float) -> dict[str, Any]:
        retrieval_started_at = perf_counter()
        retrieval_data = self.retriever.retrieve(query)
        retrieval_duration = perf_counter() - retrieval_started_at

        # Educational queries must ONLY consider educational documents (e.g. organic_products.md).
        # Store policies, operational FAQs, and company overviews must NOT be used as educational context.
        # Chunks must achieve a strict relevance score (>= 0.15) to be considered grounded context.
        educational_sources = []
        educational_chunks = []

        raw_results = retrieval_data.get("raw_results", [])
        for item in raw_results:
            source_file = str(item.get("source", "")).lower()
            score = item.get("score", 0.0)
            content = item.get("content", "").strip()
            if any(p in source_file for p in ("policy", "policies", "faq", "overview")):
                continue
            if score >= 0.15 and content:
                educational_chunks.append(content)
                educational_sources.append({
                    "document": item.get("source", "unknown"),
                    "title": item.get("title", "Organic Products Guide"),
                    "score": score,
                })

        if educational_chunks:
            context_text = "\n\n---\n\n".join(educational_chunks)
            user_prompt = f"""Supporting OrganicKart Knowledge Context:
{context_text}

Educational Question:
{query}

Answer the educational question clearly and concisely. Clearly distinguish general educational explanations from verified OrganicKart-specific claims:"""
            final_sources = educational_sources
        else:
            user_prompt = f"""Educational Question:
{query}

Answer the educational question clearly, objectively, and concisely based on established agricultural, nutritional, and general knowledge. Do not invent store policies or specific OrganicKart claims:"""
            final_sources = GENERAL_KNOWLEDGE_SOURCE

        llm_started_at = perf_counter()
        answer = await self.llm_service.generate(user_prompt, system_prompt=GENERAL_KNOWLEDGE_SYSTEM_PROMPT)
        logger.info(
            "AI route=general_knowledge retrieval=%.3fs llm=%.3fs total=%.3fs",
            retrieval_duration,
            perf_counter() - llm_started_at,
            perf_counter() - started_at,
        )
        return {"answer": answer, "sources": final_sources}

    async def _execute_intent(
        self,
        intent: CustomerIntent,
        query: str,
        user_id: int | None,
        token: str | None,
        started_at: float,
        meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        meta = meta or {}

        if intent == CustomerIntent.GREETING_OR_CHITCHAT:
            return self._handle_greeting_or_chitchat(meta.get("kind", "GREETING"))

        if intent == CustomerIntent.CLARIFICATION_REQUIRED:
            return self._handle_clarification(query, meta)

        if intent == CustomerIntent.ORDER_QUERY:
            sub_type = meta.get("sub_type")
            if sub_type == "cart":
                return await self._handle_live_cart_tool(user_id, token)
            if sub_type == "delivery":
                return await self._handle_live_delivery_tool(user_id, token, query)
            if sub_type == "notification":
                return await self._handle_live_notification_tool(user_id, token, query)

            order_intent = meta.get("order_intent")
            order_ids = meta.get("order_ids")
            if not order_intent:
                _, order_intent, order_ids = self._is_live_order_query(query)
            return await self._handle_live_order_tool(order_intent, order_ids or [], user_id, token, query)

        if intent == CustomerIntent.PRODUCT_QUERY:
            product_id = meta.get("product_id")
            search = meta.get("search")
            if product_id is None and search is None and not meta.get("resolved"):
                _, product_id, search = self._live_product_query(query)
            return await self._handle_live_product_tool(product_id, search)

        if intent == CustomerIntent.POLICY_KB:
            if meta.get("web") or self._is_current_web_query(query):
                return await self._handle_web_query(query)
            return await self._handle_rag_query(query, started_at)

        if intent == CustomerIntent.GENERAL_KNOWLEDGE:
            return await self._handle_general_knowledge_query(query, started_at)

        return await self._handle_rag_query(query, started_at)

    async def _handle_multi_intent_query(
        self,
        sub_tasks: list[tuple[CustomerIntent, str]],
        user_id: int | None,
        token: str | None,
        started_at: float,
    ) -> dict[str, Any]:
        section_titles = {
            CustomerIntent.PRODUCT_QUERY: "Product Information",
            CustomerIntent.ORDER_QUERY: "Order Details",
            CustomerIntent.POLICY_KB: "OrganicKart Policies",
            CustomerIntent.GENERAL_KNOWLEDGE: "Educational Information",
            CustomerIntent.CLARIFICATION_REQUIRED: "Clarification Needed",
        }

        sections: list[str] = []
        combined_sources: list[dict[str, Any]] = []
        seen_sources: set[tuple[str, str]] = set()

        for intent, sub_query in sub_tasks:
            _, meta = self._classify_single_intent(sub_query)
            resp = await self._execute_intent(intent, sub_query, user_id, token, started_at, meta)
            title = section_titles.get(intent, "Information")
            sections.append(f"### {title}\n{resp.get('answer', '')}")
            for src in resp.get("sources", []):
                key = (src.get("document", ""), src.get("title", ""))
                if key not in seen_sources:
                    seen_sources.add(key)
                    combined_sources.append(src)

        synthesized_answer = "\n\n---\n\n".join(sections)
        return {
            "answer": synthesized_answer,
            "sources": combined_sources,
        }

    async def handle_query(
        self,
        query: str,
        user_id: int | None = None,
        token: str | None = None,
    ) -> dict[str, Any]:
        """
        Analyze customer request and route to the appropriate capability:
          - GREETING_OR_CHITCHAT: conversational greetings and guidance
          - CLARIFICATION_REQUIRED: ambiguous queries requiring user clarification
          - ORDER_QUERY: authenticated customer order, cart, delivery, and notifications
          - PRODUCT_QUERY: live Product Service catalog search, prices, and stock
          - POLICY_KB: OrganicKart official policies grounded in RAG knowledge
          - GENERAL_KNOWLEDGE: educational explanations via LLM without store invention
          - MULTI_INTENT: combined multiple capabilities synthesized cleanly
        """
        started_at = perf_counter()
        intent, meta = self.classify_intent(query)
        logger.info("AI route intent=%s user_id=%s query=%s", intent.value, user_id, query[:80])

        if intent == CustomerIntent.MULTI_INTENT:
            sub_tasks = meta.get("sub_tasks", [])
            response = await self._handle_multi_intent_query(sub_tasks, user_id, token, started_at)
            response["intent"] = intent.value
            return response

        response = await self._execute_intent(intent, query, user_id, token, started_at, meta)
        response["intent"] = intent.value
        return response
