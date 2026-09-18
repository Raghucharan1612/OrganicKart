/**
 * Safely extracts a human-readable error string from API / Axios errors.
 * Never returns a non-string object, ensuring React never crashes when rendering it.
 */
export function getApiErrorMessage(error, fallback = "An unexpected error occurred.") {
  if (!error) return fallback;
  if (typeof error === "string") return error;

  // Extract from error.response?.data?.detail
  const detail = error.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    const firstMsg = detail[0]?.msg || detail[0]?.message || (typeof detail[0] === "string" ? detail[0] : null);
    if (typeof firstMsg === "string" && firstMsg.trim()) return firstMsg;
  }
  if (typeof detail?.detail === "string") return detail.detail;
  if (typeof detail?.message === "string") return detail.message;
  if (typeof detail === "object" && detail !== null) {
    if (typeof detail.msg === "string") return detail.msg;
    try {
      const str = JSON.stringify(detail);
      if (str && str !== "{}") return str;
    } catch {
      // ignore serialization error
    }
  }

  // Extract from error.response?.data?.message
  const message = error.response?.data?.message;
  if (typeof message === "string") return message;

  // Extract from error.message
  if (typeof error.message === "string" && error.message.trim()) {
    return error.message;
  }

  return fallback;
}
