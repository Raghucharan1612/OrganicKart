import apiClient from "./apiClient";

const addressService = {
  list: () => apiClient.get("/users/me/addresses").then((res) => res.data),

  create: (payload) => apiClient.post("/users/me/addresses", payload).then((res) => res.data),

  update: (id, payload) => apiClient.put(`/users/me/addresses/${id}`, payload).then((res) => res.data),

  remove: (id) => apiClient.delete(`/users/me/addresses/${id}`).then((res) => res.data),
};

export default addressService;
