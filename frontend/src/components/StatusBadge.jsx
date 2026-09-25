const STATUS_STYLES = {
  PENDING: "bg-amber-50 text-amber-700 ring-amber-200/80",
  PAYMENT_PENDING: "bg-amber-50 text-amber-700 ring-amber-200/80",
  PAID: "bg-emerald-50 text-emerald-700 ring-emerald-200/80",
  APPROVED: "bg-emerald-50 text-emerald-700 ring-emerald-200/80",
  PLACED: "bg-emerald-50 text-emerald-700 ring-emerald-200/80",
  CONFIRMED: "bg-emerald-50 text-emerald-700 ring-emerald-200/80",
  PROCESSING: "bg-amber-50 text-amber-700 ring-amber-200/80",
  PICKED_UP: "bg-amber-50 text-amber-700 ring-amber-200/80",
  IN_TRANSIT: "bg-emerald-50 text-emerald-700 ring-emerald-200/80",
  OUT_FOR_DELIVERY: "bg-emerald-50 text-emerald-700 ring-emerald-200/80",
  SHIPPED: "bg-emerald-50 text-emerald-700 ring-emerald-200/80",
  DELIVERED: "bg-emerald-50 text-emerald-700 ring-emerald-200/80",
  REJECTED: "bg-red-50 text-red-700 ring-red-200/80",
  FAILED: "bg-red-50 text-red-700 ring-red-200/80",
  CANCELLED: "bg-red-50 text-red-700 ring-red-200/80",
};

export default function StatusBadge({ status }) {
  const normalized = String(status || "PENDING").toUpperCase();
  const style = STATUS_STYLES[normalized] || "bg-primary-50 text-primary-700 ring-primary-200/80";

  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-semibold ring-1 ${style}`}>
      {normalized}
    </span>
  );
}
