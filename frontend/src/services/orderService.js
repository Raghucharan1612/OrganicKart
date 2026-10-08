import apiClient from "./apiClient";

const orderService = {
  getCart: () => apiClient.get("/cart").then((res) => res.data),

  addItem: (payload) => apiClient.post("/cart/items", payload).then((res) => res.data),

  updateItem: (itemId, payload) => apiClient.put(`/cart/items/${itemId}`, payload).then((res) => res.data),

  removeItem: (itemId) => apiClient.delete(`/cart/items/${itemId}`).then((res) => res.data),

  clearCart: () => apiClient.delete("/cart").then((res) => res.data),

  listOrders: () => apiClient.get("/orders").then((res) => res.data),

  getOrder: (id) => apiClient.get(`/orders/${id}`).then((res) => res.data),

  initiateCheckout: (addressId, idempotencyKey) => apiClient.post(
    "/orders/checkout/initiate",
    { address_id: addressId },
    { headers: { "Idempotency-Key": idempotencyKey } }
  ).then((res) => res.data),

  verifyPayment: (payload) => apiClient.post("/orders/payments/verify", payload).then((res) => res.data),

  cancelOrder: (id) => apiClient.post(`/orders/${id}/cancel`).then((res) => res.data),

  getSellerOrders: () => apiClient.get("/orders/seller").then((res) => res.data),

  getSellerAnalytics: () => apiClient.get("/orders/seller/analytics").then((res) => res.data),
};

export default orderService;
