import json
import logging
from time import perf_counter

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.session import get_db
from app.schemas.order import (
    CheckoutInitiate,
    CheckoutInitiateResponse,
    AdminBusinessInsightsResponse,
    AdminOrderAnalyticsResponse,
    OrderCreate,
    OrderItemResponse,
    OrderResponse,
    PaymentStatusResponse,
    PaymentVerificationResponse,
    RazorpayPaymentVerify,
    SellerAnalyticsResponse,
)
from app.services.order_service import OrderService
from app.services.razorpay_service import RazorpayService

router = APIRouter(prefix="/orders", tags=["orders"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if payload.get("role", "CUSTOMER") != "CUSTOMER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can access order operations.",
        )
    return int(payload["sub"])


def get_current_seller_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    role = payload.get("role")
    if role not in {"VENDOR", "FARMER"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors and farmers can access seller order operations.",
        )
    return int(payload["sub"])


def get_current_admin_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if payload.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access order analytics.",
        )
    return int(payload["sub"])


@router.get("/seller", response_model=list[OrderResponse])
def list_seller_orders(
    db: Session = Depends(get_db),
    seller_id: int = Depends(get_current_seller_id),
):
    orders = OrderService(db).list_seller_orders(seller_id)
    results = []
    for order in orders:
        results.append(
            OrderResponse(
                id=order.id,
                user_id=order.user_id,
                status=order.status,
                payment_status=order.payment_status,
                subtotal=order.subtotal,
                delivery_fee=order.delivery_fee,
                total_amount=order.total_amount,
                shipping_address=order.shipping_address,
                created_at=order.created_at,
                updated_at=order.updated_at,
                items=[
                    OrderItemResponse(
                        id=item.id,
                        order_id=item.order_id,
                        product_id=item.product_id,
                        seller_id=item.seller_id,
                        product_name=item.product_name,
                        unit_price=item.unit_price,
                        quantity=item.quantity,
                        subtotal=item.subtotal,
                        created_at=item.created_at,
                    )
                    for item in order.items
                    if item.seller_id == seller_id
                ],
            )
        )
    return results


@router.get("/seller/analytics", response_model=SellerAnalyticsResponse)
def get_seller_analytics(
    db: Session = Depends(get_db),
    seller_id: int = Depends(get_current_seller_id),
):
    return OrderService(db).get_seller_analytics(seller_id)


@router.get("/admin/analytics", response_model=AdminOrderAnalyticsResponse)
def get_admin_analytics(
    db: Session = Depends(get_db),
    _: int = Depends(get_current_admin_id),
):
    return OrderService(db).get_admin_analytics()


@router.get("/admin/business-insights", response_model=AdminBusinessInsightsResponse)
def get_admin_business_insights(
    db: Session = Depends(get_db),
    _: int = Depends(get_current_admin_id),
):
    return OrderService(db).get_admin_business_insights()


@router.get("", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    orders = OrderService(db).list_orders(user_id)
    results = []
    for order in orders:
        results.append(
            OrderResponse(
                id=order.id,
                user_id=order.user_id,
                status=order.status,
                payment_status=order.payment_status,
                subtotal=order.subtotal,
                delivery_fee=order.delivery_fee,
                total_amount=order.total_amount,
                shipping_address=order.shipping_address,
                created_at=order.created_at,
                updated_at=order.updated_at,
                items=[
                    OrderItemResponse(
                        id=item.id,
                        order_id=item.order_id,
                        product_id=item.product_id,
                        product_name=item.product_name,
                        unit_price=item.unit_price,
                        quantity=item.quantity,
                        subtotal=item.subtotal,
                        created_at=item.created_at,
                    )
                    for item in order.items
                ],
            )
        )
    return results


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    order = OrderService(db).get_order(user_id, order_id)
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        payment_status=order.payment_status,
        subtotal=order.subtotal,
        delivery_fee=order.delivery_fee,
        total_amount=order.total_amount,
        shipping_address=order.shipping_address,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[
            OrderItemResponse(
                id=item.id,
                order_id=item.order_id,
                product_id=item.product_id,
                product_name=item.product_name,
                unit_price=item.unit_price,
                quantity=item.quantity,
                subtotal=item.subtotal,
                created_at=item.created_at,
            )
            for item in order.items
        ],
    )


