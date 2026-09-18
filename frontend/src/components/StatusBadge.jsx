const STATUS_STYLES = {
  PENDING: "bg-slate-100 text-slate-700 ring-slate-200",
  PAYMENT_PENDING: "bg-amber-100 text-amber-700 ring-amber-200",
  PAID: "bg-emerald-100 text-emerald-700 ring-emerald-200",
  PLACED: "bg-slate-100 text-slate-700 ring-slate-200",
  CONFIRMED: "bg-emerald-100 text-emerald-700 ring-emerald-200",
  PROCESSING: "bg-amber-100 text-amber-700 ring-amber-200",
  PICKED_UP: "bg-amber-100 text-amber-700 ring-amber-200",
  IN_TRANSIT: "bg-sky-100 text-sky-700 ring-sky-200",
  OUT_FOR_DELIVERY: "bg-violet-100 text-violet-700 ring-violet-200",
  SHIPPED: "bg-sky-100 text-sky-700 ring-sky-200",
  DELIVERED: "bg-emerald-100 text-emerald-700 ring-emerald-200",
  FAILED: "bg-red-100 text-red-700 ring-red-200",
  CANCELLED: "bg-red-100 text-red-700 ring-red-200",
};

export default function StatusBadge({ status }) {
  const normalized = String(status || "PENDING").toUpperCase();
  const style = STATUS_STYLES[normalized] || "bg-primary-100 text-primary-700 ring-primary-200";

  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-semibold ring-1 ${style}`}>
      {normalized}
    </span>
  );
}
