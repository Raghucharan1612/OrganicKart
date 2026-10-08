from __future__ import annotations

import logging
import re
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request, status

from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")

SERVICE_MAP = {
    "auth": settings.AUTH_SERVICE_URL,
    "users": settings.AUTH_SERVICE_URL,
    "ai": settings.AI_SERVICE_URL,
    "products": settings.PRODUCT_SERVICE_URL,
    "categories": settings.PRODUCT_SERVICE_URL,
    "cart": settings.ORDER_SERVICE_URL,
    "orders": settings.ORDER_SERVICE_URL,
    "deliveries": settings.DELIVERY_SERVICE_URL,
    "notifications": settings.NOTIFICATION_SERVICE_URL,
}


def _build_target_url(service_name: str, path: str) -> str:
    base_url = SERVICE_MAP.get(service_name)
    if not base_url:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unknown service route: {service_name}",
        )
    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{base_url.rstrip('/')}{normalized_path}"


def _service_path(prefix: str, path: str) -> str:
    return f"{prefix}/{path}" if path else prefix


def _safe_exception_repr(exc: BaseException | None) -> str:
    if exc is None:
        return ""
    value = repr(exc)
    value = re.sub(r"(://[^:\s'\"/]+:)[^@\s'\"/]+@", r"\1***@", value)
    value = re.sub(r"(?i)(bearer\s+)[^\s'\"]+", r"\1***", value)
    value = re.sub(r"(?i)((?:token|secret|password|authorization)=)[^,\s'\"]+", r"\1***", value)
    return value[:500]


async def _forward_request(request: Request, service_name: str, path: str) -> Any:
    url = _build_target_url(service_name, path)

    headers = {k: v for k, v in request.headers.items() if k.lower() not in {"host", "content-length"}}
    body = await request.body()

    if service_name == "ai":
        logger.warning(
            "AI_GATEWAY_TRACE step=forward_start method=%s path=%s authorization_present=%s",
            request.method,
            path,
            any(key.lower() == "authorization" for key in headers),
        )

    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body if body else None,
                params=request.query_params,
            )

        if service_name == "ai":
            logger.warning(
                "AI_GATEWAY_TRACE step=upstream_response method=%s path=%s status=%s",
                request.method,
                path,
                response.status_code,
            )
    except httpx.HTTPError as exc:
        cause = exc.__cause__
        diagnostic = f"{type(exc).__name__}: {_safe_exception_repr(exc)}"
        cause_diagnostic = f"{type(cause).__name__}: {_safe_exception_repr(cause)}" if cause else None
        logger.warning(
            "Upstream transport failure service=%s exception=%s cause=%s",
            service_name,
            diagnostic,
            cause_diagnostic,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Upstream service unavailable for {service_name}: {diagnostic}",
        ) from exc

    try:
        payload = response.json()
    except ValueError:
        payload = response.text

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=payload if isinstance(payload, dict) else {"detail": payload},
        )

    return payload


@router.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def auth_proxy(request: Request, path: str) -> Any:
    return await _forward_request(request, "auth", f"/api/v1/auth/{path}")


@router.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def users_proxy(request: Request, path: str) -> Any:
    return await _forward_request(request, "users", f"/api/v1/users/{path}")


@router.api_route("/products/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def products_proxy(request: Request, path: str) -> Any:
    return await _forward_request(request, "products", f"/api/v1/products/{path}")


@router.api_route("/products", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def products_root_proxy(request: Request) -> Any:
    return await _forward_request(request, "products", "/api/v1/products/")


@router.api_route("/categories/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def categories_proxy(request: Request, path: str) -> Any:
    return await _forward_request(request, "categories", f"/api/v1/categories/{path}")


@router.api_route("/categories", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def categories_root_proxy(request: Request) -> Any:
    return await _forward_request(request, "categories", "/api/v1/categories/")


@router.api_route("/cart/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def cart_proxy(request: Request, path: str) -> Any:
    return await _forward_request(request, "cart", _service_path("/api/v1/cart", path))


@router.api_route("/cart", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def cart_root_proxy(request: Request) -> Any:
    return await _forward_request(request, "cart", "/api/v1/cart")


@router.api_route("/orders/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def orders_proxy(request: Request, path: str) -> Any:
    return await _forward_request(request, "orders", _service_path("/api/v1/orders", path))


@router.api_route("/orders", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def orders_root_proxy(request: Request) -> Any:
    return await _forward_request(request, "orders", "/api/v1/orders")


@router.api_route("/deliveries/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def deliveries_proxy(request: Request, path: str) -> Any:
    return await _forward_request(request, "deliveries", _service_path("/api/v1/deliveries", path))


@router.api_route("/deliveries", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def deliveries_root_proxy(request: Request) -> Any:
    return await _forward_request(request, "deliveries", "/api/v1/deliveries")


@router.api_route("/notifications", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def notifications_root_proxy(request: Request) -> Any:
    return await _forward_request(request, "notifications", "/api/v1/notifications")


@router.api_route("/notifications/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def notifications_proxy(request: Request, path: str) -> Any:
    return await _forward_request(request, "notifications", _service_path("/api/v1/notifications", path))


@router.api_route("/ai/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def ai_proxy(request: Request, path: str) -> Any:
    return await _forward_request(request, "ai", _service_path("/api/v1/ai", path))


@router.api_route("/ai", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def ai_root_proxy(request: Request) -> Any:
    return await _forward_request(request, "ai", "/api/v1/ai")
