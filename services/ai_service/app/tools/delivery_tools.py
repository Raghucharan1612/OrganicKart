import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class DeliveryServiceClient:
    """Read customer-owned delivery tracking data from Delivery Service."""

    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or settings.DELIVERY_SERVICE_URL).rstrip("/")
        self.timeout = timeout or settings.DELIVERY_SERVICE_TIMEOUT_SECONDS

    async def get_my_deliveries(self, token: str, user_id: int) -> dict[str, Any]:
        if not token:
            return {"success": False, "error": "unauthorized", "detail": "Authentication token is missing."}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/deliveries",
                    headers={"Authorization": f"Bearer {token}"},
                )

            if response.status_code == 401:
                return {"success": False, "error": "unauthorized", "detail": "Unauthorized access to delivery tracking."}
            if response.status_code == 403:
                return {"success": False, "error": "forbidden", "detail": "Forbidden access to delivery tracking."}
            if response.status_code != 200:
                return {"success": False, "error": "invalid_response", "detail": f"Delivery Service returned status {response.status_code}."}

            deliveries = response.json()
            if not isinstance(deliveries, list) or not all(isinstance(delivery, dict) for delivery in deliveries):
                return {"success": False, "error": "invalid_response", "detail": "Invalid delivery list format returned by Delivery Service."}
            if any(delivery.get("user_id") != user_id for delivery in deliveries):
                logger.warning("Delivery Service returned an unexpected delivery owner for user_id=%s", user_id)
                return {"success": False, "error": "forbidden", "detail": "The requested delivery does not belong to your account."}
            return {"success": True, "deliveries": deliveries}
        except httpx.TimeoutException:
            return {"success": False, "error": "timeout", "detail": "Delivery Service request timed out. Please try again later."}
        except (httpx.ConnectError, httpx.RequestError):
            return {"success": False, "error": "unavailable", "detail": "Delivery Service is currently unavailable. Please try again later."}
        except Exception:
            logger.exception("Unexpected error fetching deliveries for user_id=%s", user_id)
            return {"success": False, "error": "invalid_response", "detail": "An unexpected error occurred while communicating with Delivery Service."}
