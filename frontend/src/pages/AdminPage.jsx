import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { useAuth } from "@/hooks/useAuth";
import productService from "@/services/productService";
import categoryService from "@/services/categoryService";
import Spinner from "@/components/Spinner";
import EmptyState from "@/components/EmptyState";
import { getApiErrorMessage } from "@/utils/errorUtils";

const CERTIFICATION_TABS = [
  { id: "PENDING", label: "Pending Queue" },
  { id: "APPROVED", label: "Approved Products" },
  { id: "REJECTED", label: "Rejected Products" },
  { id: "ALL", label: "All Products" },
];

export default function AdminPage() {
  const { user } = useAuth();

  // Stats state
  const [counts, setCounts] = useState({ pending: 0, approved: 0, rejected: 0 });
  const [isStatsLoading, setIsStatsLoading] = useState(true);

  // Queue state
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [categoryMap, setCategoryMap] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [updatingProductId, setUpdatingProductId] = useState(null);

  // Filters state
  const [activeTab, setActiveTab] = useState("PENDING");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");

  // Modal / Detail inspection state
  const [previewProduct, setPreviewProduct] = useState(null);

  // Fetch summary counts
  const loadCounts = useCallback(async () => {
    setIsStatsLoading(true);
    try {
      const [pendingRes, approvedRes, rejectedRes] = await Promise.all([
        productService.list({ certification: "PENDING", page: 1, page_size: 1 }),
        productService.list({ certification: "APPROVED", page: 1, page_size: 1 }),
        productService.list({ certification: "REJECTED", page: 1, page_size: 1 }),
      ]);

      const getCount = (res) =>
        typeof res?.total === "number"
          ? res.total
          : Array.isArray(res?.items)
          ? res.items.length
          : Array.isArray(res)
          ? res.length
          : 0;

      setCounts({
        pending: getCount(pendingRes),
        approved: getCount(approvedRes),
        rejected: getCount(rejectedRes),
      });
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not refresh dashboard statistics."));
    } finally {
      setIsStatsLoading(false);
    }
  }, []);

  // Fetch categories taxonomy
  const loadCategories = useCallback(async () => {
    try {
      const data = await categoryService.list(true);
      const list = Array.isArray(data) ? data : [];
      setCategories(list);
      const map = {};
      list.forEach((c) => {
        map[c.id] = c.name;
      });
      setCategoryMap(map);
    } catch {
      // Non-critical background load
    }
  }, []);

  // Fetch products queue based on current filters
  const loadProducts = useCallback(async () => {
    setIsLoading(true);
    try {
      const params = { page: 1, page_size: 50 };
      if (activeTab !== "ALL") {
        params.certification = activeTab;
      }
      if (searchQuery.trim()) {
        const queryStr = searchQuery.trim();
        if (/^\d+$/.test(queryStr)) {
          params.seller_id = parseInt(queryStr, 10);
        } else {
          params.search = queryStr;
        }
      }
      if (selectedCategory) {
        params.category_id = parseInt(selectedCategory, 10);
      }

      const res = await productService.list(params);
      const items = Array.isArray(res?.items) ? res.items : Array.isArray(res) ? res : [];
      setProducts(items);
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not load certification queue."));
    } finally {
      setIsLoading(false);
    }
  }, [activeTab, searchQuery, selectedCategory]);

  useEffect(() => {
    loadCounts();
    loadCategories();
  }, [loadCounts, loadCategories]);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  // Handle Approve / Reject actions
  const handleDecision = async (product, action) => {
    if (updatingProductId !== null) return;
    setUpdatingProductId(product.id);
    try {
      if (action === "approve") {
        await productService.approve(product.id);
        toast.success(`Product "${product.name}" approved successfully.`);
      } else {
        await productService.reject(product.id);
        toast.success(`Product "${product.name}" rejected.`);
      }
      if (previewProduct?.id === product.id) {
        setPreviewProduct(null);
      }
      await Promise.all([loadProducts(), loadCounts()]);
    } catch (err) {
      toast.error(getApiErrorMessage(err, `Could not ${action} product.`));
    } finally {
      setUpdatingProductId(null);
    }
  };

  const getCertificationBadge = (status) => {
    const norm = String(status || "PENDING").toUpperCase();
    if (norm === "APPROVED") {
      return (
        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-800 border border-emerald-200">
          ✓ Approved
        </span>
      );
    }
    if (norm === "REJECTED") {
      return (
        <span className="inline-flex items-center gap-1 rounded-full bg-rose-50 px-2.5 py-0.5 text-xs font-semibold text-rose-800 border border-rose-200">
          ✕ Rejected
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-semibold text-amber-800 border border-amber-200">
        ⏳ Pending
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header Banner - Clean White & Organic Green */}
      <div className="bg-white border border-emerald-100/90 shadow-sm p-6 rounded-2xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex items-start gap-3.5">
            <div className="h-11 w-11 rounded-2xl bg-emerald-100 text-emerald-800 flex items-center justify-center text-xl shrink-0 shadow-sm">
              🌿
            </div>
            <div>
              <h1 className="font-display text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="mt-1 text-sm text-gray-600 max-w-2xl">
                Welcome, <span className="font-semibold text-emerald-800">{user?.full_name || "Administrator"}</span>. Manage organic product certifications, audit seller submissions, and govern the catalog taxonomy.
              </p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2.5 shrink-0">
            <Link
              to="/admin/categories"
              className="inline-flex items-center gap-1.5 bg-white border border-emerald-600 text-emerald-700 hover:bg-emerald-50 text-xs font-semibold px-4 py-2 rounded-xl transition shadow-sm"
            >
              📂 Manage Categories
            </Link>
            <Link
              to="/products"
              className="inline-flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-4 py-2 rounded-xl transition shadow-sm"
            >
              🛍️ View Storefront
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Pending Card */}
        <div
          onClick={() => setActiveTab("PENDING")}
          className={`bg-white border border-amber-200/80 shadow-sm p-5 rounded-2xl cursor-pointer transition-all hover:shadow-md border-l-4 border-l-amber-500 ${
            activeTab === "PENDING" ? "ring-2 ring-amber-400 bg-amber-50/20" : ""
          }`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-amber-800">Pending Review</p>
              <h2 className="text-3xl font-extrabold text-gray-900 mt-1">
                {isStatsLoading ? "…" : counts.pending}
              </h2>
              <p className="text-xs text-gray-500 mt-1">Awaiting quality approval</p>
            </div>
            <div className="h-12 w-12 rounded-2xl bg-amber-50 text-amber-700 border border-amber-200 flex items-center justify-center text-xl font-bold">
              ⏳
            </div>
          </div>
        </div>

        {/* Approved Card */}
        <div
          onClick={() => setActiveTab("APPROVED")}
          className={`bg-white border border-emerald-200/80 shadow-sm p-5 rounded-2xl cursor-pointer transition-all hover:shadow-md border-l-4 border-l-emerald-500 ${
            activeTab === "APPROVED" ? "ring-2 ring-emerald-500 bg-emerald-50/20" : ""
          }`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-emerald-800">Approved Products</p>
              <h2 className="text-3xl font-extrabold text-gray-900 mt-1">
                {isStatsLoading ? "…" : counts.approved}
              </h2>
              <p className="text-xs text-gray-500 mt-1">Active in public catalog</p>
            </div>
            <div className="h-12 w-12 rounded-2xl bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center justify-center text-xl font-bold">
              ✓
            </div>
          </div>
        </div>

        {/* Rejected Card */}
        <div
          onClick={() => setActiveTab("REJECTED")}
          className={`bg-white border border-rose-200/80 shadow-sm p-5 rounded-2xl cursor-pointer transition-all hover:shadow-md border-l-4 border-l-rose-500 ${
            activeTab === "REJECTED" ? "ring-2 ring-rose-400 bg-rose-50/20" : ""
          }`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-rose-800">Rejected Submissions</p>
              <h2 className="text-3xl font-extrabold text-gray-900 mt-1">
                {isStatsLoading ? "…" : counts.rejected}
              </h2>
              <p className="text-xs text-gray-500 mt-1">Standards not met</p>
            </div>
            <div className="h-12 w-12 rounded-2xl bg-rose-50 text-rose-700 border border-rose-200 flex items-center justify-center text-xl font-bold">
              ✕
            </div>
          </div>
        </div>
      </div>

      {/* Certification Queue Card */}
      <div className="bg-white border border-emerald-100/90 shadow-sm p-6 rounded-2xl space-y-5">
        {/* Navigation Tabs */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-100 pb-4">
          <div className="flex gap-1.5 overflow-x-auto">
            {CERTIFICATION_TABS.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-xl text-xs font-semibold transition shrink-0 ${
                  activeTab === tab.id
                    ? "bg-emerald-700 text-white shadow-sm"
                    : "bg-gray-100 text-gray-700 hover:bg-emerald-50 hover:text-emerald-800"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <button
            type="button"
            onClick={() => Promise.all([loadProducts(), loadCounts()])}
            className="text-xs font-semibold text-emerald-800 hover:text-emerald-950 flex items-center gap-1.5 bg-emerald-50 px-3 py-1.5 rounded-xl border border-emerald-200/80 transition"
          >
            🔄 Refresh Queue
          </button>
        </div>

        {/* Filter Controls Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search product name or Seller ID…"
              className="w-full rounded-xl border border-gray-200 bg-white pl-9 pr-4 py-2.5 text-xs text-gray-900 shadow-sm placeholder:text-gray-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-100 transition"
            />
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-xs">🔍</span>
          </div>

          <div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-xs text-gray-900 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-100 transition"
            >
              <option value="">All Categories</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} {!c.is_active ? "(Inactive)" : ""}
                </option>
              ))}
            </select>
          </div>

          {(searchQuery || selectedCategory) && (
            <div className="flex items-center">
              <button
                type="button"
                onClick={() => {
                  setSearchQuery("");
                  setSelectedCategory("");
                }}
                className="text-xs text-rose-600 hover:text-rose-800 font-semibold underline"
              >
                Clear Filters
              </button>
            </div>
          )}
        </div>

        {/* Queue Items */}
        {isLoading ? (
          <div className="py-12">
            <Spinner label="Loading certification queue…" />
          </div>
        ) : products.length === 0 ? (
          <EmptyState
            title="No products found"
            description={
              searchQuery || selectedCategory
                ? "No product submissions match your selected search or category filters."
                : `There are currently no products with status "${activeTab}".`
            }
          />
        ) : (
          <div className="space-y-3">
            {products.map((product) => (
              <div
                key={product.id}
                className="rounded-2xl border border-gray-200/80 hover:border-emerald-300 bg-white p-4 shadow-sm hover:shadow transition"
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  {/* Left Product Info */}
                  <div className="flex items-start gap-3.5">
                    {/* Image Thumbnail */}
                    <div className="h-16 w-16 shrink-0 rounded-xl overflow-hidden bg-gray-50 border border-gray-200/80 flex items-center justify-center">
                      {product.image_url ? (
                        <img
                          src={product.image_url}
                          alt={product.name}
                          className="h-full w-full object-cover"
                          onError={(e) => {
                            e.target.style.display = "none";
                            e.target.nextSibling.style.display = "flex";
                          }}
                        />
                      ) : null}
                      <span
                        className="text-xl"
                        style={{ display: product.image_url ? "none" : "flex" }}
                      >
                        🥬
                      </span>
                    </div>

                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="font-display font-semibold text-gray-900">{product.name}</h3>
                        {getCertificationBadge(product.certification)}
                      </div>

                      <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-500">
                        <span>Category: <strong className="text-gray-700">{categoryMap[product.category_id] || `ID ${product.category_id}`}</strong></span>
                        <span>•</span>
                        <span>Seller ID: <strong className="text-gray-700">{product.seller_id}</strong></span>
                        <span>•</span>
                        <span>Stock: <strong className="text-gray-700">{product.stock_quantity} {product.unit}</strong></span>
                        <span>•</span>
                        <span>Price: <strong className="text-emerald-700 font-bold">₹{Number(product.price).toFixed(2)}</strong></span>
                      </div>

                      {product.description && (
                        <p className="mt-1 text-xs text-gray-600 line-clamp-1 max-w-2xl">{product.description}</p>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 shrink-0 self-end md:self-center">
                    <button
                      type="button"
                      onClick={() => setPreviewProduct(product)}
                      className="border border-emerald-600 text-emerald-700 hover:bg-emerald-50 text-xs font-semibold px-3 py-1.5 rounded-xl transition"
                    >
                      🔍 Inspect
                    </button>

                    {product.certification !== "APPROVED" && (
                      <button
                        type="button"
                        onClick={() => handleDecision(product, "approve")}
                        disabled={updatingProductId !== null}
                        className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-3.5 py-1.5 rounded-xl shadow-sm transition disabled:opacity-50"
                      >
                        {updatingProductId === product.id ? "Updating…" : "Approve"}
                      </button>
                    )}

                    {product.certification !== "REJECTED" && (
                      <button
                        type="button"
                        onClick={() => handleDecision(product, "reject")}
                        disabled={updatingProductId !== null}
                        className="border border-rose-300 text-rose-700 hover:bg-rose-50 text-xs font-semibold px-3.5 py-1.5 rounded-xl transition disabled:opacity-50"
                      >
                        Reject
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Product Detail Preview Modal */}
      {previewProduct && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
          <div className="bg-white border border-emerald-100 shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto space-y-4 rounded-2xl p-6 animate-in fade-in zoom-in-95">
            <div className="flex items-start justify-between border-b border-gray-100 pb-3">
              <div>
                <span className="text-xs font-semibold text-emerald-800 uppercase tracking-wider">Product Inspection</span>
                <h2 className="font-display text-xl font-bold text-gray-900 mt-0.5">{previewProduct.name}</h2>
              </div>
              <button
                type="button"
                onClick={() => setPreviewProduct(null)}
                className="text-gray-400 hover:text-gray-600 text-lg font-bold p-1 rounded-lg"
              >
                ✕
              </button>
            </div>

            {/* Modal Image */}
            <div className="h-48 w-full rounded-xl overflow-hidden bg-gray-50 border border-gray-200 flex items-center justify-center">
              {previewProduct.image_url ? (
                <img
                  src={previewProduct.image_url}
                  alt={previewProduct.name}
                  className="h-full w-full object-cover"
                  onError={(e) => {
                    e.target.style.display = "none";
                    e.target.nextSibling.style.display = "flex";
                  }}
                />
              ) : null}
              <span className="text-4xl" style={{ display: previewProduct.image_url ? "none" : "flex" }}>
                🥬
              </span>
            </div>

            {/* Metadata Grid */}
            <div className="grid grid-cols-2 gap-3 text-xs bg-emerald-50/40 p-3.5 rounded-xl border border-emerald-100/80">
              <div>
                <span className="text-gray-500">Certification Status:</span>
                <div className="mt-0.5">{getCertificationBadge(previewProduct.certification)}</div>
              </div>
              <div>
                <span className="text-gray-500">Category:</span>
                <p className="font-semibold text-gray-800">{categoryMap[previewProduct.category_id] || previewProduct.category_id}</p>
              </div>
              <div>
                <span className="text-gray-500">Price & Unit:</span>
                <p className="font-bold text-emerald-800">₹{Number(previewProduct.price).toFixed(2)} per {previewProduct.unit}</p>
              </div>
              <div>
                <span className="text-gray-500">Available Stock:</span>
                <p className="font-semibold text-gray-800">{previewProduct.stock_quantity} units</p>
              </div>
              <div>
                <span className="text-gray-500">Seller User ID:</span>
                <p className="font-semibold text-gray-800">{previewProduct.seller_id}</p>
              </div>
              <div>
                <span className="text-gray-500">Listed Date:</span>
                <p className="font-semibold text-gray-800">
                  {previewProduct.created_at ? new Date(previewProduct.created_at).toLocaleDateString() : "N/A"}
                </p>
              </div>
            </div>

            {/* Description */}
            <div>
              <span className="text-xs font-semibold text-gray-700">Product Description</span>
              <p className="mt-1 text-xs text-gray-600 bg-white p-3 rounded-xl border border-gray-200 leading-relaxed">
                {previewProduct.description || "No description provided by vendor."}
              </p>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-end gap-2 pt-3 border-t border-gray-100">
              <button
                type="button"
                onClick={() => setPreviewProduct(null)}
                className="border border-gray-200 text-gray-700 hover:bg-gray-50 text-xs font-semibold px-4 py-2 rounded-xl transition"
              >
                Close
              </button>

              {previewProduct.certification !== "APPROVED" && (
                <button
                  type="button"
                  onClick={() => handleDecision(previewProduct, "approve")}
                  disabled={updatingProductId !== null}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-4 py-2 rounded-xl shadow-sm transition disabled:opacity-50"
                >
                  {updatingProductId === previewProduct.id ? "Updating…" : "Approve Product"}
                </button>
              )}

              {previewProduct.certification !== "REJECTED" && (
                <button
                  type="button"
                  onClick={() => handleDecision(previewProduct, "reject")}
                  disabled={updatingProductId !== null}
                  className="border border-rose-300 text-rose-700 hover:bg-rose-50 text-xs font-semibold px-4 py-2 rounded-xl transition disabled:opacity-50"
                >
                  Reject Product
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
