import apiClient from "./apiClient";

const notificationService = {
  list: () => apiClient.get("/notifications").then((res) => res.data),

  get: (id) => apiClient.get(`/notifications/${id}`).then((res) => res.data),

  markRead: (id) => apiClient.patch(`/notifications/${id}/read`).then((res) => res.data),

  markAllRead: () => apiClient.patch("/notifications/read-all").then((res) => res.data),
};

export default notificationService;
