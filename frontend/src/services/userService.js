import apiClient from "./apiClient";

const userService = {
  getProfile: () => apiClient.get("/users/me").then((res) => res.data),

  updateProfile: (payload) => apiClient.put("/users/me", payload).then((res) => res.data),

  changePassword: (payload) => apiClient.post("/users/me/change-password", payload).then((res) => res.data),
};

export default userService;
