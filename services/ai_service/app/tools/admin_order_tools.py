import logging
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class AdminOrderServiceClient:
    """Read-only client for the ADMIN aggregate order analytics endpoint."""

    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or settings.ORDER_SERVICE_URL).rstrip("/")
        self.timeout = timeout or settings.ORDER_SERVICE_TIMEOUT_SECONDS

    async def get_order_analytics(self, token: str | None) -> dict[str, Any]:
        if not token:
            return {
                "success": False,
                "error": "unauthorized",
                "detail": "Authentication token is missing.",
            }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/orders/admin/analytics",
                    headers={"Authorization": f"Bearer {token}"},
                )
            if response.status_code == 401:
                return {"success": False, "error": "unauthorized", "detail": "Unauthorized access to order analytics."}
            if response.status_code == 403:
                return {"success": False, "error": "forbidden", "detail": "Forbidden access to order analytics."}
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": "invalid_response",
                    "detail": f"Order Service returned status {response.status_code}.",
                }
            analytics = response.json()
            required_types = {
                "total_orders": int,
                "orders_by_status": dict,
                "payment_status_breakdown": dict,
                "cancelled_orders": int,
                "monthly_sales_summary": list,
                "recent_orders": list,
            }
            if not isinstance(analytics, dict) or any(
                not isinstance(analytics.get(field), expected_type)
                for field, expected_type in required_types.items()
            ):
                return {
                    "success": False,
                    "error": "invalid_response",
                    "detail": "Invalid order analytics format returned by Order Service.",
                }
            try:
                Decimal(str(analytics.get("total_revenue")))
            except (InvalidOperation, ValueError, TypeError):
                return {
                    "success": False,
                    "error": "invalid_response",
                    "detail": "Invalid order analytics format returned by Order Service.",
                }
            return {"success": True, "analytics": analytics}
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "timeout",
                "detail": "Order Service analytics request timed out. Please try again later.",
            }
        except httpx.RequestError as exc:
            logger.warning("Admin order analytics transport failure: %s", type(exc).__name__)
            return {
                "success": False,
                "error": "unavailable",
                "detail": "Order Service is currently unavailable. Please try again later.",
            }
        except Exception:
            logger.exception("Unexpected error retrieving admin order analytics")
            return {
                "success": False,
                "error": "invalid_response",
                "detail": "An unexpected error occurred while communicating with Order Service.",
            }

    async def get_business_insights(self, token: str | None) -> dict[str, Any]:
        if not token:
            return {"success": False, "error": "unauthorized", "detail": "Authentication token is missing."}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/orders/admin/business-insights",
                    headers={"Authorization": f"Bearer {token}"},
                )
            if response.status_code == 401:
                return {"success": False, "error": "unauthorized", "detail": "Unauthorized access to business insights."}
            if response.status_code == 403:
                return {"success": False, "error": "forbidden", "detail": "Forbidden access to business insights."}
            if response.status_code != 200:
                return {"success": False, "error": "invalid_response", "detail": f"Order Service returned status {response.status_code}."}
            insights = response.json()
            required_types = {
                "vendor_sales": list,
                "product_sales": list,
                "current_period": str,
                "previous_period": str,
                "sales_decline_available": bool,
                "sales_declines": list,
            }
            if not isinstance(insights, dict) or any(
                not isinstance(insights.get(field), expected_type)
                for field, expected_type in required_types.items()
            ):
                return {"success": False, "error": "invalid_response", "detail": "Invalid business insights format returned by Order Service."}
            return {"success": True, "insights": insights}
        except httpx.TimeoutException:
            return {"success": False, "error": "timeout", "detail": "Order Service business insights request timed out. Please try again later."}
        except httpx.RequestError as exc:
            logger.warning("Admin business insights transport failure: %s", type(exc).__name__)
            return {"success": False, "error": "unavailable", "detail": "Order Service is currently unavailable. Please try again later."}
        except Exception:
            logger.exception("Unexpected error retrieving admin business insights")
            return {"success": False, "error": "invalid_response", "detail": "An unexpected error occurred while communicating with Order Service."}
