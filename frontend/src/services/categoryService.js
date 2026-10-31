import apiClient from "./apiClient";
import { invalidateCatalogCache } from "./productService";

const CATEGORY_CACHE_TTL_MS = 5 * 60_000;
let publicCategoriesCache = null;
let publicCategoriesInFlight = null;

export const invalidateCategoryCache = () => {
  publicCategoriesCache = null;
  publicCategoriesInFlight = null;
  invalidateCatalogCache();
};

const getPublicCategories = () => {
  if (publicCategoriesCache && Date.now() - publicCategoriesCache.createdAt < CATEGORY_CACHE_TTL_MS) {
    return Promise.resolve(publicCategoriesCache.data);
  }
  if (publicCategoriesInFlight) return publicCategoriesInFlight;

  publicCategoriesInFlight = apiClient
    .get("/categories")
    .then((res) => {
      publicCategoriesCache = { data: res.data, createdAt: Date.now() };
      return res.data;
    })
    .finally(() => {
      publicCategoriesInFlight = null;
    });
  return publicCategoriesInFlight;
};

const categoryService = {
  list: (includeInactive = false) =>
    includeInactive
      ? apiClient.get("/categories", { params: { include_inactive: true } }).then((res) => res.data)
      : getPublicCategories(),

  get: (id) => apiClient.get(`/categories/${id}`).then((res) => res.data),

  create: (payload) => apiClient.post("/categories", payload).then((res) => {
    invalidateCategoryCache();
    return res.data;
  }),

  update: (id, payload) => apiClient.put(`/categories/${id}`, payload).then((res) => {
    invalidateCategoryCache();
    return res.data;
  }),

  deactivate: (id) => apiClient.delete(`/categories/${id}`).then((res) => {
    invalidateCategoryCache();
    return res.data;
  }),

  uploadImage: (id, file) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post(`/categories/${id}/image`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then((res) => {
      invalidateCategoryCache();
      return res.data;
    });
  },

  setImageUrl: (id, externalUrl) => apiClient.put(`/categories/${id}/image/url`, { external_url: externalUrl }).then((res) => {
    invalidateCategoryCache();
    return res.data;
  }),

  removeImage: (id) => apiClient.delete(`/categories/${id}/image`).then((res) => {
    invalidateCategoryCache();
    return res.data;
  }),
};

export default categoryService;
