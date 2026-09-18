import { Link } from "react-router-dom";
import StatusBadge from "@/components/StatusBadge";

export default function OrderCard({ order }) {
  const itemCount = Array.isArray(order.items) ? order.items.reduce((sum, item) => sum + Number(item.quantity || 0), 0) : 0;
  const total = Number(order.total_amount ?? order.total ?? 0);
  const orderDate = order.created_at ? new Date(order.created_at).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" }) : "Date unavailable";
  const paymentStatus = order.payment_status || "PAYMENT_PENDING";

  return (
    <article className="rounded-[26px] border border-gray-100 bg-white p-4 shadow-sm transition hover:shadow-md sm:p-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <p className="text-xs font-medium uppercase tracking-[0.2em] text-primary-600">Order</p>
            <span className="text-sm text-gray-400"># {order.id}</span>
          </div>
          <p className="mt-2 text-sm text-gray-500">{orderDate}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <StatusBadge status={order.status} />
          <StatusBadge status={paymentStatus} />
        </div>
      </div>

      <div className="mt-4 grid gap-3 text-sm text-gray-600 sm:grid-cols-3">
        <div>
          <p className="text-[11px] uppercase tracking-[0.2em] text-gray-400">Items</p>
          <p className="mt-1 font-semibold text-gray-800">{itemCount}</p>
        </div>
        <div>
          <p className="text-[11px] uppercase tracking-[0.2em] text-gray-400">Total</p>
          <p className="mt-1 font-semibold text-gray-800">₹{total.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-[11px] uppercase tracking-[0.2em] text-gray-400">Payment</p>
          <p className="mt-1 font-semibold text-gray-800">{paymentStatus}</p>
        </div>
      </div>

      <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <span className="text-xs text-gray-500">Payment and fulfilment status update from your order.</span>
        <Link to={`/orders/${order.id}`} className="btn-secondary w-full sm:w-auto">
          View details
        </Link>
      </div>
    </article>
  );
}
