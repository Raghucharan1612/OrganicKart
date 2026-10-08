import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class NotificationServiceClient:
    """Read customer-owned notifications from Notification Service."""

    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or settings.NOTIFICATION_SERVICE_URL).rstrip("/")
        self.timeout = timeout or settings.NOTIFICATION_SERVICE_TIMEOUT_SECONDS

    async def get_my_notifications(self, token: str, user_id: int) -> dict[str, Any]:
        if not token:
            return {"success": False, "error": "unauthorized", "detail": "Authentication token is missing."}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/notifications",
                    headers={"Authorization": f"Bearer {token}"},
                )

            if response.status_code == 401:
                return {"success": False, "error": "unauthorized", "detail": "Unauthorized access to notifications."}
            if response.status_code == 403:
                return {"success": False, "error": "forbidden", "detail": "Forbidden access to notifications."}
            if response.status_code != 200:
                return {"success": False, "error": "invalid_response", "detail": f"Notification Service returned status {response.status_code}."}

            notifications = response.json()
            if not isinstance(notifications, list) or not all(isinstance(n, dict) for n in notifications):
                return {"success": False, "error": "invalid_response", "detail": "Invalid notification list format returned by Notification Service."}

            if any(n.get("user_id") != user_id for n in notifications):
                logger.warning("Notification Service returned an unexpected notification owner for user_id=%s", user_id)
                return {"success": False, "error": "forbidden", "detail": "The requested notification does not belong to your account."}

            return {"success": True, "notifications": notifications}
        except httpx.TimeoutException:
            return {"success": False, "error": "timeout", "detail": "Notification Service request timed out. Please try again later."}
        except (httpx.ConnectError, httpx.RequestError):
            return {"success": False, "error": "unavailable", "detail": "Notification Service is currently unavailable. Please try again later."}
        except Exception:
            logger.exception("Unexpected error fetching notifications for user_id=%s", user_id)
            return {"success": False, "error": "invalid_response", "detail": "An unexpected error occurred while communicating with Notification Service."}
