import apiClient from "./apiClient";

const deliveryService = {
  listDeliveries: () => apiClient.get("/deliveries").then((res) => res.data),

  getDelivery: (id) => apiClient.get(`/deliveries/${id}`).then((res) => res.data),

  getAvailableDeliveries: () => apiClient.get("/deliveries/partner/available").then((res) => res.data),

  getAssignedDeliveries: () => apiClient.get("/deliveries/partner/assigned").then((res) => res.data),

  acceptDelivery: (id) => apiClient.post(`/deliveries/${id}/accept`).then((res) => res.data),

  createDelivery: (payload) => apiClient.post("/deliveries", payload).then((res) => res.data),

  updateDelivery: (id, payload) => apiClient.put(`/deliveries/${id}`, payload).then((res) => res.data),

  updateDeliveryStatus: (id, payload) => apiClient.patch(`/deliveries/${id}/status`, payload).then((res) => res.data),
};

export default deliveryService;
