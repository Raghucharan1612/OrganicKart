import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import orderService from "@/services/orderService";
import Spinner from "@/components/Spinner";
import OrderCard from "@/components/OrderCard";
import { getApiErrorMessage } from "@/utils/errorUtils";

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    orderService
      .listOrders()
      .then((data) => {
        if (active) setOrders(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        if (active) setError(getApiErrorMessage(err, "Unable to load your order history right now."));
      })
      .finally(() => active && setIsLoading(false));

    return () => {
      active = false;
    };
  }, []);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-5xl space-y-4">
        <div className="card animate-pulse">
          <div className="h-6 w-48 rounded bg-gray-200" />
          <div className="mt-4 h-4 w-64 rounded bg-gray-200" />
        </div>
        {[1, 2, 3].map((key) => (
          <div key={key} className="card animate-pulse">
            <div className="h-6 w-40 rounded bg-gray-200" />
            <div className="mt-4 h-4 w-full rounded bg-gray-200" />
            <div className="mt-3 h-4 w-2/3 rounded bg-gray-200" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-6">
      <div className="card">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h1 className="font-display text-2xl font-bold text-primary-900">Order History</h1>
            <p className="mt-1 text-sm text-gray-500">Track your latest organic grocery orders and delivery updates.</p>
          </div>
          <Link to="/products" className="btn-secondary">Continue Shopping</Link>
        </div>
      </div>

      {error && (
        <div className="rounded-2xl border border-red-100 bg-red-50 p-4 text-sm text-red-700">
          <p className="font-semibold">Unable to load your orders.</p>
          <p className="mt-1">{error}</p>
          <button type="button" onClick={() => window.location.reload()} className="btn-secondary mt-3">
            Retry
          </button>
        </div>
      )}

      {orders.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-lg font-bold text-primary-900">No orders placed yet</p>
          <p className="mt-2 text-sm text-gray-600">Your recent grocery orders will appear here once you make a purchase.</p>
          <Link to="/products" className="btn-primary mt-5 inline-flex font-bold">Start Shopping →</Link>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <OrderCard key={order.id} order={order} />
          ))}
        </div>
      )}
    </div>
  );
}

