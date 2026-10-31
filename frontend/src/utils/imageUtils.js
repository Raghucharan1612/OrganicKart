/**
 * Utility functions for resolving, validating, and formatting product images.
 * Always routes relative URLs to the API Gateway on port 8000.
 */

export const GATEWAY_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
export const FALLBACK_PRODUCT_IMAGE = "/images/product-placeholder.svg";

/**
 * Returns a fully-qualified or safely resolvable image URL.
 * Falls back to FALLBACK_PRODUCT_IMAGE if empty.
 */
export function getProductImageUrl(imageUrl) {
  if (!imageUrl || typeof imageUrl !== "string") {
    return FALLBACK_PRODUCT_IMAGE;
  }

  const trimmed = imageUrl.trim();
  if (!trimmed) {
    return FALLBACK_PRODUCT_IMAGE;
  }

  if (
    trimmed.startsWith("http://") ||
    trimmed.startsWith("https://") ||
    trimmed.startsWith("blob:") ||
    trimmed.startsWith("data:")
  ) {
    return trimmed;
  }

  // Prepend gateway base URL if starts with /api or relative path
  if (trimmed.startsWith("/")) {
    return `${GATEWAY_BASE_URL}${trimmed}`;
  }

  return `${GATEWAY_BASE_URL}/${trimmed}`;
}

export const SUPPORTED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp", "image/avif"];
export const MAX_IMAGE_FILE_SIZE = 5 * 1024 * 1024; // 5 MB

export function validateImageFile(file) {
  if (!file) {
    return "Please choose an image file.";
  }

  if (!SUPPORTED_IMAGE_TYPES.includes(file.type)) {
    return `Unsupported format (${file.type || "unknown"}). Only JPEG, PNG, WebP, and AVIF are supported.`;
  }

  if (file.size > MAX_IMAGE_FILE_SIZE) {
    const sizeInMb = (file.size / (1024 * 1024)).toFixed(1);
    return `File size (${sizeInMb}MB) exceeds the 5MB limit.`;
  }

  return null;
}
