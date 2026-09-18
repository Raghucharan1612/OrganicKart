import { useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import deliveryService from "@/services/deliveryService";
import Spinner from "@/components/Spinner";
import StatusBadge from "@/components/StatusBadge";
import DeliveryTimeline from "@/components/DeliveryTimeline";
import { getApiErrorMessage } from "@/utils/errorUtils";

const NEXT_STATUSES = {
  PENDING: ["CONFIRMED", "ACCEPTED"],
  CONFIRMED: ["ACCEPTED", "PICKED_UP"],
  ACCEPTED: ["PICKED_UP"],
  ASSIGNED: ["PICKED_UP"],
  PICKED_UP: ["IN_TRANSIT", "OUT_FOR_DELIVERY"],
  IN_TRANSIT: ["OUT_FOR_DELIVERY"],
  OUT_FOR_DELIVERY: ["DELIVERED"],
  DELIVERED: [],
  FAILED: [],
  CANCELLED: [],
};

const STATUS_LABELS = {
  PICKED_UP: "Mark Picked Up",
  IN_TRANSIT: "Mark In Transit",
  OUT_FOR_DELIVERY: "Mark Out for Delivery",
  DELIVERED: "Mark Delivered",
  ACCEPTED: "Accept Delivery",
  CONFIRMED: "Confirm Delivery",
};

export default function DeliveryPage() {
  const { user } = useAuth();
  const isPartner = user?.role === "DELIVERY_PARTNER";

  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const [deliveries, setDeliveries] = useState([]);
  const [availableDeliveries, setAvailableDeliveries] = useState([]);
  const [assignedDeliveries, setAssignedDeliveries] = useState([]);
  const [selectedDelivery, setSelectedDelivery] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");
  const [actionSuccess, setActionSuccess] = useState("");
  const [processingId, setProcessingId] = useState(null);

  const normalizeList = (res) => {
    if (Array.isArray(res)) return res;
    if (res && typeof res === "object" && res.id) return [res];
    return [];
  };

  const loadPartnerData = async () => {
    setError("");
    const [availableResult, assignedResult] = await Promise.allSettled([
      deliveryService.getAvailableDeliveries(),
      deliveryService.getAssignedDeliveries(),
    ]);

    setAvailableDeliveries(normalizeList(availableResult.status === "fulfilled" ? availableResult.value : []));
    setAssignedDeliveries(normalizeList(assignedResult.status === "fulfilled" ? assignedResult.value : []));
    const failedResult = [availableResult, assignedResult].find((result) => result.status === "rejected");
    if (failedResult) {
      setError(getApiErrorMessage(failedResult.reason, "Unable to load partner deliveries."));
    }
  };

  const loadCustomerData = async () => {
    try {
      setError("");
      const data = await deliveryService.listDeliveries();
      const next = normalizeList(data);
      setDeliveries(next);

      const targetId = id ? Number(id) : null;
      const targetOrderId = searchParams.get("order") ? Number(searchParams.get("order")) : null;
      const match =
        next.find((item) => (targetId ? Number(item.id) === targetId : Number(item.order_id) === targetOrderId)) ||
        next[0] ||
        null;
      setSelectedDelivery(match);
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to load delivery information right now."));
    }
  };

  useEffect(() => {
    let active = true;
    setIsLoading(true);
    const promise = isPartner ? loadPartnerData() : loadCustomerData();
    promise.finally(() => active && setIsLoading(false));

    return () => {
      active = false;
    };
  }, [id, searchParams, isPartner]);

  const handleAccept = async (deliveryId) => {
    setProcessingId(deliveryId);
    setActionError("");
    setActionSuccess("");
    try {
      await deliveryService.acceptDelivery(deliveryId);
      setActionSuccess(`Successfully accepted delivery #${deliveryId}!`);
      await loadPartnerData();
    } catch (err) {
      setActionError(getApiErrorMessage(err, "Failed to accept delivery. It may already have been accepted by another partner."));
    } finally {
      setProcessingId(null);
    }
  };

  const handleStatusUpdate = async (deliveryId, newStatus) => {
    setProcessingId(deliveryId);
    setActionError("");
    setActionSuccess("");
    try {
      await deliveryService.updateDeliveryStatus(deliveryId, { status: newStatus });
      setActionSuccess(`Updated delivery #${deliveryId} status to ${newStatus.replace(/_/g, " ")}.`);
      await loadPartnerData();
    } catch (err) {
      setActionError(getApiErrorMessage(err, "Failed to update delivery status."));
    } finally {
      setProcessingId(null);
    }
  };

  if (isLoading) return <Spinner label="Loading delivery information..." />;

  // Delivery Partner View
  if (isPartner) {
    const activeDeliveriesCount = assignedDeliveries.filter(
      (d) => !["DELIVERED", "FAILED", "CANCELLED"].includes(d.status)
    ).length;

    return (
      <div className="mx-auto max-w-6xl space-y-6 pb-12">
        {/* Header & Role Badge */}
        <div className="bg-white rounded-[24px] p-6 shadow-sm border border-gray-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
                Partner Portal
              </span>
              <span className="text-xs text-gray-400">• Quick Commerce Logistics</span>
            </div>
            <h1 className="font-display text-2xl font-bold text-gray-900 mt-1">Delivery Partner Dashboard</h1>
            <p className="text-xs text-gray-500 mt-0.5">Manage incoming orders, update tracking statuses, and fulfill customer deliveries.</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={loadPartnerData}
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-700 bg-gray-50 hover:bg-gray-100 px-3.5 py-2 rounded-xl border border-gray-200 transition"
              title="Refresh Data"
            >
              🔄 Refresh
            </button>
            <span className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-600 text-white text-xs font-semibold shadow-sm">
              🚚 Partner Active
            </span>
          </div>
        </div>

        {/* Notifications / Banners */}
        {error && <div className="rounded-[18px] border border-red-200 bg-red-50 p-4 text-sm font-medium text-red-800 shadow-sm">{error}</div>}
        {actionError && <div className="rounded-[18px] border border-red-200 bg-red-50 p-4 text-sm font-medium text-red-800 shadow-sm">{actionError}</div>}
        {actionSuccess && <div className="rounded-[18px] border border-emerald-200 bg-emerald-50 p-4 text-sm font-semibold text-emerald-900 shadow-sm flex items-center gap-2"><span>✅</span> {actionSuccess}</div>}

        {/* Dashboard Summary Statistics */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white rounded-[22px] p-5 border border-gray-100 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Available Queue</p>
              <p className="text-3xl font-extrabold text-gray-900 mt-1">{availableDeliveries.length}</p>
              <p className="text-[11px] text-gray-400 mt-0.5">Ready for pickup</p>
            </div>
            <div className="h-12 w-12 rounded-2xl bg-amber-50 text-amber-600 font-bold flex items-center justify-center text-xl">
              📋
            </div>
          </div>

          <div className="bg-white rounded-[22px] p-5 border border-emerald-100 bg-emerald-50/30 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-emerald-800 uppercase tracking-wider">My Assigned</p>
              <p className="text-3xl font-extrabold text-emerald-900 mt-1">{assignedDeliveries.length}</p>
              <p className="text-[11px] text-emerald-600 mt-0.5">Total assigned to you</p>
            </div>
            <div className="h-12 w-12 rounded-2xl bg-emerald-100 text-emerald-700 font-bold flex items-center justify-center text-xl">
              📦
            </div>
          </div>

          <div className="bg-white rounded-[22px] p-5 border border-gray-100 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Active Deliveries</p>
              <p className="text-3xl font-extrabold text-primary-900 mt-1">{activeDeliveriesCount}</p>
              <p className="text-[11px] text-gray-400 mt-0.5">In-progress deliveries</p>
            </div>
            <div className="h-12 w-12 rounded-2xl bg-primary-50 text-primary-700 font-bold flex items-center justify-center text-xl">
              ⚡
            </div>
          </div>
        </div>

        {/* Section 1: Assigned Deliveries */}
        <div className="bg-white rounded-[24px] p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between border-b border-gray-100 pb-4 mb-6">
            <div>
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <span>📦</span> My Assigned Deliveries ({assignedDeliveries.length})
              </h2>
              <p className="text-xs text-gray-500 mt-0.5">Deliveries currently assigned to your account. Update statuses as you progress.</p>
            </div>
          </div>

          {assignedDeliveries.length === 0 ? (
            <div className="rounded-[20px] border border-dashed border-gray-200 bg-gray-50/50 p-8 text-center">
              <span className="text-3xl">📭</span>
              <p className="mt-2 text-sm font-semibold text-gray-700">No active assigned deliveries</p>
              <p className="text-xs text-gray-500 mt-1">Accept an available delivery from the queue below to start!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {assignedDeliveries.map((delivery) => {
                const availableNext = NEXT_STATUSES[delivery.status] || [];
                return (
                  <div
                    key={delivery.id}
                    className="rounded-[22px] border border-emerald-200/80 bg-emerald-50/20 p-5 shadow-sm hover:shadow-md transition"
                  >
                    <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
                      {/* Delivery Details */}
                      <div className="space-y-3 flex-1">
                        <div className="flex flex-wrap items-center gap-2.5">
                          <span className="font-bold text-gray-900 text-base">Delivery #{delivery.id}</span>
                          <span className="bg-gray-100 text-gray-700 text-xs px-2.5 py-0.5 rounded-md font-mono">
                            Order #{delivery.order_id}
                          </span>
                          <span className="text-xs font-mono text-gray-500 bg-gray-50 px-2 py-0.5 rounded border border-gray-200">
                            {delivery.tracking_number}
                          </span>
                          <StatusBadge status={delivery.status} />
                        </div>

                        {/* Customer & Address Details */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs bg-white rounded-xl p-3.5 border border-gray-100">
                          <div>
                            <p className="text-[10px] uppercase font-bold text-gray-400">Recipient</p>
                            <p className="font-semibold text-gray-800 text-sm mt-0.5">{delivery.recipient_name || `Customer #${delivery.user_id}`}</p>
                            <p className="text-gray-500 mt-0.5">{delivery.recipient_phone ? `📞 ${delivery.recipient_phone}` : "No phone listed"}</p>
                          </div>
                          <div>
                            <p className="text-[10px] uppercase font-bold text-gray-400">Delivery Address</p>
                            <p className="font-medium text-gray-700 text-xs mt-0.5">
                              {delivery.address_line1}
                              {delivery.address_line2 ? `, ${delivery.address_line2}` : ""}
                            </p>
                            <p className="text-gray-500 text-xs">
                              {delivery.city ? `${delivery.city}, ` : ""}
                              {delivery.state ? `${delivery.state} ` : ""}
                              {delivery.postal_code || ""}
                            </p>
                          </div>
                        </div>

                        {/* Timestamps */}
                        <div className="flex flex-wrap items-center gap-4 text-[11px] text-gray-500">
                          {delivery.estimated_delivery_date && (
                            <span>📅 Est. Delivery: {new Date(delivery.estimated_delivery_date).toLocaleDateString()}</span>
                          )}
                          {delivery.accepted_at && (
                            <span>⏰ Accepted: {new Date(delivery.accepted_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                          )}
                          {delivery.shipped_at && (
                            <span>🚚 Shipped: {new Date(delivery.shipped_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                          )}
                        </div>
                      </div>

                      {/* Action Controls */}
                      <div className="lg:self-center shrink-0 border-t lg:border-t-0 border-gray-200/60 pt-3 lg:pt-0">
                        {availableNext.length > 0 ? (
                          <div className="flex flex-wrap items-center gap-2">
                            {availableNext.map((nextSt) => (
                              <button
                                key={nextSt}
                                onClick={() => handleStatusUpdate(delivery.id, nextSt)}
                                disabled={processingId === delivery.id}
                                className="bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition shadow-sm disabled:opacity-50 flex items-center gap-1.5"
                              >
                                {processingId === delivery.id ? "Updating..." : (STATUS_LABELS[nextSt] || `Mark ${nextSt.replace(/_/g, " ")}`)}
                              </button>
                            ))}
                          </div>
                        ) : (
                          <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-800 bg-emerald-100 px-3 py-1.5 rounded-xl">
                            <span>✨</span> Status Complete ({delivery.status})
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Section 2: Available Deliveries Queue */}
        <div className="bg-white rounded-[24px] p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between border-b border-gray-100 pb-4 mb-6">
            <div>
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <span>📋</span> Available Deliveries ({availableDeliveries.length})
              </h2>
              <p className="text-xs text-gray-500 mt-0.5">Paid customer orders waiting to be claimed by an available delivery partner.</p>
            </div>
          </div>

          {availableDeliveries.length === 0 ? (
            <div className="rounded-[20px] border border-dashed border-gray-200 bg-gray-50/50 p-8 text-center text-sm text-gray-500">
              No available deliveries in queue right now. Check back soon!
            </div>
          ) : (
            <div className="space-y-4">
              {availableDeliveries.map((delivery) => (
                <div
                  key={delivery.id}
                  className="rounded-[22px] border border-gray-200 bg-white p-5 shadow-sm hover:border-emerald-300 transition flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-gray-900 text-base">Delivery #{delivery.id}</span>
                      <span className="text-xs text-gray-400 font-mono">• Order #{delivery.order_id}</span>
                      <StatusBadge status={delivery.status} />
                    </div>
                    <p className="text-sm font-semibold text-gray-800">{delivery.recipient_name || `Customer #${delivery.user_id}`}</p>
                    <p className="text-xs text-gray-500">
                      📍 {delivery.address_line1}
                      {delivery.city ? `, ${delivery.city}` : ""}
                      {delivery.postal_code ? ` (${delivery.postal_code})` : ""}
                    </p>
                  </div>

                  <button
                    onClick={() => handleAccept(delivery.id)}
                    disabled={processingId === delivery.id}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs px-5 py-2.5 rounded-xl shadow-sm hover:shadow transition disabled:opacity-50 shrink-0"
                  >
                    {processingId === delivery.id ? "Accepting..." : "Accept Delivery"}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Customer View
  if (selectedDelivery) {
    return (
      <div className="mx-auto max-w-5xl space-y-6">
        <div className="card">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-medium uppercase tracking-[0.2em] text-primary-600">Tracking</p>
              <h1 className="font-display text-2xl font-bold text-primary-900">{selectedDelivery.tracking_number || "Tracking unavailable"}</h1>
            </div>
            <StatusBadge status={selectedDelivery.status} />
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <div className="rounded-[22px] bg-primary-50/60 p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-gray-500">Recipient</p>
              <p className="mt-2 font-medium text-primary-900">{selectedDelivery.recipient_name || "Recipient unavailable"}</p>
              <p className="text-sm text-gray-600">{selectedDelivery.recipient_phone || "Phone not provided"}</p>
            </div>
            <div className="rounded-[22px] bg-primary-50/60 p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-gray-500">Estimated delivery</p>
              <p className="mt-2 font-medium text-primary-900">
                {selectedDelivery.estimated_delivery_date ? new Date(selectedDelivery.estimated_delivery_date).toLocaleDateString() : "Pending"}
              </p>
            </div>
          </div>

          {selectedDelivery.address_line1 && (
            <div className="mt-6 rounded-[22px] border border-gray-100 bg-gray-50 p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-gray-400">Delivery address</p>
              <p className="mt-2 text-sm text-gray-700">
                {selectedDelivery.address_line1}
                {selectedDelivery.address_line2 ? `, ${selectedDelivery.address_line2}` : ""}
                {selectedDelivery.city ? `, ${selectedDelivery.city}` : ""}
                {selectedDelivery.state ? `, ${selectedDelivery.state}` : ""}
                {selectedDelivery.postal_code ? ` ${selectedDelivery.postal_code}` : ""}
                {selectedDelivery.country ? `, ${selectedDelivery.country}` : ""}
              </p>
            </div>
          )}

          <DeliveryTimeline status={selectedDelivery.status} />
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl">
      <div className="card">
        <h1 className="font-display text-2xl font-bold text-primary-900">Delivery information</h1>
        <p className="mt-1 text-sm text-gray-500">Track your active and past deliveries.</p>

        {error && <div className="mt-4 rounded-[18px] border border-red-100 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

        {searchParams.get("order") ? (
          <div className="mt-6 rounded-[22px] border border-primary-100 bg-primary-50/50 p-8 text-center text-gray-700">
            <p className="font-semibold text-primary-900">Delivery setup is pending</p>
            <p className="mt-1 text-sm">Your order was placed successfully. Tracking will appear here once a delivery is assigned.</p>
          </div>
        ) : deliveries.length === 0 ? (
          <div className="mt-6 rounded-[22px] border border-dashed border-gray-200 bg-primary-50/30 p-8 text-center text-gray-600">
            No delivery records yet.
          </div>
        ) : (
          <div className="mt-6 space-y-4">
            {deliveries.map((delivery) => (
              <div key={delivery.id} className="rounded-[22px] border border-gray-100 bg-white p-4 shadow-sm">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-medium text-primary-900">#{delivery.id}</p>
                    <p className="text-sm text-gray-500">Tracking: {delivery.tracking_number || "Unavailable"}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <StatusBadge status={delivery.status} />
                    <Link to={`/delivery/${delivery.id}`} className="btn-secondary">
                      View
                    </Link>
                  </div>
                </div>
                <p className="mt-3 text-sm text-gray-600">{delivery.address_line1 || "Delivery address pending"}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
