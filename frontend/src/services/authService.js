import apiClient from "./apiClient";

/**
 * All calls to /api/v1/auth/*. Components and Redux thunks call these
 * functions instead of using apiClient directly, so the API contract
 * lives in exactly one place per resource.
 */
const authService = {
  register: (payload) => apiClient.post("/auth/register", payload).then((res) => res.data),

  login: (payload) => apiClient.post("/auth/login", payload).then((res) => res.data),

  logout: () => apiClient.post("/auth/logout").then((res) => res.data),

  getCurrentUser: () => apiClient.get("/auth/me").then((res) => res.data),

  requestPasswordReset: (payload) => apiClient.post("/auth/password-reset/request", payload).then((res) => res.data),

  resetPassword: (payload) => apiClient.post("/auth/password-reset/confirm", payload).then((res) => res.data),
};

export default authService;
