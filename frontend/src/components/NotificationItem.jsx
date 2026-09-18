import StatusBadge from "@/components/StatusBadge";

export default function NotificationItem({ notification, onMarkRead, isUpdating = false }) {
  const isUnread = notification.status !== "READ" && notification.status !== "read";
  const createdAt = notification.created_at
    ? new Date(notification.created_at).toLocaleString(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" })
    : "Just now";

  return (
    <article className={`rounded-[22px] border p-4 shadow-sm ${isUnread ? "border-primary-200 bg-primary-50/40" : "border-gray-100 bg-white"}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-medium text-primary-900">{notification.title || "Notification"}</h3>
            {isUnread && <StatusBadge status="PENDING" />}
          </div>
          <p className="mt-2 text-sm leading-relaxed text-gray-600">{notification.message}</p>
          <div className="mt-3 flex flex-wrap items-center gap-3 text-[11px] uppercase tracking-[0.15em] text-gray-400">
            <span>{notification.type || "GENERAL"}</span>
            <span>{createdAt}</span>
          </div>
        </div>

        {isUnread && (
          <button type="button" onClick={() => onMarkRead(notification.id)} disabled={isUpdating} className="shrink-0 text-sm font-medium text-primary-700 hover:text-primary-900 disabled:opacity-60">
            {isUpdating ? "Updating…" : "Mark read"}
          </button>
        )}
      </div>
    </article>
  );
}
