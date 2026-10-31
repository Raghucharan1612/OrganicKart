import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate, useParams, useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";
import { useAuth } from "@/hooks/useAuth";
import productService from "@/services/productService";
import categoryService from "@/services/categoryService";
import orderService from "@/services/orderService";
import ProductForm from "@/features/catalog/components/ProductForm";
import ImageUploadManager from "@/components/vendor/ImageUploadManager";
import { getProductImageUrl } from "@/utils/imageUtils";
import { getApiErrorMessage } from "@/utils/errorUtils";
import Spinner from "@/components/Spinner";
import EmptyState from "@/components/EmptyState";
import Button from "@/components/Button";

export default function SellerDashboardPage({ defaultTab = null }) {
  const { user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const params = useParams();
  const [searchParams, setSearchParams] = useSearchParams();

  // Active Tab state: 'overview' | 'products' | 'add' | 'edit'
  const initialTab =
    defaultTab ||
    searchParams.get("tab") ||
    (location.pathname.includes("/new")
      ? "add"
      : location.pathname.includes("/edit")
      ? "edit"
      : location.pathname.includes("/products")
      ? "products"
      : "overview");

  const [activeTab, setActiveTab] = useState(initialTab);

  // Data states
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [sellerOrders, setSellerOrders] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);

  // Edit product selection
  const [editingProductId, setEditingProductId] = useState(
    params.id ? Number(params.id) : searchParams.get("id") ? Number(searchParams.get("id")) : null
  );

  // Deactivation confirmation modal
  const [deactivatingProduct, setDeactivatingProduct] = useState(null);
  const [isDeactivating, setIsDeactivating] = useState(false);

  // Standalone image manager modal for a specific product
  const [imageModalProduct, setImageModalProduct] = useState(null);

  // Filter & Search states in My Products
  const [productSearch, setProductSearch] = useState("");
  const [selectedCategoryFilter, setSelectedCategoryFilter] = useState("ALL");
  const [selectedStatusFilter, setSelectedStatusFilter] = useState("ALL"); // ALL | APPROVED | PENDING | REJECTED | DEACTIVATED

  const isFarmer = user?.role === "FARMER";
  const roleTitle = isFarmer ? "Farmer Dashboard" : "Vendor Dashboard";
  const roleBadgeText = isFarmer ? "Verified Organic Farmer" : "Verified Organic Vendor";
  const subtitleText = isFarmer
    ? "Welcome back, farmer! Manage your organic harvests, store listings, images, and orders."
    : "Welcome back, vendor! Manage your organic catalog, product images, inventory, and orders.";

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [productsData, categoriesData, ordersData, analyticsData] = await Promise.all([
        productService.listMine(),
        categoryService.list(),
        orderService.getSellerOrders().catch(() => []),
        orderService.getSellerAnalytics().catch(() => null),
      ]);
      setProducts(Array.isArray(productsData) ? productsData : []);
      setCategories(Array.isArray(categoriesData) ? categoriesData : []);
      setSellerOrders(Array.isArray(ordersData) ? ordersData : []);
      setAnalytics(analyticsData || null);
    } catch (err) {
      const msg = getApiErrorMessage(err, "Could not load vendor dashboard data.");
      setError(msg);
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Sync tab if URL changes
  useEffect(() => {
    if (defaultTab) {
      setActiveTab(defaultTab);
    } else {
      const tabParam = searchParams.get("tab");
      if (tabParam && ["overview", "products", "add", "edit"].includes(tabParam)) {
        setActiveTab(tabParam);
      }
    }
  }, [defaultTab, searchParams]);

  // Tab switch handler
  const handleTabChange = (tab, productId = null) => {
    setActiveTab(tab);
    if (tab === "edit" && productId) {
      setEditingProductId(productId);
      setSearchParams({ tab: "edit", id: String(productId) });
    } else {
      setSearchParams({ tab });
    }
  };

  // Compute live product & order metrics
  const stats = useMemo(() => {
    const totalCount = products.length;
    const activeCount = products.filter((p) => p.is_active).length;
    const pendingCount = products.filter((p) => p.certification === "PENDING").length;
    const approvedCount = products.filter((p) => p.certification === "APPROVED").length;
    const rejectedCount = products.filter((p) => p.certification === "REJECTED").length;
    const lowStockCount = products.filter((p) => Number(p.stock_quantity || 0) <= 10).length;

    const totalOrdersCount = analytics?.total_orders ?? sellerOrders.length;
    const rawRevenue = analytics?.total_revenue != null ? Number(analytics.total_revenue) : 0;
    const formattedRevenue = `₹${rawRevenue.toFixed(2)}`;

    return {
      total: totalCount,
      active: activeCount,
      pending: pendingCount,
      approved: approvedCount,
      rejected: rejectedCount,
      lowStock: lowStockCount,
      orders: totalOrdersCount,
      revenue: formattedRevenue,
    };
  }, [products, sellerOrders, analytics]);

  // Category inventory distribution (strictly organic green/teal/amber/lime tones — no purple/indigo/violet)
  const categoryInventory = useMemo(() => {
    if (products.length === 0) return [];

    const categoryMap = {};
    products.forEach((p) => {
      const catName = p.category?.name || "Uncategorized";
      if (!categoryMap[catName]) {
        categoryMap[catName] = { count: 0, totalStock: 0 };
      }
      categoryMap[catName].count += 1;
      categoryMap[catName].totalStock += Number(p.stock_quantity || 0);
    });

    const organicColors = ["bg-emerald-500", "bg-teal-500", "bg-lime-500", "bg-green-600", "bg-amber-500"];
    const totalProducts = products.length;

    return Object.entries(categoryMap).map(([name, data], idx) => {
      const share = Math.round((data.count / totalProducts) * 100);
      return {
        name,
        share,
        count: `${data.count} product${data.count > 1 ? "s" : ""}`,
        stock: `${data.totalStock} units`,
        color: organicColors[idx % organicColors.length],
      };
    });
  }, [products]);

  // Filtered products list for "My Products" section
  const filteredProducts = useMemo(() => {
    return products.filter((p) => {
      const matchesSearch =
        !productSearch.trim() ||
        p.name.toLowerCase().includes(productSearch.toLowerCase()) ||
        p.category?.name?.toLowerCase().includes(productSearch.toLowerCase());

      const matchesCategory =
        selectedCategoryFilter === "ALL" || String(p.category_id) === String(selectedCategoryFilter);

      let matchesStatus = true;
      if (selectedStatusFilter === "APPROVED") matchesStatus = p.certification === "APPROVED" && p.is_active;
      else if (selectedStatusFilter === "PENDING") matchesStatus = p.certification === "PENDING";
      else if (selectedStatusFilter === "REJECTED") matchesStatus = p.certification === "REJECTED";
      else if (selectedStatusFilter === "DEACTIVATED") matchesStatus = !p.is_active;

      return matchesSearch && matchesCategory && matchesStatus;
    });
  }, [products, productSearch, selectedCategoryFilter, selectedStatusFilter]);

  // Find currently editing product
  const editingProduct = useMemo(() => {
    if (!editingProductId) return null;
    return products.find((p) => p.id === editingProductId) || null;
  }, [products, editingProductId]);

  // Handle Product Creation + Image Upload
  const handleCreateProduct = async (payload, pendingFiles, pendingPrimaryIndex, pendingUrls = []) => {
    setIsSaving(true);
    try {
      const created = await productService.create(payload);
      const newProductId = created.id;

      // Upload selected pending images
      if (pendingFiles && pendingFiles.length > 0) {
        toast.loading("Uploading product photos...", { id: "upload-toast" });
        const uploadedImages = await productService.uploadImages(newProductId, pendingFiles);
        if (pendingPrimaryIndex > 0 && uploadedImages[pendingPrimaryIndex]) {
          await productService.setPrimaryImage(newProductId, uploadedImages[pendingPrimaryIndex].id);
        }
        toast.dismiss("upload-toast");
      }
      for (const imageUrl of pendingUrls) {
        await productService.addImageUrl(newProductId, imageUrl);
      }

      toast.success("Product created! Submitted for organic verification.");
      await loadData();
      handleTabChange("products");
    } catch (err) {
      toast.dismiss("upload-toast");
      toast.error(getApiErrorMessage(err, "Failed to create product."));
    } finally {
      setIsSaving(false);
    }
  };

  // Handle Product Update
  const handleUpdateProduct = async (payload) => {
    if (!editingProductId) return;
    setIsSaving(true);
    try {
      await productService.update(editingProductId, payload);
      toast.success("Product details updated and re-submitted for verification.");
      await loadData();
      handleTabChange("products");
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Failed to update product."));
    } finally {
      setIsSaving(false);
    }
  };

  // Handle Deactivation Confirmation
  const confirmDeactivate = async () => {
    if (!deactivatingProduct) return;
    setIsDeactivating(true);
    try {
      await productService.deactivate(deactivatingProduct.id);
      toast.success("Product deactivated.");
      setDeactivatingProduct(null);
      await loadData();
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not deactivate product."));
    } finally {
      setIsDeactivating(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-800">
      {/* Top Header & Navigation Banner */}
      <div className="bg-white border-b border-slate-200 shadow-2xs sticky top-0 z-20">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-10 2xl:px-12 flex flex-col md:flex-row md:items-center md:justify-between py-3 gap-3">
          {/* Title & Badge */}
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-xl shrink-0">
              🌿
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-display text-lg sm:text-xl font-bold text-slate-900">{roleTitle}</h1>
                <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-800 border border-emerald-200">
                  {roleBadgeText}
                </span>
              </div>
              <p className="text-[11px] text-slate-500 hidden sm:block">{subtitleText}</p>
            </div>
          </div>

          {/* Quick Tab Switcher */}
          <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-hide py-1">
            <button
              type="button"
              onClick={() => handleTabChange("overview")}
              className={`px-3.5 py-1.5 text-xs font-semibold rounded-xl transition-all whitespace-nowrap ${
                activeTab === "overview"
                  ? "bg-emerald-600 text-white shadow-2xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              }`}
            >
              Overview
            </button>
            <button
              type="button"
              onClick={() => handleTabChange("products")}
              className={`px-3.5 py-1.5 text-xs font-semibold rounded-xl transition-all whitespace-nowrap flex items-center gap-1.5 ${
                activeTab === "products"
                  ? "bg-emerald-600 text-white shadow-2xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              }`}
            >
              <span>My Products</span>
              <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
                activeTab === "products" ? "bg-white/20 text-white" : "bg-slate-200 text-slate-700"
              }`}>
                {products.length}
              </span>
            </button>
            <button
              type="button"
              onClick={() => handleTabChange("add")}
              className={`px-3.5 py-1.5 text-xs font-semibold rounded-xl transition-all whitespace-nowrap ${
                activeTab === "add"
                  ? "bg-emerald-600 text-white shadow-2xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              }`}
            >
              + Add Product
            </button>
            {activeTab === "edit" && (
              <button
                type="button"
                className="px-3.5 py-1.5 text-xs font-semibold rounded-xl bg-emerald-600 text-white shadow-2xs whitespace-nowrap"
              >
                Edit Product
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Container */}
      <div className="w-full px-4 py-6 sm:px-6 lg:px-8 xl:px-10 2xl:px-12 space-y-6">
        {/* Error notification banner */}
        {error && (
          <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800 flex items-center justify-between">
            <span>⚠️ {error}</span>
            <button
              type="button"
              onClick={loadData}
              className="ml-4 font-semibold text-rose-700 underline hover:text-rose-900"
            >
              Retry
            </button>
          </div>
        )}

        {/* Global Loading state */}
        {isLoading ? (
          <div className="py-20 text-center">
            <Spinner label="Loading vendor dashboard..." />
          </div>
        ) : (
          <>
            {/* ============================================================== */}
            {/* SECTION 1: OVERVIEW */}
            {/* ============================================================== */}
            {activeTab === "overview" && (
              <div className="space-y-6 animate-fade-in">
                {/* KPI Metrics Grid */}
                <section className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
                  <div className="bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-4 sm:p-5 flex flex-col justify-between">
                    <div>
                      <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Total Products</span>
                      <p className="text-2xl font-extrabold text-slate-900 mt-2">{stats.total}</p>
                    </div>
                    <p className="text-xs text-slate-400 mt-2">Listed in catalog</p>
                  </div>

                  <div className="bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-4 sm:p-5 flex flex-col justify-between">
                    <div>
                      <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Active</span>
                      <p className="text-2xl font-extrabold text-emerald-700 mt-2">{stats.active}</p>
                    </div>
                    <p className="text-xs text-emerald-600 font-medium mt-2">Live on store</p>
                  </div>

                  <div className="bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-4 sm:p-5 flex flex-col justify-between">
                    <div>
                      <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Pending Quality Audit</span>
                      <p className="text-2xl font-extrabold text-amber-600 mt-2">{stats.pending}</p>
                    </div>
                    <p className="text-xs text-amber-600 font-medium mt-2">Under verification</p>
                  </div>

                  <div className="bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-4 sm:p-5 flex flex-col justify-between">
                    <div>
                      <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Low Stock</span>
                      <p className="text-2xl font-extrabold text-rose-600 mt-2">{stats.lowStock}</p>
                    </div>
                    <p className="text-xs text-slate-400 mt-2">&le; 10 units</p>
                  </div>

                  <div className="bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-4 sm:p-5 flex flex-col justify-between">
                    <div>
                      <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Orders</span>
                      <p className="text-2xl font-extrabold text-slate-900 mt-2">{stats.orders}</p>
                    </div>
                    <p className="text-xs text-slate-400 mt-2">Customer orders</p>
                  </div>

                  <div className="bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-4 sm:p-5 flex flex-col justify-between">
                    <div>
                      <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Revenue</span>
                      <p className="text-2xl font-extrabold text-emerald-700 mt-2">{stats.revenue}</p>
                    </div>
                    <p className="text-xs text-emerald-600 font-medium mt-2">Organic earnings</p>
                  </div>
                </section>

                {/* Row: Quality Status & Category Breakdown */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                  {/* Organic Certification Audit Summary */}
                  <div className="lg:col-span-5 bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-5 sm:p-6 space-y-4">
                    <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                      <div>
                        <h2 className="font-display text-base font-bold text-slate-900">Approval &amp; Quality Audit</h2>
                        <p className="text-xs text-slate-500">Official organic compliance verification</p>
                      </div>
                      <span className="rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-800 border border-emerald-200">
                        NPOP Compliant
                      </span>
                    </div>

                    <div className="divide-y divide-slate-100 text-xs">
                      <div className="flex justify-between py-2.5">
                        <span className="text-slate-600 font-medium flex items-center gap-2">
                          <span className="h-2 w-2 rounded-full bg-emerald-500" /> Approved for Customers
                        </span>
                        <span className="font-bold text-emerald-700">{stats.approved} products</span>
                      </div>
                      <div className="flex justify-between py-2.5">
                        <span className="text-slate-600 font-medium flex items-center gap-2">
                          <span className="h-2 w-2 rounded-full bg-amber-500" /> Pending Admin Audit
                        </span>
                        <span className="font-bold text-amber-600">{stats.pending} products</span>
                      </div>
                      <div className="flex justify-between py-2.5">
                        <span className="text-slate-600 font-medium flex items-center gap-2">
                          <span className="h-2 w-2 rounded-full bg-rose-500" /> Needs Revision / Rejected
                        </span>
                        <span className="font-bold text-rose-600">{stats.rejected} products</span>
                      </div>
                    </div>

                    <div className="pt-2">
                      <button
                        type="button"
                        onClick={() => handleTabChange("add")}
                        className="w-full py-2.5 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-semibold border border-emerald-200 transition text-center"
                      >
                        + Submit New Organic Harvest / Product
                      </button>
                    </div>
                  </div>

                  {/* Category Inventory Breakdown */}
                  <div className="lg:col-span-7 bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-5 sm:p-6 space-y-4">
                    <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                      <h2 className="font-display text-base font-bold text-slate-900">Inventory by Category</h2>
                      <span className="text-xs text-slate-400 font-medium">{products.length} Total Items</span>
                    </div>

                    {categoryInventory.length === 0 ? (
                      <p className="text-xs text-slate-500 text-center py-8">No inventory listed yet.</p>
                    ) : (
                      <div className="space-y-3.5">
                        {categoryInventory.map((cat) => (
                          <div key={cat.name} className="space-y-1">
                            <div className="flex items-center justify-between text-xs">
                              <span className="font-semibold text-slate-800">{cat.name}</span>
                              <span className="text-slate-500 font-medium">{cat.stock} &bull; {cat.count}</span>
                            </div>
                            <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                              <div style={{ width: `${cat.share}%` }} className={`h-full ${cat.color} rounded-full`} />
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Quick Products Preview */}
                <div className="bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-5 sm:p-6 space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="font-display text-base font-bold text-slate-900">Recent Products</h2>
                      <p className="text-xs text-slate-500">Overview of your latest catalog entries</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleTabChange("products")}
                      className="text-xs font-semibold text-emerald-700 hover:underline"
                    >
                      View All Products ({products.length}) &rarr;
                    </button>
                  </div>

                  {products.length === 0 ? (
                    <EmptyState
                      title="No products yet"
                      description="Add your first organic product with photos to start selling."
                      action={
                        <button
                          type="button"
                          onClick={() => handleTabChange("add")}
                          className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-2xs transition"
                        >
                          + Add Product
                        </button>
                      }
                    />
                  ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                      {products.slice(0, 4).map((p) => (
                        <div
                          key={p.id}
                          className="rounded-xl border border-slate-200/80 bg-white p-3 shadow-2xs hover:border-emerald-300 transition flex flex-col justify-between"
                        >
                          <div className="space-y-2.5">
                            <div className="h-32 w-full rounded-lg bg-emerald-50/50 border border-slate-100 overflow-hidden relative">
                              <img
                                src={getProductImageUrl(p.image_url)}
                                alt={p.name}
                                className="h-full w-full object-cover"
                                onError={(e) => {
                                  e.currentTarget.src = "/images/product-placeholder.svg";
                                }}
                              />
                              <span className={`absolute top-2 right-2 text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                                p.certification === "APPROVED"
                                  ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                                  : p.certification === "REJECTED"
                                  ? "bg-rose-50 text-rose-800 border-rose-200"
                                  : "bg-amber-50 text-amber-800 border-amber-200"
                              }`}>
                                {p.certification || "PENDING"}
                              </span>
                            </div>

                            <div>
                              <p className="text-[11px] font-semibold text-emerald-800">{p.category?.name || "Organic"}</p>
                              <h4 className="text-xs font-bold text-slate-900 line-clamp-1">{p.name}</h4>
                              <p className="text-xs font-extrabold text-emerald-700 mt-1">
                                ₹{Number(p.price).toFixed(2)} <span className="text-[10px] font-normal text-slate-500">/ {p.unit}</span>
                              </p>
                            </div>
                          </div>

                          <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                            <span className="text-[11px] text-slate-500">{p.stock_quantity} in stock</span>
                            <button
                              type="button"
                              onClick={() => handleTabChange("edit", p.id)}
                              className="font-semibold text-emerald-700 hover:underline"
                            >
                              Edit &rarr;
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* ============================================================== */}
            {/* SECTION 2: MY PRODUCTS */}
            {/* ============================================================== */}
            {activeTab === "products" && (
              <div className="space-y-5 animate-fade-in">
                {/* Section Header & Search/Filters */}
                <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-2xs space-y-4">
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                    <div>
                      <h2 className="font-display text-lg font-bold text-slate-900">My Product Catalog</h2>
                      <p className="text-xs text-slate-500">
                        Manage inventory, prices, photos, and quality certification status
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleTabChange("add")}
                      className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-2xs transition"
                    >
                      + Add New Product
                    </button>
                  </div>

                  {/* Filters Bar */}
                  <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 pt-2 border-t border-slate-100">
                    <div className="sm:col-span-5">
                      <input
                        type="text"
                        placeholder="Search products by name or category..."
                        value={productSearch}
                        onChange={(e) => setProductSearch(e.target.value)}
                        className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs text-slate-800 placeholder-slate-400 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-hidden transition"
                      />
                    </div>

                    <div className="sm:col-span-4">
                      <select
                        value={selectedCategoryFilter}
                        onChange={(e) => setSelectedCategoryFilter(e.target.value)}
                        className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs text-slate-800 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-hidden transition"
                      >
                        <option value="ALL">All Categories</option>
                        {categories.map((c) => (
                          <option key={c.id} value={c.id}>
                            {c.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="sm:col-span-3">
                      <select
                        value={selectedStatusFilter}
                        onChange={(e) => setSelectedStatusFilter(e.target.value)}
                        className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs text-slate-800 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-hidden transition"
                      >
                        <option value="ALL">All Statuses</option>
                        <option value="APPROVED">Approved (Live)</option>
                        <option value="PENDING">Pending Audit</option>
                        <option value="REJECTED">Rejected</option>
                        <option value="DEACTIVATED">Deactivated</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Products Table & Grid */}
                {filteredProducts.length === 0 ? (
                  <EmptyState
                    title={products.length === 0 ? "No products listed yet" : "No matching products found"}
                    description={
                      products.length === 0
                        ? "List your first organic produce item to begin receiving customer orders."
                        : "Try adjusting your search keywords or filter settings."
                    }
                    action={
                      products.length === 0 ? (
                        <button
                          type="button"
                          onClick={() => handleTabChange("add")}
                          className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-2xs transition"
                        >
                          + Add Product
                        </button>
                      ) : null
                    }
                  />
                ) : (
                  <div className="bg-white border border-slate-200/80 rounded-2xl shadow-2xs overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-slate-200/80 text-xs">
                        <thead className="bg-slate-50 font-semibold text-slate-500 uppercase tracking-wider text-left">
                          <tr>
                            <th className="px-4 py-3">Product &amp; Thumbnail</th>
                            <th className="px-4 py-3">Category</th>
                            <th className="px-4 py-3">Price / Unit</th>
                            <th className="px-4 py-3">Available Stock</th>
                            <th className="px-4 py-3">Approval Status</th>
                            <th className="px-4 py-3">Listing</th>
                            <th className="px-4 py-3 text-right">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 bg-white">
                          {filteredProducts.map((p) => {
                            const imageCount = p.images ? p.images.length : p.image_url ? 1 : 0;
                            return (
                              <tr key={p.id} className="hover:bg-slate-50/60 transition">
                                <td className="px-4 py-3">
                                  <div className="flex items-center gap-3">
                                    <div className="h-12 w-12 rounded-xl bg-emerald-50 border border-slate-200 overflow-hidden shrink-0 relative group">
                                      <img
                                        src={getProductImageUrl(p.image_url)}
                                        alt={p.name}
                                        className="h-full w-full object-cover"
                                        onError={(e) => {
                                          e.currentTarget.src = "/images/product-placeholder.svg";
                                        }}
                                      />
                                      {imageCount > 1 && (
                                        <span className="absolute bottom-0.5 right-0.5 bg-black/70 text-white text-[9px] font-bold px-1 rounded">
                                          +{imageCount}
                                        </span>
                                      )}
                                    </div>
                                    <div>
                                      <h4 className="font-bold text-slate-900 line-clamp-1">{p.name}</h4>
                                      <span className="text-[11px] text-slate-400">ID #{p.id}</span>
                                    </div>
                                  </div>
                                </td>

                                <td className="px-4 py-3 text-slate-600 font-medium">
                                  {p.category?.name || "Organic"}
                                </td>

                                <td className="px-4 py-3">
                                  <span className="font-extrabold text-emerald-700">₹{Number(p.price).toFixed(2)}</span>
                                  <span className="text-slate-400 ml-1">/ {p.unit}</span>
                                </td>

                                <td className="px-4 py-3">
                                  <span className={`font-semibold ${Number(p.stock_quantity) <= 10 ? "text-rose-600 font-bold" : "text-slate-700"}`}>
                                    {p.stock_quantity} units
                                  </span>
                                  {Number(p.stock_quantity) <= 10 && (
                                    <span className="ml-1.5 text-[10px] text-rose-600 bg-rose-50 border border-rose-200 px-1.5 py-0.2 rounded font-medium">
                                      Low
                                    </span>
                                  )}
                                </td>

                                <td className="px-4 py-3">
                                  <span
                                    className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[11px] font-semibold border ${
                                      p.certification === "APPROVED"
                                        ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                                        : p.certification === "REJECTED"
                                        ? "bg-rose-50 text-rose-800 border-rose-200"
                                        : "bg-amber-50 text-amber-800 border-amber-200"
                                    }`}
                                  >
                                    {p.certification === "APPROVED" && "✓ "}
                                    {p.certification === "PENDING" && "⏳ "}
                                    {p.certification === "REJECTED" && "✕ "}
                                    {p.certification || "PENDING"}
                                  </span>
                                </td>

                                <td className="px-4 py-3">
                                  <span
                                    className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold border ${
                                      p.is_active
                                        ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                                        : "bg-slate-100 text-slate-600 border-slate-200"
                                    }`}
                                  >
                                    {p.is_active ? "Active" : "Deactivated"}
                                  </span>
                                </td>

                                <td className="px-4 py-3 text-right">
                                  <div className="flex items-center justify-end gap-2">
                                    <button
                                      type="button"
                                      onClick={() => setImageModalProduct(p)}
                                      className="px-2.5 py-1 text-xs font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded-lg border border-emerald-200 transition"
                                    >
                                      Photos
                                    </button>
                                    <button
                                      type="button"
                                      onClick={() => handleTabChange("edit", p.id)}
                                      className="px-2.5 py-1 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition"
                                    >
                                      Edit
                                    </button>
                                    {p.is_active && (
                                      <button
                                        type="button"
                                        onClick={() => setDeactivatingProduct(p)}
                                        className="px-2.5 py-1 text-xs font-semibold text-rose-600 hover:bg-rose-50 rounded-lg transition"
                                      >
                                        Deactivate
                                      </button>
                                    )}
                                  </div>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ============================================================== */}
            {/* SECTION 3: ADD PRODUCT */}
            {/* ============================================================== */}
            {activeTab === "add" && (
              <div className="max-w-4xl mx-auto space-y-5 animate-fade-in">
                <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                  <div>
                    <h2 className="font-display text-xl font-bold text-slate-900">Add New Organic Product</h2>
                    <p className="text-xs text-slate-500">
                      Submit a new harvest or product listing. Once submitted, it enters the admin quality audit queue.
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleTabChange("products")}
                    className="text-xs font-semibold text-slate-600 hover:text-slate-900"
                  >
                    &larr; Back to Products
                  </button>
                </div>

                <div className="rounded-2xl border border-emerald-200 bg-emerald-50/50 p-4 text-xs text-emerald-900 flex items-start gap-2.5">
                  <span className="text-base shrink-0">🌱</span>
                  <div>
                    <span className="font-bold">Organic Transparency Notice:</span> All products require high-quality photos demonstrating clean organic standards. Uploaded photos will be reviewed by administrators alongside the certification document.
                  </div>
                </div>

                <ProductForm
                  categories={categories}
                  onSubmit={handleCreateProduct}
                  onCancel={() => handleTabChange("products")}
                  isSaving={isSaving}
                />
              </div>
            )}

            {/* ============================================================== */}
            {/* SECTION 4: EDIT PRODUCT */}
            {/* ============================================================== */}
            {activeTab === "edit" && (
              <div className="max-w-4xl mx-auto space-y-5 animate-fade-in">
                <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                  <div>
                    <h2 className="font-display text-xl font-bold text-slate-900">Edit Product</h2>
                    <p className="text-xs text-slate-500">
                      Updating price, description, or images will re-submit this item for verification.
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleTabChange("products")}
                    className="text-xs font-semibold text-slate-600 hover:text-slate-900"
                  >
                    &larr; Back to Products
                  </button>
                </div>

                {!editingProduct ? (
                  <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center space-y-3">
                    <p className="text-sm font-semibold text-slate-800">No product selected to edit.</p>
                    <p className="text-xs text-slate-500">Please choose a product from your catalog list.</p>
                    <button
                      type="button"
                      onClick={() => handleTabChange("products")}
                      className="px-4 py-2 rounded-xl bg-emerald-600 text-white text-xs font-semibold"
                    >
                      Browse My Products
                    </button>
                  </div>
                ) : (
                  <>
                    {/* Status notice */}
                    <div className="rounded-2xl border border-amber-200 bg-amber-50/60 p-4 text-xs text-amber-900 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span>🛡️ Current Certification: <strong>{editingProduct.certification || "PENDING"}</strong></span>
                      </div>
                      <span className="text-[11px] text-amber-800">
                        Edits reset approval to PENDING until re-audited.
                      </span>
                    </div>

                    <ProductForm
                      categories={categories}
                      initialValues={editingProduct}
                      onSubmit={handleUpdateProduct}
                      onCancel={() => handleTabChange("products")}
                      isSaving={isSaving}
                      onImagesUpdated={loadData}
                    />
                  </>
                )}
              </div>
            )}
          </>
        )}
      </div>

      {/* Standalone Product Images Modal (when clicking 'Photos' in products table) */}
      {imageModalProduct && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-2xs animate-fade-in">
          <div className="w-full max-w-2xl rounded-2xl bg-white p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="font-display text-base font-bold text-slate-900">
                  Manage Photos: {imageModalProduct.name}
                </h3>
                <p className="text-xs text-slate-500">Upload, remove, replace, or select primary photo</p>
              </div>
              <button
                type="button"
                onClick={() => setImageModalProduct(null)}
                className="h-8 w-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 text-xs font-bold flex items-center justify-center transition"
              >
                ✕
              </button>
            </div>

            <ImageUploadManager
              productId={imageModalProduct.id}
              onImagesUpdated={loadData}
            />

            <div className="pt-2 flex justify-end">
              <button
                type="button"
                onClick={() => setImageModalProduct(null)}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-2xs transition"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}

      {/* In-app Product Deactivation Confirmation Modal */}
      {deactivatingProduct && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-2xs animate-fade-in">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl space-y-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600 text-lg">
                ⚠️
              </div>
              <div>
                <h3 className="font-display text-base font-bold text-slate-900">
                  Deactivate Product?
                </h3>
                <p className="text-xs text-slate-500">
                  {deactivatingProduct.name}
                </p>
              </div>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              Are you sure you want to deactivate this product? It will immediately be hidden from the customer marketplace.
            </p>

            <div className="flex justify-end gap-2.5 pt-2">
              <Button
                variant="secondary"
                onClick={() => setDeactivatingProduct(null)}
                disabled={isDeactivating}
                className="!text-xs"
              >
                Cancel
              </Button>
              <Button
                className="!bg-rose-600 hover:!bg-rose-700 !text-white !text-xs !font-semibold"
                onClick={confirmDeactivate}
                isLoading={isDeactivating}
              >
                Deactivate
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
