import apiClient from "./apiClient";

const CATALOG_CACHE_TTL_MS = 60_000;
const catalogCache = new Map();
const catalogInFlight = new Map();

const normalizeCatalogParams = (params) =>
  Object.entries(params)
    .filter(([, value]) => value !== undefined && value !== null && value !== "")
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([key, value]) => `${key}=${String(value)}`)
    .join("&");

// Only cache requests guaranteed to receive the public catalog view. Explicit
// certification filters can return role-specific admin data, so they always
// bypass this shared in-memory cache.
const isPublicCatalogQuery = (params) => !params.seller_id && !params.certification;

const getCachedCatalog = (params) => {
  const key = normalizeCatalogParams(params);
  const cached = catalogCache.get(key);
  if (cached && Date.now() - cached.createdAt < CATALOG_CACHE_TTL_MS) {
    return Promise.resolve(cached.data);
  }

  if (catalogInFlight.has(key)) return catalogInFlight.get(key);

  const request = apiClient
    .get("/products", { params })
    .then((res) => {
      catalogCache.set(key, { data: res.data, createdAt: Date.now() });
      return res.data;
    })
    .finally(() => catalogInFlight.delete(key));

  catalogInFlight.set(key, request);
  return request;
};

export const invalidateCatalogCache = () => {
  catalogCache.clear();
  catalogInFlight.clear();
};

/**
 * All product queries go through the backend as real query params —
 * search/filter/sort/pagination happen in SQL, never by downloading
 * the whole catalog and filtering in the browser.
 */
const productService = {
  list: (params = {}) =>
    isPublicCatalogQuery(params)
      ? getCachedCatalog(params)
      : apiClient.get("/products", { params }).then((res) => res.data),

  getById: (id) => apiClient.get(`/products/${id}`).then((res) => res.data),

  listMine: () => apiClient.get("/products/mine").then((res) => res.data),

  create: (payload) => apiClient.post("/products", payload).then((res) => {
    invalidateCatalogCache();
    return res.data;
  }),

  update: (id, payload) => apiClient.put(`/products/${id}`, payload).then((res) => {
    invalidateCatalogCache();
    return res.data;
  }),

  approve: (id) => apiClient.post(`/products/${id}/approve`).then((res) => {
    invalidateCatalogCache();
    return res.data;
  }),

  reject: (id) => apiClient.post(`/products/${id}/reject`).then((res) => {
    invalidateCatalogCache();
    return res.data;
  }),

  deactivate: (id) => apiClient.delete(`/products/${id}`).then((res) => {
    invalidateCatalogCache();
    return res.data;
  }),

  uploadImages: (productId, files, onUploadProgress) => {
    const formData = new FormData();
    for (const file of files) {
      formData.append("files", file);
    }
    return apiClient
      .post(`/products/${productId}/images`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress,
      })
      .then((res) => {
        invalidateCatalogCache();
        return res.data;
      });
  },

  getImages: (productId) => apiClient.get(`/products/${productId}/images`).then((res) => res.data),

  deleteImage: (productId, imageId) =>
    apiClient.delete(`/products/${productId}/images/${imageId}`).then((res) => {
      invalidateCatalogCache();
      return res.data;
    }),

  replaceImage: (productId, imageId, file) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient
      .put(`/products/${productId}/images/${imageId}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((res) => {
        invalidateCatalogCache();
        return res.data;
      });
  },

  setPrimaryImage: (productId, imageId) =>
    apiClient.patch(`/products/${productId}/images/${imageId}/primary`).then((res) => {
      invalidateCatalogCache();
      return res.data;
    }),

  addImageUrl: (productId, externalUrl, urlLabel = null) =>
    apiClient
      .post(`/products/${productId}/images/url`, {
        external_url: externalUrl,
        url_label: urlLabel || undefined,
      })
      .then((res) => {
        invalidateCatalogCache();
        return res.data;
      }),
};

export default productService;
