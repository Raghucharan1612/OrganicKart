from datetime import UTC, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import logging
from time import perf_counter
from typing import Any
from uuid import uuid4

import httpx
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.payment import PaymentAttempt, PaymentStatus
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.order import (
    AdminMonthlySalesSummary,
    AdminBusinessInsightsResponse,
    AdminOrderAnalyticsResponse,
    AdminProductSalesInsight,
    AdminRecentOrderSummary,
    AdminSalesDeclineInsight,
    AdminVendorSalesInsight,
    MonthlySalesSummary,
    RecentOrderSummary,
    SellerAnalyticsResponse,
)
from app.services.razorpay_service import RazorpayService

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.cart_repo = CartRepository(db)
        self.order_repo = OrderRepository(db)

    def list_orders(self, user_id: int) -> list[Order]:
        return self.order_repo.get_by_user(user_id)

    def list_seller_orders(self, seller_id: int) -> list[Order]:
        return self.order_repo.get_by_seller(seller_id)

    def get_seller_analytics(self, seller_id: int) -> SellerAnalyticsResponse:
        orders = self.order_repo.get_by_seller(seller_id)
        total_orders = 0
        total_revenue = Decimal("0.00")
        monthly_stats: dict[str, dict[str, Any]] = {}
        recent_orders: list[RecentOrderSummary] = []

        for order in orders:
            seller_items = [item for item in order.items if item.seller_id == seller_id]
            if not seller_items:
                continue

            seller_subtotal = sum((item.subtotal for item in seller_items), Decimal("0.00"))

            if order.status != "CANCELLED":
                total_orders += 1
                total_revenue += seller_subtotal

                month_key = order.created_at.strftime("%Y-%m") if order.created_at else datetime.now(UTC).strftime("%Y-%m")
                if month_key not in monthly_stats:
                    monthly_stats[month_key] = {"orders": 0, "revenue": Decimal("0.00")}
                monthly_stats[month_key]["orders"] += 1
                monthly_stats[month_key]["revenue"] += seller_subtotal

            recent_orders.append(
                RecentOrderSummary(
                    order_id=order.id,
                    created_at=order.created_at,
                    status=order.status,
                    payment_status=order.payment_status,
                    items_count=len(seller_items),
                    seller_revenue=seller_subtotal,
                )
            )

        monthly_sales_summary = [
            MonthlySalesSummary(
                month=month,
                orders=data["orders"],
                revenue=data["revenue"],
            )
            for month, data in monthly_stats.items()
        ]
        monthly_orders = {month: data["orders"] for month, data in monthly_stats.items()}
        monthly_revenue = {month: data["revenue"] for month, data in monthly_stats.items()}

        return SellerAnalyticsResponse(
            total_orders=total_orders,
            total_revenue=total_revenue,
            monthly_sales_summary=monthly_sales_summary,
            monthly_orders=monthly_orders,
            monthly_revenue=monthly_revenue,
            recent_order_summary=recent_orders[:10],
            recent_orders_summary=recent_orders[:10],
        )

    def get_admin_analytics(self) -> AdminOrderAnalyticsResponse:
        """Aggregate whole-order analytics for ADMIN without exposing customer PII."""
        orders = self.order_repo.get_all()
        orders_by_status: dict[str, int] = {}
        payment_status_breakdown: dict[str, int] = {}
        monthly_stats: dict[str, dict[str, Any]] = {}
        recent_orders: list[AdminRecentOrderSummary] = []
        total_revenue = Decimal("0.00")

        for order in orders:
            orders_by_status[order.status] = orders_by_status.get(order.status, 0) + 1
            payment_status_breakdown[order.payment_status] = payment_status_breakdown.get(order.payment_status, 0) + 1
            recent_orders.append(
                AdminRecentOrderSummary(
                    order_id=order.id,
                    created_at=order.created_at,
                    status=order.status,
                    payment_status=order.payment_status,
                    items_count=len(order.items),
                    total_amount=order.total_amount,
                )
            )

            # Whole-order revenue is authoritative only after payment and is
            # excluded when the existing cancellation policy marks it cancelled.
            if order.payment_status == PaymentStatus.PAID.value and order.status != "CANCELLED":
                total_revenue += order.total_amount
                month_key = order.created_at.strftime("%Y-%m") if order.created_at else datetime.now(UTC).strftime("%Y-%m")
                if month_key not in monthly_stats:
                    monthly_stats[month_key] = {"orders": 0, "revenue": Decimal("0.00")}
                monthly_stats[month_key]["orders"] += 1
                monthly_stats[month_key]["revenue"] += order.total_amount

        return AdminOrderAnalyticsResponse(
            total_orders=len(orders),
            orders_by_status=orders_by_status,
            payment_status_breakdown=payment_status_breakdown,
            cancelled_orders=orders_by_status.get("CANCELLED", 0),
            total_revenue=total_revenue,
            monthly_sales_summary=[
                AdminMonthlySalesSummary(month=month, orders=data["orders"], revenue=data["revenue"])
                for month, data in sorted(monthly_stats.items(), reverse=True)
            ],
            recent_orders=recent_orders[:10],
        )

    def get_admin_business_insights(self) -> AdminBusinessInsightsResponse:
        """Read-only, paid non-cancelled order-item aggregates for ADMIN."""
        now = datetime.now(UTC)
        current_period = now.strftime("%Y-%m")
        previous_period_date = (now.replace(day=1) - timedelta(days=1))
        previous_period = previous_period_date.strftime("%Y-%m")
        vendor_stats: dict[int, dict[str, Any]] = {}
        product_stats: dict[int, dict[str, Any]] = {}
        current_quantities: dict[int, int] = {}
        previous_quantities: dict[int, int] = {}
        product_names: dict[int, str] = {}
        has_current_period_sales = False
        has_previous_period_sales = False

        for order in self.order_repo.get_all():
            if order.payment_status != PaymentStatus.PAID.value or order.status == "CANCELLED":
                continue
            order_period = order.created_at.strftime("%Y-%m") if order.created_at else None
            for item in order.items:
                if item.product_id is None:
                    continue
                product_names.setdefault(item.product_id, item.product_name)
                product = product_stats.setdefault(
                    item.product_id,
                    {"name": item.product_name, "units_sold": 0, "revenue": Decimal("0.00")},
                )
                product["units_sold"] += item.quantity
                product["revenue"] += item.subtotal

                if item.seller_id is not None:
                    vendor = vendor_stats.setdefault(
                        item.seller_id,
                        {"order_ids": set(), "units_sold": 0, "revenue": Decimal("0.00")},
                    )
                    vendor["order_ids"].add(order.id)
                    vendor["units_sold"] += item.quantity
                    vendor["revenue"] += item.subtotal

                if order_period == current_period:
                    has_current_period_sales = True
                    current_quantities[item.product_id] = current_quantities.get(item.product_id, 0) + item.quantity
                elif order_period == previous_period:
                    has_previous_period_sales = True
                    previous_quantities[item.product_id] = previous_quantities.get(item.product_id, 0) + item.quantity

        vendor_sales = sorted(
            (
                AdminVendorSalesInsight(
                    seller_id=seller_id,
                    orders_count=len(data["order_ids"]),
                    units_sold=data["units_sold"],
                    revenue=data["revenue"],
                )
                for seller_id, data in vendor_stats.items()
            ),
            key=lambda entry: (-entry.revenue, entry.seller_id),
        )[:10]
        product_sales = sorted(
            (
                AdminProductSalesInsight(
                    product_id=product_id,
                    product_name=data["name"],
                    units_sold=data["units_sold"],
                    revenue=data["revenue"],
                )
                for product_id, data in product_stats.items()
            ),
            key=lambda entry: (-entry.units_sold, -entry.revenue, entry.product_id),
        )[:10]

        sales_decline_available = has_current_period_sales and has_previous_period_sales
        sales_declines: list[AdminSalesDeclineInsight] = []
        if sales_decline_available:
            for product_id, previous_quantity in previous_quantities.items():
                current_quantity = current_quantities.get(product_id, 0)
                if current_quantity >= previous_quantity:
                    continue
                percentage_change = (
                    (Decimal(current_quantity - previous_quantity) / Decimal(previous_quantity)) * Decimal("100")
                ).quantize(Decimal("0.01"))
                sales_declines.append(
                    AdminSalesDeclineInsight(
                        product_id=product_id,
                        product_name=product_names.get(product_id, "Unknown product"),
                        current_period_quantity=current_quantity,
                        previous_period_quantity=previous_quantity,
                        percentage_change=percentage_change,
                    )
                )
            sales_declines.sort(key=lambda entry: (entry.percentage_change, entry.product_id))

        return AdminBusinessInsightsResponse(
            vendor_sales=vendor_sales,
            product_sales=product_sales,
            current_period=current_period,
            previous_period=previous_period,
            sales_decline_available=sales_decline_available,
            sales_declines=sales_declines[:10],
        )


    def get_order(self, user_id: int, order_id: int) -> Order:
        order = self.order_repo.get_by_id(order_id)
        if order is None or order.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return order

    def initiate_checkout(self, user_id: int, address_id: int, access_token: str, idempotency_key: str | None = None) -> tuple[Order, PaymentAttempt]:
        RazorpayService()
        if idempotency_key:
            existing = self.db.query(PaymentAttempt).filter(
                PaymentAttempt.user_id == user_id,
                PaymentAttempt.idempotency_key == idempotency_key,
            ).first()
            if existing:
                order = self.get_order(user_id, existing.order_id)
                if existing.status != PaymentStatus.PAYMENT_PENDING.value:
                    return order, existing
                return order, self._ensure_razorpay_order(order, existing)
        logger.warning("CHECKOUT_TRACE step=3 user_id=%s action=cart_load_start", user_id)
        cart = self.cart_repo.get_by_user(user_id)
        if cart is None or not cart.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")
        logger.warning("CHECKOUT_TRACE step=4 user_id=%s action=cart_load_complete item_count=%s", user_id, len(cart.items))

        logger.warning("CHECKOUT_TRACE step=5 user_id=%s action=user_service_start", user_id)
        address = self._get_customer_address(user_id, address_id, access_token)
        logger.warning("CHECKOUT_TRACE step=6 user_id=%s action=user_service_complete", user_id)
        snapshots: list[dict[str, Any]] = []
        subtotal = Decimal("0.00")
        for item in cart.items:
            logger.warning("CHECKOUT_TRACE step=7 user_id=%s product_id=%s action=product_service_start", user_id, item.product_id)
            product = self._validate_product(item.product_id)
            logger.warning("CHECKOUT_TRACE step=8 user_id=%s product_id=%s action=product_service_complete", user_id, item.product_id)
            if item.quantity > int(product.get("stock_quantity", 0)):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Requested quantity exceeds stock for product {item.product_id}")
            unit_price = Decimal(str(product.get("price", "0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            item_subtotal = unit_price * item.quantity
            subtotal += item_subtotal
            snapshots.append({
                "product_id": item.product_id,
                "seller_id": product.get("seller_id"),
                "product_name": product.get("name") or item.product_name,
                "unit_price": unit_price,
                "quantity": item.quantity,
                "subtotal": item_subtotal,
                "image_url": product.get("image_url") or item.image_url,
                "unit": product.get("unit") or item.unit,
            })

        delivery_fee = Decimal("0.00")
        total_amount = subtotal + delivery_fee
        amount_paise = int((total_amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        logger.warning("CHECKOUT_TRACE step=9 user_id=%s action=local_payment_pending_create_start", user_id)
        order = Order(
            user_id=user_id,
            status="PAYMENT_PENDING",
            payment_status=PaymentStatus.PAYMENT_PENDING.value,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total_amount=total_amount,
            shipping_address=self._format_address(address),
        )
        self.db.add(order)
        self.db.flush()
        for snapshot in snapshots:
            self.db.add(OrderItem(order_id=order.id, **snapshot))

        payment = PaymentAttempt(
            order_id=order.id,
            user_id=user_id,
            provider="RAZORPAY",
            status=PaymentStatus.PAYMENT_PENDING.value,
            amount_paise=amount_paise,
            currency="INR",
            idempotency_key=idempotency_key or uuid4().hex,
        )
        self.db.add(payment)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            if idempotency_key:
                existing = self.db.query(PaymentAttempt).filter(
                    PaymentAttempt.user_id == user_id,
                    PaymentAttempt.idempotency_key == idempotency_key,
                ).first()
                if existing:
                    return self.get_order(user_id, existing.order_id), self._ensure_razorpay_order(self.get_order(user_id, existing.order_id), existing)
            raise
        self.db.refresh(order)
        self.db.refresh(payment)
        logger.warning("CHECKOUT_TRACE step=10 user_id=%s order_id=%s payment_attempt_id=%s action=local_payment_pending_create_complete", user_id, order.id, payment.id)
        return order, self._ensure_razorpay_order(order, payment)

    def verify_razorpay_payment(self, user_id: int, order_id: int, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> tuple[Order, PaymentAttempt]:
        order, payment = self.get_payment_status(user_id, order_id)
        self._assert_provider_order(payment, razorpay_order_id)
        self._assert_provider_payment_available(payment, razorpay_payment_id)
        if payment.status == PaymentStatus.PAID.value:
            if payment.provider_payment_id != razorpay_payment_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Razorpay payment does not match the confirmed order")
            return order, payment
        razorpay = RazorpayService()
        razorpay.verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature)
        self._validate_provider_payment(razorpay.fetch_payment(razorpay_payment_id), payment, razorpay_order_id)
        self._record_provider_payment(payment, razorpay_payment_id, razorpay_signature)
        return self.confirm_payment(payment.id, user_id, payment.amount_paise)

    def confirm_razorpay_webhook_payment(self, razorpay_order_id: str, razorpay_payment_id: str) -> tuple[Order, PaymentAttempt]:
        payment = self.db.query(PaymentAttempt).filter(PaymentAttempt.provider_order_id == razorpay_order_id).first()
        if payment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment attempt not found")
        if payment.status == PaymentStatus.PAID.value:
            if payment.provider_payment_id and payment.provider_payment_id != razorpay_payment_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Razorpay payment does not match the confirmed order")
            return self.get_order(payment.user_id, payment.order_id), payment
        self._validate_provider_payment(RazorpayService().fetch_payment(razorpay_payment_id), payment, razorpay_order_id)
        self._record_provider_payment(payment, razorpay_payment_id, None)
        return self.confirm_payment(payment.id, payment.user_id, payment.amount_paise)

    def get_payment_status(self, user_id: int, order_id: int) -> tuple[Order, PaymentAttempt]:
        order = self.get_order(user_id, order_id)
        payment = self.db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).order_by(PaymentAttempt.created_at.desc()).first()
        if payment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment attempt not found")
        return order, payment

    def confirm_payment(self, payment_attempt_id: int, user_id: int, amount_paise: int) -> tuple[Order, PaymentAttempt]:
        """Confirm a verified provider payment. Razorpay verification/webhooks call this in Phase 4."""
        payment = self.db.query(PaymentAttempt).filter(PaymentAttempt.id == payment_attempt_id).with_for_update().first()
        if payment is None or payment.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment attempt not found")
        if payment.amount_paise != amount_paise:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment amount does not match the order")
        if payment.status == PaymentStatus.FAILED.value:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Payment attempt has failed")

        order = self.db.query(Order).filter(Order.id == payment.order_id).with_for_update().first()
        if order is None or order.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        if payment.status == PaymentStatus.PAID.value:
            return order, payment
        if order.payment_status != PaymentStatus.PAYMENT_PENDING.value:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order is not awaiting payment")

        now = datetime.now(UTC).replace(tzinfo=None)
        payment.status = PaymentStatus.PAID.value
        payment.verified_at = now
        order.payment_status = PaymentStatus.PAID.value
        order.status = "CONFIRMED"
        order.confirmed_at = now
        cart = self.cart_repo.get_by_user(user_id)
        if cart is not None:
            self.db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        self.db.commit()
        self.db.refresh(order)
        self.db.refresh(payment)

        self._trigger_fulfilment(order)
        return order, payment

    def mark_payment_failed(self, payment_attempt_id: int, user_id: int, reason: str) -> PaymentAttempt:
        payment = self.db.query(PaymentAttempt).filter(PaymentAttempt.id == payment_attempt_id).with_for_update().first()
        if payment is None or payment.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment attempt not found")
        if payment.status == PaymentStatus.PAID.value:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Payment attempt is already paid")
        if payment.status != PaymentStatus.FAILED.value:
            payment.status = PaymentStatus.FAILED.value
            payment.failure_reason = reason
            self.db.commit()
            self.db.refresh(payment)
        return payment

    def _ensure_razorpay_order(self, order: Order, payment: PaymentAttempt) -> PaymentAttempt:
        if payment.provider_order_id:
            return payment
        started_at = perf_counter()
        logger.warning("CHECKOUT_TRACE step=11 user_id=%s order_id=%s payment_attempt_id=%s action=razorpay_order_create_start", payment.user_id, order.id, payment.id)
        provider_order = RazorpayService().create_order(
            payment.amount_paise,
            payment.currency,
            f"ok-{order.id}-{payment.id}",
        )
        provider_order_id = provider_order.get("id")
        if not provider_order_id:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Razorpay did not return an order ID")
        payment.provider_order_id = str(provider_order_id)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Razorpay order is already associated with another payment") from exc
        self.db.refresh(payment)
        logger.warning(
            "CHECKOUT_TRACE step=12 user_id=%s order_id=%s payment_attempt_id=%s action=razorpay_order_create_complete elapsed_ms=%.1f",
            payment.user_id,
            order.id,
            payment.id,
            (perf_counter() - started_at) * 1000,
        )
        return payment

    @staticmethod
    def _assert_provider_order(payment: PaymentAttempt, razorpay_order_id: str) -> None:
        if payment.provider != "RAZORPAY" or payment.provider_order_id != razorpay_order_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Razorpay order does not match the payment attempt")

    @staticmethod
    def _validate_provider_payment(provider_payment: dict[str, Any], payment: PaymentAttempt, razorpay_order_id: str) -> None:
        if provider_payment.get("order_id") != razorpay_order_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Razorpay payment order does not match")
        if int(provider_payment.get("amount", -1)) != payment.amount_paise:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Razorpay payment amount does not match")
        if provider_payment.get("currency") != payment.currency or provider_payment.get("status") != "captured":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Razorpay payment is not captured")

    def _record_provider_payment(self, payment: PaymentAttempt, provider_payment_id: str, signature: str | None) -> None:
        self._assert_provider_payment_available(payment, provider_payment_id)
        if payment.provider_payment_id and payment.provider_payment_id != provider_payment_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Payment attempt already has a different Razorpay payment")
        payment.provider_payment_id = provider_payment_id
        if signature:
            payment.signature = signature
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            self._assert_provider_payment_available(payment, provider_payment_id)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Razorpay payment is already associated with another order") from exc
        self.db.refresh(payment)

    def _assert_provider_payment_available(self, payment: PaymentAttempt, provider_payment_id: str) -> None:
        other = self.db.query(PaymentAttempt).filter(
            PaymentAttempt.provider_payment_id == provider_payment_id,
            PaymentAttempt.id != payment.id,
        ).first()
        if other:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Razorpay payment is already associated with another order")

    def create_order(self, user_id: int, shipping_address: str | None = None) -> Order:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Use /api/v1/orders/checkout/initiate to create a payment-pending order.",
        )

    def _get_customer_address(self, user_id: int, address_id: int, access_token: str) -> dict[str, Any]:
        started_at = perf_counter()
        try:
            response = httpx.get(
                f"{settings.USER_SERVICE_URL}/api/v1/users/me/addresses",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
        except httpx.HTTPError as exc:
            logger.warning(
                "CHECKOUT_TRACE user_id=%s action=user_service_error exception=%s repr=%r elapsed_ms=%.1f",
                user_id,
                type(exc).__name__,
                exc,
                (perf_counter() - started_at) * 1000,
            )
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Address service unavailable") from exc
        logger.warning("CHECKOUT_TRACE user_id=%s action=user_service_http_complete status=%s elapsed_ms=%.1f", user_id, response.status_code, (perf_counter() - started_at) * 1000)
        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to validate delivery address")
        address = next((item for item in response.json() if int(item.get("id", 0)) == address_id), None)
        if address is None or int(address.get("user_id", 0)) != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
        return address

    @staticmethod
    def _format_address(address: dict[str, Any]) -> str:
        return ", ".join(str(value).strip() for value in (
            address.get("recipient_name"), address.get("phone"), address.get("address_line1"),
            address.get("address_line2"), address.get("city"), address.get("state"),
            address.get("postal_code"), address.get("country"),
        ) if value)

    def _trigger_fulfilment(self, order: Order) -> None:
        try:
            httpx.post(
                f"{settings.DELIVERY_SERVICE_URL}/api/v1/deliveries/internal/assign",
                json={"order_id": order.id, "user_id": order.user_id, "shipping_address": order.shipping_address},
                headers={"X-Internal-Service-Key": settings.INTERNAL_SERVICE_KEY},
                timeout=5.0,
            ).raise_for_status()
        except httpx.HTTPError:
            pass
        try:
            httpx.post(
                f"{settings.NOTIFICATION_SERVICE_URL}/api/v1/notifications",
                json={
                    "user_id": order.user_id,
                    "type": "ORDER_CONFIRMED",
                    "title": f"Order #{order.id} confirmed",
                    "message": "Your payment was received and your order is confirmed.",
                    "channel": "IN_APP",
                    "reference_type": "ORDER",
                    "reference_id": order.id,
                },
                headers={"X-Internal-Service-Key": settings.INTERNAL_SERVICE_KEY},
                timeout=settings.NOTIFICATION_REQUEST_TIMEOUT,
            )
        except httpx.HTTPError:
            pass

    def _validate_product(self, product_id: int) -> dict[str, Any]:
        started_at = perf_counter()
        try:
            response = httpx.get(f"{settings.PRODUCT_SERVICE_URL}/api/v1/products/{product_id}", timeout=10)
        except httpx.HTTPError as exc:
            logger.warning(
                "CHECKOUT_TRACE product_id=%s action=product_service_error exception=%s repr=%r elapsed_ms=%.1f",
                product_id,
                type(exc).__name__,
                exc,
                (perf_counter() - started_at) * 1000,
            )
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Product catalog unavailable") from exc
        logger.warning("CHECKOUT_TRACE product_id=%s action=product_service_http_complete status=%s elapsed_ms=%.1f", product_id, response.status_code, (perf_counter() - started_at) * 1000)
        if response.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid product reference")
        product = response.json()
        if product.get("is_active") is not True:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is unavailable for purchase")
        if product.get("certification") != "APPROVED":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product certification must be APPROVED before purchase")
        if int(product.get("stock_quantity", 0)) <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is out of stock")
        return product

    def cancel_order(self, user_id: int, order_id: int) -> Order:
        order = self.get_order(user_id, order_id)
        if order.status == "CANCELLED":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order already cancelled")
        if order.status in {"DELIVERED", "SHIPPED"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order status transition")
        return self.order_repo.cancel(order)
