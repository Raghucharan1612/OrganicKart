import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class ProductServiceClient:
    """Read the public, customer-visible catalog from Product Service."""

    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or settings.PRODUCT_SERVICE_URL).rstrip("/")
        self.timeout = timeout or settings.PRODUCT_SERVICE_TIMEOUT_SECONDS

    async def search_products(self, query: str | None = None) -> dict[str, Any]:
        params = {"search": query} if query else None
        return await self._get_products("/api/v1/products/", params=params)

    async def get_my_products(self, token: str | None = None) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/products/mine", headers=headers)

            if response.status_code == 401:
                return {"success": False, "error": "unauthorized", "detail": "Could not validate seller credentials."}
            if response.status_code == 403:
                return {"success": False, "error": "forbidden", "detail": "You do not have permission to view vendor products."}
            if response.status_code != 200:
                return {"success": False, "error": "invalid_response", "detail": f"Product Service returned status {response.status_code}."}

            products = response.json()
            if not isinstance(products, list) or not all(isinstance(p, dict) for p in products):
                return {"success": False, "error": "invalid_response", "detail": "Invalid products list format returned by Product Service."}
            return {"success": True, "products": products}
        except httpx.TimeoutException:
            return {"success": False, "error": "timeout", "detail": "Product Service request timed out. Please try again later."}
        except (httpx.ConnectError, httpx.RequestError):
            return {"success": False, "error": "unavailable", "detail": "Product Service is currently unavailable. Please try again later."}
        except Exception:
            logger.exception("Unexpected error fetching vendor products")
            return {"success": False, "error": "invalid_response", "detail": "An unexpected error occurred while communicating with Product Service."}

    async def get_admin_products(
        self,
        token: str | None,
        certification: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        """Read the ADMIN catalog view. Identity is supplied only by the JWT."""
        if not token:
            return {"success": False, "error": "unauthorized", "detail": "Authentication token is missing."}

        params: dict[str, str | int] = {"page": 1, "page_size": 100}
        if certification:
            params["certification"] = certification
        if search:
            params["search"] = search

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/products/",
                    headers={"Authorization": f"Bearer {token}"},
                    params=params,
                )

            if response.status_code == 401:
                return {"success": False, "error": "unauthorized", "detail": "Could not validate admin credentials."}
            if response.status_code == 403:
                return {"success": False, "error": "forbidden", "detail": "You do not have permission to view the admin catalog."}
            if response.status_code != 200:
                return {"success": False, "error": "invalid_response", "detail": f"Product Service returned status {response.status_code}."}

            payload = response.json()
            if not isinstance(payload, dict) or not isinstance(payload.get("items"), list) or not isinstance(payload.get("total"), int):
                return {"success": False, "error": "invalid_response", "detail": "Invalid admin catalog format returned by Product Service."}
            if not all(isinstance(product, dict) for product in payload["items"]):
                return {"success": False, "error": "invalid_response", "detail": "Invalid admin catalog item format returned by Product Service."}
            return {"success": True, "products": payload["items"], "total": payload["total"]}
        except httpx.TimeoutException:
            return {"success": False, "error": "timeout", "detail": "Product Service request timed out. Please try again later."}
        except (httpx.ConnectError, httpx.RequestError):
            return {"success": False, "error": "unavailable", "detail": "Product Service is currently unavailable. Please try again later."}
        except Exception:
            logger.exception("Unexpected error fetching admin product catalog")
            return {"success": False, "error": "invalid_response", "detail": "An unexpected error occurred while communicating with Product Service."}

    async def get_pending_certification_products(self, token: str | None) -> dict[str, Any]:
        """Return the current ADMIN-visible PENDING certification queue."""
        return await self.get_admin_products(token, certification="PENDING")

    async def get_admin_low_stock_products(self, token: str | None) -> dict[str, Any]:
        """Read the fixed server-side low-stock threshold view as ADMIN."""
        if not token:
            return {"success": False, "error": "unauthorized", "detail": "Authentication token is missing."}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/products/admin/low-stock",
                    headers={"Authorization": f"Bearer {token}"},
                )
            if response.status_code == 401:
                return {"success": False, "error": "unauthorized", "detail": "Could not validate admin credentials."}
            if response.status_code == 403:
                return {"success": False, "error": "forbidden", "detail": "You do not have permission to view low-stock products."}
            if response.status_code != 200:
                return {"success": False, "error": "invalid_response", "detail": f"Product Service returned status {response.status_code}."}
            payload = response.json()
            if (
                not isinstance(payload, dict)
                or not isinstance(payload.get("threshold"), int)
                or not isinstance(payload.get("items"), list)
                or not all(isinstance(product, dict) for product in payload["items"])
            ):
                return {"success": False, "error": "invalid_response", "detail": "Invalid low-stock response returned by Product Service."}
            return {"success": True, "threshold": payload["threshold"], "products": payload["items"]}
        except httpx.TimeoutException:
            return {"success": False, "error": "timeout", "detail": "Product Service low-stock request timed out. Please try again later."}
        except (httpx.ConnectError, httpx.RequestError):
            return {"success": False, "error": "unavailable", "detail": "Product Service is currently unavailable. Please try again later."}
        except Exception:
            logger.exception("Unexpected error fetching admin low-stock products")
            return {"success": False, "error": "invalid_response", "detail": "An unexpected error occurred while communicating with Product Service."}

    async def get_admin_product(self, product_id: int, token: str | None) -> dict[str, Any]:
        """Read a single product as ADMIN, including non-customer-visible fields."""
        if not token:
            return {"success": False, "error": "unauthorized", "detail": "Authentication token is missing."}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/products/{product_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )

            if response.status_code == 404:
                return {"success": False, "error": "not_found", "detail": "Product not found."}
            if response.status_code == 401:
                return {"success": False, "error": "unauthorized", "detail": "Could not validate admin credentials."}
            if response.status_code == 403:
                return {"success": False, "error": "forbidden", "detail": "You do not have permission to view this product."}
            if response.status_code != 200:
                return {"success": False, "error": "invalid_response", "detail": f"Product Service returned status {response.status_code}."}
            product = response.json()
            if not isinstance(product, dict):
                return {"success": False, "error": "invalid_response", "detail": "Invalid product format returned by Product Service."}
            return {"success": True, "product": product}
        except httpx.TimeoutException:
            return {"success": False, "error": "timeout", "detail": "Product Service request timed out. Please try again later."}
        except (httpx.ConnectError, httpx.RequestError):
            return {"success": False, "error": "unavailable", "detail": "Product Service is currently unavailable. Please try again later."}
        except Exception:
            logger.exception("Unexpected error fetching admin product_id=%s", product_id)
            return {"success": False, "error": "invalid_response", "detail": "An unexpected error occurred while communicating with Product Service."}

    async def get_product(self, product_id: int) -> dict[str, Any]:

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/products/{product_id}")

            if response.status_code == 404:
                return {"success": False, "error": "not_found", "detail": "That product is not currently available."}
            if response.status_code != 200:
                return {"success": False, "error": "invalid_response", "detail": f"Product Service returned status {response.status_code}."}

            product = response.json()
            if not isinstance(product, dict):
                return {"success": False, "error": "invalid_response", "detail": "Invalid product format returned by Product Service."}
            return {"success": True, "product": product}
        except httpx.TimeoutException:
            return {"success": False, "error": "timeout", "detail": "Product Service request timed out. Please try again later."}
        except (httpx.ConnectError, httpx.RequestError):
            return {"success": False, "error": "unavailable", "detail": "Product Service is currently unavailable. Please try again later."}
        except Exception:
            logger.exception("Unexpected error fetching product_id=%s", product_id)
            return {"success": False, "error": "invalid_response", "detail": "An unexpected error occurred while communicating with Product Service."}

    async def _get_products(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}{path}", params=params)

            if response.status_code != 200:
                return {"success": False, "error": "invalid_response", "detail": f"Product Service returned status {response.status_code}."}

            payload = response.json()
            products = payload.get("items") if isinstance(payload, dict) else payload
            if not isinstance(products, list) or not all(isinstance(product, dict) for product in products):
                return {"success": False, "error": "invalid_response", "detail": "Invalid product list format returned by Product Service."}
            return {"success": True, "products": products}
        except httpx.TimeoutException:
            return {"success": False, "error": "timeout", "detail": "Product Service request timed out. Please try again later."}
        except (httpx.ConnectError, httpx.RequestError):
            return {"success": False, "error": "unavailable", "detail": "Product Service is currently unavailable. Please try again later."}
        except Exception:
            logger.exception("Unexpected error searching products")
            return {"success": False, "error": "invalid_response", "detail": "An unexpected error occurred while communicating with Product Service."}
