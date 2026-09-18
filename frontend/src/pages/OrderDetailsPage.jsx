import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import orderService from "@/services/orderService";
import deliveryService from "@/services/deliveryService";
import Spinner from "@/components/Spinner";
import StatusBadge from "@/components/StatusBadge";
import { getApiErrorMessage } from "@/utils/errorUtils";

export default function OrderDetailsPage() {
  const { id } = useParams();
  const location = useLocation();
  const [order, setOrder] = useState(null);
  const [delivery, setDelivery] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [isCancelling, setIsCancelling] = useState(false);

  const loadOrder = async () => {
    setIsLoading(true);
    setError("");

    try {
      const data = await orderService.getOrder(id);
      setOrder(data);

      try {
        const deliveries = await deliveryService.listDeliveries();
        const activeDelivery = Array.isArray(deliveries)
          ? deliveries.find((entry) => Number(entry.order_id) === Number(id)) || null
          : null;
        setDelivery(activeDelivery);
      } catch {
        setDelivery(null);
      }
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to load this order."));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadOrder();
  }, [id]);

  const handleCancel = async () => {
    setIsCancelling(true);
    try {
      await orderService.cancelOrder(id);
      await loadOrder();
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to cancel this order."));
    } finally {
      setIsCancelling(false);
    }
  };

  if (isLoading) return <Spinner label="Loading order…" />;

  if (error || !order) {
    return (
      <div className="card mx-auto max-w-lg text-center">
        <h1 className="font-display text-xl font-bold text-primary-900">Order not found</h1>
        <p className="mt-2 text-sm text-gray-500">{error || "The order you requested is unavailable."}</p>
        <Link to="/orders" className="btn-primary mt-4 inline-flex">
          Back to orders
        </Link>
      </div>
    );
  }

  const items = Array.isArray(order.items) ? order.items : [];
  const calculatedSubtotal = items.reduce((sum, item) => sum + Number(item.unit_price || 0) * Number(item.quantity || 0), 0);
  const subtotal = Number(order.subtotal ?? calculatedSubtotal);
  const deliveryFee = Number(order.delivery_fee ?? 0);
  const total = Number(order.total_amount ?? subtotal + deliveryFee);
  const orderDate = order.created_at ? new Date(order.created_at).toLocaleString() : "Date unavailable";

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      {location.state?.paymentConfirmed && order.payment_status === "PAID" && (
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-medium text-emerald-800">
          Payment verified successfully. Your order is confirmed.
        </div>
      )}
      <div className="card">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.2em] text-primary-600">Order</p>
            <h1 className="font-display text-2xl font-bold text-primary-900">#{order.id}</h1>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <StatusBadge status={order.status} />
            {order.status !== "CANCELLED" && order.status !== "DELIVERED" && (
              <button type="button" onClick={handleCancel} disabled={isCancelling} className="btn-secondary disabled:opacity-60">
                {isCancelling ? "Cancelling…" : "Cancel order"}
              </button>
            )}
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-4">
          <div className="rounded-[22px] bg-primary-50/60 p-4">
            <p className="text-[11px] uppercase tracking-[0.2em] text-gray-500">Date</p>
            <p className="mt-2 text-sm text-gray-700">{orderDate}</p>
          </div>
          <div className="rounded-[22px] bg-primary-50/60 p-4">
            <p className="text-[11px] uppercase tracking-[0.2em] text-gray-500">Status</p>
            <p className="mt-2 text-sm font-medium text-primary-800">{order.status}</p>
          </div>
          <div className="rounded-[22px] bg-primary-50/60 p-4">
            <p className="text-[11px] uppercase tracking-[0.2em] text-gray-500">Payment</p>
            <div className="mt-2"><StatusBadge status={order.payment_status} /></div>
          </div>
          <div className="rounded-[22px] bg-primary-50/60 p-4">
            <p className="text-[11px] uppercase tracking-[0.2em] text-gray-500">Total</p>
            <p className="mt-2 text-lg font-semibold text-primary-900">₹{total.toFixed(2)}</p>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.5fr_0.9fr]">
        <div className="card">
          <h2 className="font-display text-xl font-semibold text-primary-900">Items</h2>
          <div className="mt-4 space-y-4">
            {items.length === 0 ? (
              <p className="text-sm text-gray-500">No items in this order.</p>
            ) : (
              items.map((item) => (
                <div key={item.id || `${order.id}-${item.product_id}`} className="flex items-center justify-between gap-4 rounded-[22px] border border-gray-100 p-4">
                  <div className="flex min-w-0 items-center gap-3">
                    <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-50 text-2xl">
                      {item.product_name ? item.product_name.slice(0, 1).toUpperCase() : "O"}
                    </div>
                    <div className="min-w-0">
                      <p className="truncate font-medium text-primary-900">{item.product_name || "Organic product"}</p>
                      <p className="text-sm text-gray-500">{item.unit || "unit"} · Qty {item.quantity}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500">₹{Number(item.unit_price || 0).toFixed(2)} each</p>
                    <p className="mt-1 font-semibold text-primary-900">₹{Number(item.subtotal ?? Number(item.unit_price || 0) * Number(item.quantity || 0)).toFixed(2)}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <aside className="card">
          <h2 className="font-display text-xl font-semibold text-primary-900">Summary</h2>
          <div className="mt-4 space-y-3 text-sm text-gray-700">
            <div className="flex justify-between">
              <span>Subtotal</span>
              <span>₹{subtotal.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span>Delivery fee</span>
              <span>₹{deliveryFee.toFixed(2)}</span>
            </div>
            <div className="flex justify-between border-t border-gray-200 pt-3 text-base font-semibold text-primary-900">
              <span>Total</span>
              <span>₹{total.toFixed(2)}</span>
            </div>
          </div>

          {delivery && (
            <div className="mt-6 rounded-[22px] border border-primary-100 bg-primary-50/30 p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-gray-500">Delivery</p>
              <p className="mt-2 text-sm font-medium text-primary-900">{delivery.status}</p>
              <p className="mt-1 text-sm text-gray-600">Tracking: {delivery.tracking_number || "Unavailable"}</p>
              {delivery.estimated_delivery_date && (
                <p className="mt-1 text-sm text-gray-600">ETA: {new Date(delivery.estimated_delivery_date).toLocaleDateString()}</p>
              )}
              <Link to={delivery.id ? `/delivery/${delivery.id}` : "/delivery"} className="btn-secondary mt-4 w-full">
                Track delivery
              </Link>
            </div>
          )}
        </aside>
      </div>

      <div className="card">
        <h2 className="font-display text-xl font-semibold text-primary-900">Delivery details</h2>
        {order.shipping_address && (
          <div className="mt-4 rounded-[20px] border border-gray-100 bg-gray-50 p-4">
            <p className="text-[11px] uppercase tracking-[0.2em] text-gray-400">Delivery address</p>
            <p className="mt-2 text-sm text-gray-700">{order.shipping_address}</p>
          </div>
        )}
        {delivery ? (
          <div className="mt-4 space-y-3 text-sm text-gray-600">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[11px] uppercase tracking-[0.2em] text-gray-400">Current status</span>
              <StatusBadge status={delivery.status} />
            </div>
            {delivery.tracking_number && <p>Tracking number: <span className="font-medium text-primary-900">{delivery.tracking_number}</span></p>}
            {delivery.estimated_delivery_date && <p>Estimated delivery: <span className="font-medium text-primary-900">{new Date(delivery.estimated_delivery_date).toLocaleDateString()}</span></p>}
            {delivery.address_line1 && (
              <div className="rounded-[20px] border border-gray-100 bg-gray-50 p-4">
                <p className="text-[11px] uppercase tracking-[0.2em] text-gray-400">Delivery address</p>
                <p className="mt-2 text-sm text-gray-700">
                  {delivery.address_line1}
                  {delivery.address_line2 ? `, ${delivery.address_line2}` : ""}
                  {delivery.city ? `, ${delivery.city}` : ""}
                  {delivery.state ? `, ${delivery.state}` : ""}
                  {delivery.postal_code ? ` ${delivery.postal_code}` : ""}
                  {delivery.country ? `, ${delivery.country}` : ""}
                </p>
              </div>
            )}
            <Link to={delivery.id ? `/delivery/${delivery.id}` : "/delivery"} className="btn-primary inline-flex">
              Track delivery
            </Link>
          </div>
        ) : (
          <p className="mt-4 text-sm text-gray-500">Delivery information is not available for this order yet.</p>
        )}
      </div>
    </div>
  );
}
