import { useEffect, useState } from "react";
import notificationService from "@/services/notificationService";
import Spinner from "@/components/Spinner";
import NotificationItem from "@/components/NotificationItem";
import { getApiErrorMessage } from "@/utils/errorUtils";

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingNotificationId, setUpdatingNotificationId] = useState(null);
  const [isMarkingAllRead, setIsMarkingAllRead] = useState(false);

  const refresh = async () => {
    setIsLoading(true);
    try {
      const data = await notificationService.list();
      setNotifications(Array.isArray(data) ? data : []);
      setError("");
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to load notifications right now."));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const markRead = async (notificationId) => {
    setUpdatingNotificationId(notificationId);
    try {
      const updated = await notificationService.markRead(notificationId);
      setNotifications((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setError("");
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to update this notification."));
    } finally {
      setUpdatingNotificationId(null);
    }
  };

  const markAllRead = async () => {
    setIsMarkingAllRead(true);
    try {
      await notificationService.markAllRead();
      setNotifications((current) =>
        current.map((notification) => ({
          ...notification,
          status: "READ",
          read_at: notification.read_at || new Date().toISOString(),
        }))
      );
      setError("");
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to update notifications."));
    } finally {
      setIsMarkingAllRead(false);
    }
  };

  if (isLoading) return <Spinner label="Loading notifications…" />;

  const unreadCount = notifications.filter((notification) => String(notification.status).toUpperCase() !== "READ").length;

  return (
    <div className="mx-auto max-w-5xl">
      <div className="card">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="font-display text-2xl font-bold text-primary-900">Notifications</h1>
            <p className="mt-1 text-sm text-gray-500">
              {unreadCount ? `${unreadCount} unread notification${unreadCount === 1 ? "" : "s"}` : "You are all caught up."}
            </p>
          </div>
          {unreadCount > 0 && (
            <button type="button" onClick={markAllRead} disabled={isMarkingAllRead} className="btn-secondary disabled:opacity-60">
              {isMarkingAllRead ? "Updating…" : "Mark all as read"}
            </button>
          )}
        </div>

        {error && <div className="mt-4 rounded-[18px] border border-red-100 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

        {notifications.length === 0 ? (
          <div className="mt-6 rounded-[22px] border border-dashed border-gray-200 bg-primary-50/30 p-8 text-center text-gray-600">
            Your notifications are clear.
          </div>
        ) : (
          <div className="mt-6 space-y-3">
            {notifications.map((notification) => (
              <NotificationItem key={notification.id} notification={notification} onMarkRead={markRead} isUpdating={updatingNotificationId === notification.id} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