@router.post("", status_code=status.HTTP_409_CONFLICT)
def create_order(payload: OrderCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    return OrderService(db).create_order(user_id, payload.shipping_address)


@router.post("/checkout/initiate", response_model=CheckoutInitiateResponse, status_code=status.HTTP_201_CREATED)
def initiate_checkout(
    payload: CheckoutInitiate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    started_at = perf_counter()
    user_id: int | None = None
    logger.warning("CHECKOUT_TRACE step=1 action=endpoint_enter")
    try:
        user_id = get_current_user_id(credentials)
        logger.warning("CHECKOUT_TRACE step=2 user_id=%s action=identity_validated", user_id)
        order, payment = OrderService(db).initiate_checkout(user_id, payload.address_id, credentials.credentials, idempotency_key)
        logger.warning("CHECKOUT_TRACE step=13 user_id=%s order_id=%s action=response_return", user_id, order.id)
        return CheckoutInitiateResponse(
            order_id=order.id,
            payment_attempt_id=payment.id,
            amount_paise=payment.amount_paise,
            currency=payment.currency,
            payment_status=payment.status,
            razorpay_key_id=RazorpayService().key_id,
            razorpay_order_id=payment.provider_order_id or "",
        )
    finally:
        logger.warning(
            "CHECKOUT_TRACE action=checkout_complete user_id=%s elapsed_ms=%.1f",
            user_id,
            (perf_counter() - started_at) * 1000,
        )


@router.post("/payments/verify", response_model=PaymentVerificationResponse)
def verify_payment(
    payload: RazorpayPaymentVerify,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    order, payment = OrderService(db).verify_razorpay_payment(
        user_id,
        payload.order_id,
        payload.razorpay_order_id,
        payload.razorpay_payment_id,
        payload.razorpay_signature,
    )
    return PaymentVerificationResponse(
        order_id=order.id,
        payment_attempt_id=payment.id,
        payment_status=payment.status,
        order_status=order.status,
    )


@router.post("/payments/webhook")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db),
    signature: str | None = Header(default=None, alias="X-Razorpay-Signature"),
):
    body = await request.body()
    RazorpayService.verify_webhook_signature(body, signature)
    try:
        event = json.loads(body)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Razorpay webhook payload") from exc
    if event.get("event") not in {"payment.captured", "order.paid"}:
        return {"status": "ignored"}
    payment_entity = event.get("payload", {}).get("payment", {}).get("entity", {})
    razorpay_order_id = payment_entity.get("order_id")
    razorpay_payment_id = payment_entity.get("id")
    if not razorpay_order_id or not razorpay_payment_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Razorpay webhook is missing payment identifiers")
    order, payment = OrderService(db).confirm_razorpay_webhook_payment(razorpay_order_id, razorpay_payment_id)
    return {"order_id": order.id, "payment_attempt_id": payment.id, "payment_status": payment.status}


@router.get("/{order_id}/payment-status", response_model=PaymentStatusResponse)
def get_payment_status(order_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    order, payment = OrderService(db).get_payment_status(user_id, order_id)
    return PaymentStatusResponse(
        order_id=order.id,
        payment_attempt_id=payment.id,
        provider=payment.provider,
        status=payment.status,
        amount_paise=payment.amount_paise,
        currency=payment.currency,
        order_status=order.status,
        confirmed_at=order.confirmed_at,
    )


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    order = OrderService(db).cancel_order(user_id, order_id)
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        payment_status=order.payment_status,
        subtotal=order.subtotal,
        delivery_fee=order.delivery_fee,
        total_amount=order.total_amount,
        shipping_address=order.shipping_address,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[
            OrderItemResponse(
                id=item.id,
                order_id=item.order_id,
                product_id=item.product_id,
                product_name=item.product_name,
                unit_price=item.unit_price,
                quantity=item.quantity,
                subtotal=item.subtotal,
                created_at=item.created_at,
            )
            for item in order.items
        ],
    )
