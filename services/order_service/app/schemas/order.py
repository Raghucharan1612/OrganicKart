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
    seller_id: int | None = None
    product_name: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MonthlySalesSummary(BaseModel):
    month: str
    orders: int
    revenue: Decimal


class RecentOrderSummary(BaseModel):
    order_id: int
    created_at: datetime
    status: str
    payment_status: str
    items_count: int
    seller_revenue: Decimal


class SellerAnalyticsResponse(BaseModel):
    total_orders: int
    total_revenue: Decimal
    monthly_sales_summary: list[MonthlySalesSummary] = []
    monthly_orders: dict[str, int] = {}
    monthly_revenue: dict[str, Decimal] = {}
    recent_order_summary: list[RecentOrderSummary] = []
    recent_orders_summary: list[RecentOrderSummary] = []


class AdminRecentOrderSummary(BaseModel):
    order_id: int
    created_at: datetime
    status: str
    payment_status: str
    items_count: int
    total_amount: Decimal


class AdminMonthlySalesSummary(BaseModel):
    month: str
    orders: int
    revenue: Decimal


class AdminOrderAnalyticsResponse(BaseModel):
    total_orders: int
    orders_by_status: dict[str, int] = Field(default_factory=dict)
    payment_status_breakdown: dict[str, int] = Field(default_factory=dict)
    cancelled_orders: int
    total_revenue: Decimal
    monthly_sales_summary: list[AdminMonthlySalesSummary] = Field(default_factory=list)
    recent_orders: list[AdminRecentOrderSummary] = Field(default_factory=list)


class AdminVendorSalesInsight(BaseModel):
    seller_id: int
    orders_count: int
    units_sold: int
    revenue: Decimal


class AdminProductSalesInsight(BaseModel):
    product_id: int
    product_name: str
    units_sold: int
    revenue: Decimal


class AdminSalesDeclineInsight(BaseModel):
    product_id: int
    product_name: str
    current_period_quantity: int
    previous_period_quantity: int
    percentage_change: Decimal


class AdminBusinessInsightsResponse(BaseModel):
    vendor_sales: list[AdminVendorSalesInsight] = Field(default_factory=list)
    product_sales: list[AdminProductSalesInsight] = Field(default_factory=list)
    current_period: str
    previous_period: str
    sales_decline_available: bool
    sales_declines: list[AdminSalesDeclineInsight] = Field(default_factory=list)



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
