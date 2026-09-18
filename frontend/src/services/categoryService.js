import apiClient from "./apiClient";

const categoryService = {
  list: (includeInactive = false) =>
    apiClient
      .get("/categories", { params: includeInactive ? { include_inactive: true } : {} })
      .then((res) => res.data),

  get: (id) => apiClient.get(`/categories/${id}`).then((res) => res.data),

  create: (payload) => apiClient.post("/categories", payload).then((res) => res.data),

  update: (id, payload) => apiClient.put(`/categories/${id}`, payload).then((res) => res.data),

  deactivate: (id) => apiClient.delete(`/categories/${id}`).then((res) => res.data),
};

export default categoryService;
