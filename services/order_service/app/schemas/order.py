from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class OrderItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    product_name: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    shipping_address: str | None = None


class CheckoutInitiate(BaseModel):
    address_id: int = Field(..., gt=0)


class CheckoutInitiateResponse(BaseModel):
    order_id: int
    payment_attempt_id: int
    amount_paise: int
    currency: str
    payment_status: str
    razorpay_key_id: str
    razorpay_order_id: str


class RazorpayPaymentVerify(BaseModel):
    order_id: int = Field(..., gt=0)
    razorpay_order_id: str = Field(..., min_length=1, max_length=128)
    razorpay_payment_id: str = Field(..., min_length=1, max_length=128)
    razorpay_signature: str = Field(..., min_length=1, max_length=512)


class PaymentVerificationResponse(BaseModel):
    order_id: int
    payment_attempt_id: int
    payment_status: str
    order_status: str


class PaymentStatusResponse(BaseModel):
    order_id: int
    payment_attempt_id: int
    provider: str
    status: str
    amount_paise: int
    currency: str
    order_status: str
    confirmed_at: datetime | None = None


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    payment_status: str
    subtotal: Decimal
    delivery_fee: Decimal
    total_amount: Decimal
    shipping_address: str | None = None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)
