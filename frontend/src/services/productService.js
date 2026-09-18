import apiClient from "./apiClient";

/**
 * All product queries go through the backend as real query params —
 * search/filter/sort/pagination happen in SQL, never by downloading
 * the whole catalog and filtering in the browser.
 */
const productService = {
  list: (params = {}) => apiClient.get("/products", { params }).then((res) => res.data),

  getById: (id) => apiClient.get(`/products/${id}`).then((res) => res.data),

  listMine: () => apiClient.get("/products/mine").then((res) => res.data),

  create: (payload) => apiClient.post("/products", payload).then((res) => res.data),

  update: (id, payload) => apiClient.put(`/products/${id}`, payload).then((res) => res.data),

  approve: (id) => apiClient.post(`/products/${id}/approve`).then((res) => res.data),

  reject: (id) => apiClient.post(`/products/${id}/reject`).then((res) => res.data),

  deactivate: (id) => apiClient.delete(`/products/${id}`).then((res) => res.data),
};

export default productService;
