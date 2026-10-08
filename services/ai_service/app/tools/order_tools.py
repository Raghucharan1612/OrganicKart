import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class OrderServiceClient:
    """
    HTTP client for calling the internal Order Service API (:8004) from AI Service.
    Uses the authenticated customer's JWT token for authorization and identity.
    """

    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or settings.ORDER_SERVICE_URL).rstrip("/")
        self.timeout = timeout or settings.ORDER_SERVICE_TIMEOUT_SECONDS

    async def get_my_cart(self, token: str, user_id: int) -> dict[str, Any]:
        """Fetch the authenticated customer's cart from Order Service."""
        if not token:
            return {
                "success": False,
                "error": "unauthorized",
                "detail": "Authentication token is missing.",
            }

        url = f"{self.base_url}/api/v1/cart"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)

            if response.status_code == 401:
                return {
                    "success": False,
                    "error": "unauthorized",
                    "detail": "Unauthorized access to cart operations.",
                }

            if response.status_code == 403:
                return {
                    "success": False,
                    "error": "forbidden",
                    "detail": "Forbidden access to cart operations.",
                }

            if response.status_code != 200:
                return {
                    "success": False,
                    "error": "invalid_response",
                    "detail": f"Order Service returned status {response.status_code}.",
                }

            cart = response.json()
            if not isinstance(cart, dict) or not isinstance(cart.get("items"), list):
                return {
                    "success": False,
                    "error": "invalid_response",
                    "detail": "Invalid cart format returned by Order Service.",
                }

            # Defense in depth: do not expose a cart returned for another user.
            if cart.get("user_id") != user_id:
                logger.warning("Order Service returned cart with unexpected owner user_id=%s", user_id)
                return {
                    "success": False,
                    "error": "forbidden",
                    "detail": "The requested cart does not belong to your account.",
                }

            return {"success": True, "cart": cart}

        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "timeout",
                "detail": "Order Service cart request timed out. Please try again later.",
            }
        except (httpx.ConnectError, httpx.RequestError):
            return {
                "success": False,
                "error": "unavailable",
                "detail": "Order Service is currently unavailable. Please try again later.",
            }
        except Exception:
            logger.exception("Unexpected error fetching cart for user_id=%s", user_id)
            return {
                "success": False,
                "error": "invalid_response",
                "detail": "An unexpected error occurred while communicating with Order Service.",
            }

    async def get_recent_orders(self, token: str, user_id: int) -> dict[str, Any]:
        """
        Fetch recent orders for the authenticated customer.
        Endpoint: GET /api/v1/orders
        """
        if not token:
            return {
                "success": False,
                "error": "unauthorized",
                "detail": "Authentication token is missing.",
            }

        url = f"{self.base_url}/api/v1/orders"
        headers = {"Authorization": f"Bearer {token}"}
        logger.warning("AI_ORDER_TRACE step=request_start operation=get_recent_orders user_id=%s", user_id)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)

            logger.warning(
                "AI_ORDER_TRACE step=response operation=get_recent_orders user_id=%s status=%s",
                user_id,
                response.status_code,
            )

            if response.status_code == 401:
                return {
                    "success": False,
                    "error": "unauthorized",
                    "detail": "Unauthorized access to order service.",
                }

            if response.status_code == 403:
                return {
                    "success": False,
                    "error": "forbidden",
                    "detail": "Forbidden access to order operations.",
                }

            if response.status_code != 200:
                return {
                    "success": False,
                    "error": "invalid_response",
                    "detail": f"Order Service returned status {response.status_code}.",
                }

            orders = response.json()
            if not isinstance(orders, list):
                return {
                    "success": False,
                    "error": "invalid_response",
                    "detail": "Invalid order list format returned by Order Service.",
                }

            # Security verification: Ensure all returned orders belong to the authenticated user_id
            user_orders = [o for o in orders if isinstance(o, dict) and o.get("user_id") == user_id]

            return {
                "success": True,
                "orders": user_orders,
            }

        except httpx.TimeoutException as exc:
            logger.warning(
                "AI_ORDER_TRACE step=exception operation=get_recent_orders user_id=%s type=%s repr=%r",
                user_id,
                type(exc).__name__,
                exc,
            )
            return {
                "success": False,
                "error": "timeout",
                "detail": "Order Service request timed out. Please try again later.",
            }
        except (httpx.ConnectError, httpx.RequestError) as exc:
            logger.warning(
                "AI_ORDER_TRACE step=exception operation=get_recent_orders user_id=%s type=%s repr=%r",
                user_id,
                type(exc).__name__,
                exc,
            )
            return {
                "success": False,
                "error": "unavailable",
                "detail": "Order Service is currently unavailable. Please try again later.",
            }
        except Exception as exc:
            logger.exception(
                "AI_ORDER_TRACE step=exception operation=get_recent_orders user_id=%s type=%s repr=%r",
                user_id,
                type(exc).__name__,
                exc,
            )
            return {
                "success": False,
                "error": "invalid_response",
                "detail": "An unexpected error occurred while communicating with Order Service.",
            }

    async def get_order_by_id(self, order_id: int, token: str, user_id: int) -> dict[str, Any]:
        """
        Fetch a specific order by ID for the authenticated customer.
        Endpoint: GET /api/v1/orders/{order_id}
        """
        if not token:
            return {
                "success": False,
                "error": "unauthorized",
                "detail": "Authentication token is missing.",
            }

        url = f"{self.base_url}/api/v1/orders/{order_id}"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)

            if response.status_code in (404, 403):
                return {
                    "success": False,
                    "error": "not_found",
                    "detail": f"Order #{order_id} was not found or does not belong to your account.",
                }

            if response.status_code == 401:
                return {
                    "success": False,
                    "error": "unauthorized",
                    "detail": "Unauthorized access to order service.",
                }

            if response.status_code != 200:
                return {
                    "success": False,
                    "error": "invalid_response",
                    "detail": f"Order Service returned status {response.status_code}.",
                }

            order_data = response.json()
            if not isinstance(order_data, dict):
                return {
                    "success": False,
                    "error": "invalid_response",
                    "detail": "Invalid order data format returned by Order Service.",
                }

            # Security verification: Validate order ownership explicitly
            if order_data.get("user_id") != user_id:
                return {
                    "success": False,
                    "error": "forbidden",
                    "detail": f"Order #{order_id} was not found or does not belong to your account.",
                }

            return {
                "success": True,
                "order": order_data,
            }

        except httpx.TimeoutException:
            logger.warning("Order Service request timed out: %s", url)
            return {
                "success": False,
                "error": "timeout",
                "detail": "Order Service request timed out. Please try again later.",
            }
        except (httpx.ConnectError, httpx.RequestError) as exc:
            logger.warning("Order Service transport failure: %s", exc)
            return {
                "success": False,
                "error": "unavailable",
                "detail": "Order Service is currently unavailable. Please try again later.",
            }
        except Exception as exc:
            logger.error("Unexpected error fetching order #%d: %s", order_id, exc)
            return {
                "success": False,
                "error": "invalid_response",
                "detail": "An unexpected error occurred while communicating with Order Service.",
            }
