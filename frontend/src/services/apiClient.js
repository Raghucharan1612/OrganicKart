import axios from "axios";

/**
 * Single Axios instance used by every service module (authService,
 * userService, addressService, ...). Keeping one instance means auth
 * headers, base URL, and error handling are configured exactly once.
 */
const gatewayBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

const apiClient = axios.create({
  baseURL: `${gatewayBaseUrl}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach the JWT (if we have one) to every outgoing request.
// Reading it from localStorage on each request (rather than trying to
// hold it only in Redux) means a hard page refresh doesn't log the user out.
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("organickart_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Centralized 401 handling: if the token is missing/expired/invalid,
// clear it so the app falls back to the logged-out state instead of
// every screen having to special-case an auth failure itself.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("organickart_token");
    }
    return Promise.reject(error);
  }
);

export default apiClient;
