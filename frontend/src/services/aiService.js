import apiClient from "./apiClient";

const aiService = {
  /**
   * Send a question/message to the Customer AI Assistant via API Gateway.
   * Endpoint: POST /api/v1/ai/chat
   * Authentication token is automatically attached by apiClient request interceptor.
   *
   * @param {string} message - Customer message
   * @returns {Promise<{ answer: string, sources: Array<{ document: string, title: string, score?: number }> }>}
   */
  async sendCustomerMessage(message) {
    const response = await apiClient.post("/ai/chat", { message });
    return response.data;
  },

  /**
   * Send a question/message to the Vendor/Farmer AI Assistant via API Gateway.
   * Endpoint: POST /api/v1/ai/vendor/chat
   * Authentication token is automatically attached by apiClient request interceptor.
   *
   * @param {string} message - Vendor/Farmer message
   * @returns {Promise<{ answer: string, sources: Array<{ document: string, title: string, score?: number }> }>}
   */
  async sendVendorMessage(message) {
    const response = await apiClient.post("/ai/vendor/chat", { message });
    return response.data;
  },

  /**
   * Send an ADMIN business question through the API Gateway.
   * Authentication is attached by the shared apiClient interceptor.
   *
   * @param {string} message - Admin message
   * @returns {Promise<{ answer: string, sources: Array<{ document: string, title: string, score?: number }> }>}
   */
  async sendAdminMessage(message) {
    const response = await apiClient.post("/ai/admin/chat", { message });
    return response.data;
  },
};

export default aiService;
