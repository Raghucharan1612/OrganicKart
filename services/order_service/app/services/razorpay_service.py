from typing import Any
import logging
from time import perf_counter

import razorpay
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)

class RazorpayService:
    def __init__(self) -> None:
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Razorpay credentials are not configured")
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    @property
    def key_id(self) -> str:
        return settings.RAZORPAY_KEY_ID or ""

    def create_order(self, amount_paise: int, currency: str, receipt: str) -> dict[str, Any]:
        started_at = perf_counter()
        try:
            return self.client.order.create({"amount": amount_paise, "currency": currency, "receipt": receipt})
        except Exception as exc:
            logger.warning(
                "CHECKOUT_TRACE action=razorpay_order_create_error exception=%s repr=%r elapsed_ms=%.1f",
                type(exc).__name__,
                exc,
                (perf_counter() - started_at) * 1000,
            )
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Unable to create Razorpay order") from exc

    def verify_payment_signature(self, order_id: str, payment_id: str, signature: str) -> None:
        try:
            self.client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            })
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Razorpay payment signature") from exc

    def fetch_payment(self, payment_id: str) -> dict[str, Any]:
        try:
            return self.client.payment.fetch(payment_id)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Unable to verify Razorpay payment") from exc

    @staticmethod
    def verify_webhook_signature(body: bytes, signature: str | None) -> None:
        if not settings.RAZORPAY_WEBHOOK_SECRET:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Razorpay webhook secret is not configured")
        if not signature:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Razorpay webhook signature")
        try:
            razorpay.utility.Utility().verify_webhook_signature(body.decode("utf-8"), signature, settings.RAZORPAY_WEBHOOK_SECRET)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Razorpay webhook signature") from exc
