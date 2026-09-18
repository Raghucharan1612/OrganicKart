/**
 * Lightweight client-side validation helpers shared across auth and
 * profile forms. These mirror (but do not replace) the backend's
 * Pydantic validation — the server always re-validates independently.
 */
export function validateEmail(value) {
  if (!value) return "Email is required.";
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!pattern.test(value)) return "Enter a valid email address.";
  return "";
}

export function validatePassword(value) {
  if (!value) return "Password is required.";
  if (value.length < 8) return "Password must be at least 8 characters.";
  if (!/\d/.test(value)) return "Password must contain at least one digit.";
  if (!/[a-zA-Z]/.test(value)) return "Password must contain at least one letter.";
  return "";
}

export function validateRequired(value, fieldName = "This field") {
  if (!value || !String(value).trim()) return `${fieldName} is required.`;
  return "";
}

export function validatePhone(value) {
  if (!value) return "";
  const pattern = /^[0-9+\-\s()]{7,20}$/;
  if (!pattern.test(value)) return "Enter a valid phone number.";
  return "";
}
