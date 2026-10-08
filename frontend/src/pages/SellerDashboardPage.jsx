import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { useAuth } from "@/hooks/useAuth";
import productService from "@/services/productService";
import orderService from "@/services/orderService";
import Spinner from "@/components/Spinner";
import EmptyState from "@/components/EmptyState";
import SellerSubNav from "@/components/SellerSubNav";
import { getApiErrorMessage } from "@/utils/errorUtils";

export default function SellerDashboardPage() {
  const { user } = useAuth();

  const [products, setProducts] = useState([]);
  const [sellerOrders, setSellerOrders] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  const isFarmer = user?.role === "FARMER";
  const roleTitle = isFarmer ? "Farmer Dashboard" : "Vendor Dashboard";
  const roleBadgeText = isFarmer ? "Verified Organic Farmer" : "Verified Organic Vendor";
  const subtitleText = isFarmer
    ? "Welcome back, farmer! Manage your products, inventory, orders and certification."
    : "Welcome back, vendor! Manage your products, inventory, orders and certification.";

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [productsData, ordersData, analyticsData] = await Promise.all([
        productService.listMine(),
        orderService.getSellerOrders(),
        orderService.getSellerAnalytics(),
      ]);
      setProducts(Array.isArray(productsData) ? productsData : []);
      setSellerOrders(Array.isArray(ordersData) ? ordersData : []);
      setAnalytics(analyticsData || null);
    } catch (err) {
      const msg = getApiErrorMessage(err, "Could not load your seller dashboard.");
      setError(msg);
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Compute live product & order stats directly from Product and Order Services
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

  // Compute real category inventory distribution
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

    const colors = ["bg-emerald-500", "bg-amber-500", "bg-blue-500", "bg-purple-500", "bg-rose-500"];
    const totalProducts = products.length;

    return Object.entries(categoryMap).map(([name, data], idx) => {
      const share = Math.round((data.count / totalProducts) * 100);
      return {
        name,
        share,
        count: `${data.count} product${data.count > 1 ? "s" : ""}`,
        stock: `${data.totalStock} units`,
        color: colors[idx % colors.length],
      };
    });
  }, [products]);

  // Monthly sales summary from real analytics API
  const monthlySalesList = useMemo(() => {
    if (analytics?.monthly_sales_summary && Array.isArray(analytics.monthly_sales_summary)) {
      return analytics.monthly_sales_summary;
    }
    if (analytics?.monthly_orders && analytics?.monthly_revenue) {
      return Object.keys(analytics.monthly_orders).map((m) => ({
        month: m,
        orders: analytics.monthly_orders[m] || 0,
        revenue: analytics.monthly_revenue[m] || 0,
      }));
    }
    return [];
  }, [analytics]);

  // Recent orders list from analytics API or seller orders
  const recentOrdersList = useMemo(() => {
    if (analytics?.recent_order_summary && Array.isArray(analytics.recent_order_summary) && analytics.recent_order_summary.length > 0) {
      return analytics.recent_order_summary;
    }
    return sellerOrders.slice(0, 10).map((ord) => ({
      order_id: ord.id,
      created_at: ord.created_at,
      status: ord.status,
      payment_status: ord.payment_status,
      items_count: ord.items ? ord.items.length : 0,
      seller_revenue: ord.items
        ? ord.items.reduce((acc, item) => acc + Number(item.subtotal || 0), 0)
        : Number(ord.total_amount || 0),
    }));
  }, [analytics, sellerOrders]);

  // Open the floating Vendor AI Assistant
  const handleOpenAiAssistant = () => {
    window.dispatchEvent(new CustomEvent("open-vendor-ai"));
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-800">
      {/* Secondary compact navigation */}
      <SellerSubNav
        activeTab={activeTab}
        onTabChange={setActiveTab}
        pendingCount={stats.pending}
      />

      {/* Main Container */}
      <div className="w-full px-4 py-6 sm:px-6 lg:px-8 xl:px-10 2xl:px-12 space-y-6">

        {/* DASHBOARD HEADER */}
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-5 sm:p-6">
          <div className="space-y-1">
            <div className="flex items-center gap-2.5 flex-wrap">
              <h1 className="font-display text-2xl font-bold text-slate-900">{roleTitle}</h1>
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-800 border border-emerald-200">
                🛡️ {roleBadgeText}
              </span>
            </div>
            <p className="text-xs text-slate-500">
              {subtitleText}
            </p>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2.5 shrink-0">
            <Link
              to="/seller/products"
              className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-4 py-2 shadow-2xs transition"
            >
              <span>+ Add Product</span>
            </Link>
            <button
              type="button"
              onClick={handleOpenAiAssistant}
              className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-white border border-emerald-600 text-emerald-700 hover:bg-emerald-50 text-xs font-semibold px-4 py-2 shadow-2xs transition"
            >
              <span>Ask AI</span>
            </button>
          </div>
        </header>

        {error && (
          <div className="rounded-2xl border border-rose-200 bg-rose-50/80 p-4 text-xs text-rose-800 flex items-center justify-between">
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

        {isLoading ? (
          <div className="py-16 text-center">
            <Spinner label="Loading dashboard data..." />
          </div>
        ) : (
          <>
            {/* KPI GRID */}
            <section className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
              {/* 1. Total Products */}
              <div className="bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-4 sm:p-5 flex flex-col justify-between">
                <div>
                  <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Total Products</span>
                  <p className="text-2xl font-extrabold text-slate-900 mt-2">{stats.total}</p>
                </div>
                <p className="text-xs text-slate-500 mt-2">Listed in catalog</p>
              </div>

              {/* 2. Active Products */}
              <div className="bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-4 sm:p-5 flex flex-col justify-between">
                <div>
                  <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Active Products</span>
                  <p className="text-2xl font-extrabold text-slate-900 mt-2">{stats.active}</p>
                </div>
                <p className="text-xs text-emerald-600 font-medium mt-2">Live on store</p>
              </div>

              {/* 3. Pending Certification */}
              <div className="bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-4 sm:p-5 flex flex-col justify-between">
                <div>
                  <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Pending Certification</span>
                  <p className="text-2xl font-extrabold text-amber-600 mt-2">{stats.pending}</p>
                </div>
                <p className="text-xs text-slate-500 mt-2">Under quality audit</p>
              </div>

              {/* 4. Low Stock */}
              <div className="bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-4 sm:p-5 flex flex-col justify-between">
                <div>
                  <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Low Stock</span>
                  <p className="text-2xl font-extrabold text-rose-600 mt-2">{stats.lowStock}</p>
                </div>
                <p className="text-xs text-slate-500 mt-2">Stock &le; 10 units</p>
              </div>

              {/* 5. Orders */}
              <div className="bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-4 sm:p-5 flex flex-col justify-between">
                <div>
                  <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Orders</span>
                  <p className="text-2xl font-extrabold text-slate-900 mt-2">{stats.orders}</p>
                </div>
                <p className="text-xs text-slate-500 mt-2">Orders received</p>
              </div>

              {/* 6. Revenue */}
              <div className="bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-4 sm:p-5 flex flex-col justify-between">
                <div>
                  <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Revenue</span>
                  <p className="text-2xl font-extrabold text-slate-900 mt-2">{stats.revenue}</p>
                </div>
                <p className="text-xs text-emerald-600 font-medium mt-2">Real seller earnings</p>
              </div>
            </section>

            {/* ROW 1: SALES & REVENUE + CERTIFICATION STATUS */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Sales & Revenue Overview */}
              <div className="lg:col-span-7 bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-5 sm:p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="font-display text-base font-bold text-slate-900">Sales &amp; Revenue Overview</h2>
                </div>

                {monthlySalesList.length === 0 ? (
                  <div className="rounded-xl border border-slate-100 bg-slate-50/60 p-6 text-center text-xs text-slate-500">
                    No sales recorded yet. Sales and monthly revenue breakdown will appear here as orders are placed.
                  </div>
                ) : (
                  <div className="space-y-3">
                    {monthlySalesList.map((item) => {
                      const rev = Number(item.revenue || 0);
                      const maxRev = Math.max(...monthlySalesList.map((i) => Number(i.revenue || 0)), 1);
                      const pct = Math.min(100, Math.round((rev / maxRev) * 100));
                      return (
                        <div key={item.month} className="space-y-1.5 p-3 rounded-xl border border-slate-100 bg-slate-50/50">
                          <div className="flex items-center justify-between text-xs">
                            <div>
                              <span className="font-bold text-slate-800">{item.month}</span>
                              <span className="text-slate-500 ml-2">({item.orders} order{item.orders !== 1 ? "s" : ""})</span>
                            </div>
                            <span className="font-extrabold text-emerald-700">₹{rev.toFixed(2)}</span>
                          </div>
                          <div className="h-2 w-full rounded-full bg-slate-200/60 overflow-hidden">
                            <div style={{ width: `${pct}%` }} className="h-full bg-emerald-500 rounded-full transition-all duration-300" />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Certification Status */}
              <div className="lg:col-span-5 bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-5 sm:p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="font-display text-base font-bold text-slate-900">Certification Status</h2>
                  <span className="inline-flex items-center rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-800 border border-emerald-200">
                    NPOP Compliant
                  </span>
                </div>

                <div className="divide-y divide-slate-100 text-xs">
                  <div className="flex justify-between py-2.5">
                    <span className="text-slate-600 font-medium">Approved</span>
                    <span className="font-bold text-emerald-700">{stats.approved}</span>
                  </div>
                  <div className="flex justify-between py-2.5">
                    <span className="text-slate-600 font-medium">Pending</span>
                    <span className="font-bold text-amber-600">{stats.pending}</span>
                  </div>
                  <div className="flex justify-between py-2.5">
                    <span className="text-slate-600 font-medium">Rejected</span>
                    <span className="font-bold text-rose-600">{stats.rejected}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* ROW 2: INVENTORY OVERVIEW + RECENT ORDERS */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Inventory Overview */}
              <div className="lg:col-span-7 bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-5 sm:p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="font-display text-base font-bold text-slate-900">Inventory Overview</h2>
                  <span className="text-xs text-slate-400 font-medium">By Category</span>
                </div>

                {categoryInventory.length === 0 ? (
                  <p className="text-xs text-slate-500 text-center py-4">No categories listed yet.</p>
                ) : (
                  <div className="space-y-3">
                    {categoryInventory.map((cat) => (
                      <div key={cat.name} className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-semibold text-slate-800">{cat.name}</span>
                          <span className="text-slate-500">{cat.stock} ({cat.count})</span>
                        </div>
                        <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                          <div style={{ width: `${cat.share}%` }} className={`h-full ${cat.color} rounded-full`} />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Recent Orders */}
              <div className="lg:col-span-5 bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-5 sm:p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="font-display text-base font-bold text-slate-900">Recent Orders</h2>
                </div>

                {recentOrdersList.length === 0 ? (
                  <div className="rounded-xl border border-slate-100 bg-slate-50/60 p-6 text-center">
                    <p className="font-semibold text-slate-800 text-xs">No seller orders yet</p>
                    <p className="text-[11px] text-slate-500 mt-0.5">Orders received from customers will appear here.</p>
                  </div>
                ) : (
                  <div className="space-y-2.5">
                    {recentOrdersList.map((ord) => {
                      const orderId = ord.order_id || ord.id;
                      const rev = Number(ord.seller_revenue || ord.total_amount || 0);
                      const itemCount = ord.items_count ?? (ord.items?.length || 1);
                      const dateStr = ord.created_at ? new Date(ord.created_at).toLocaleDateString() : "";
                      return (
                        <div key={orderId} className="flex items-center justify-between p-3 rounded-xl border border-slate-100 bg-slate-50/50 hover:bg-slate-50 transition text-xs">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-bold text-slate-900">Order #{orderId}</span>
                              <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold border ${
                                ord.status === "CONFIRMED" || ord.status === "DELIVERED"
                                  ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                                  : ord.status === "CANCELLED"
                                  ? "bg-rose-50 text-rose-800 border-rose-200"
                                  : "bg-amber-50 text-amber-800 border-amber-200"
                              }`}>
                                {ord.status}
                              </span>
                            </div>
                            <p className="text-slate-500 mt-0.5 text-[11px]">{dateStr} • {itemCount} item{itemCount !== 1 ? "s" : ""}</p>
                          </div>
                          <div className="text-right">
                            <p className="font-bold text-slate-900">₹{rev.toFixed(2)}</p>
                            <span className={`text-[10px] font-medium ${ord.payment_status === "PAID" ? "text-emerald-600" : "text-amber-600"}`}>
                              {ord.payment_status}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* ROW 3: PRODUCT PERFORMANCE / CATALOG TABLE */}
            <div className="bg-white border border-slate-200/80 shadow-2xs rounded-2xl p-5 sm:p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="font-display text-base font-bold text-slate-900">Product Performance</h2>
                <Link to="/seller/products" className="text-xs font-semibold text-emerald-700 hover:underline">
                  Manage Catalog &rarr;
                </Link>
              </div>

              {products.length === 0 ? (
                <EmptyState
                  title="No products found"
                  description="Add your first product to display it on the marketplace."
                  action={
                    <Link to="/seller/products" className="inline-flex items-center rounded-xl bg-emerald-600 px-4 py-2 text-xs font-semibold text-white shadow-2xs hover:bg-emerald-700 transition">
                      + Add Product
                    </Link>
                  }
                />
              ) : (
                <div className="overflow-x-auto rounded-xl border border-slate-200/80">
                  <table className="min-w-full divide-y divide-slate-200/80 text-xs">
                    <thead className="bg-slate-50 text-left font-semibold text-slate-500 uppercase tracking-wider">
                      <tr>
                        <th className="px-4 py-3">Product</th>
                        <th className="px-4 py-3">Category</th>
                        <th className="px-4 py-3">Price</th>
                        <th className="px-4 py-3">Stock</th>
                        <th className="px-4 py-3">Certification</th>
                        <th className="px-4 py-3">Status</th>
                        <th className="px-4 py-3 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 bg-white">
                      {products.map((prod) => (
                        <tr key={prod.id} className="hover:bg-slate-50/60 transition">
                          <td className="px-4 py-3 font-semibold text-slate-900 flex items-center gap-2.5">
                            <img
                              src={prod.image_url || "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=200&q=80"}
                              alt={prod.name}
                              className="h-8 w-8 rounded-lg object-cover border border-slate-200 shrink-0"
                            />
                            <span>{prod.name}</span>
                          </td>
                          <td className="px-4 py-3 text-slate-600">{prod.category?.name || "Organic"}</td>
                          <td className="px-4 py-3 font-semibold text-emerald-700">₹{Number(prod.price).toFixed(2)} / {prod.unit}</td>
                          <td className="px-4 py-3 text-slate-600">{prod.stock_quantity} units</td>
                          <td className="px-4 py-3">
                            <span
                              className={`inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-semibold border ${
                                prod.certification === "APPROVED"
                                  ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                                  : prod.certification === "REJECTED"
                                  ? "bg-rose-50 text-rose-800 border-rose-200"
                                  : "bg-amber-50 text-amber-800 border-amber-200"
                              }`}
                            >
                              {prod.certification || "PENDING"}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            <span
                              className={`inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-semibold border ${
                                prod.is_active
                                  ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                                  : "bg-slate-100 text-slate-600 border-slate-200"
                              }`}
                            >
                              {prod.is_active ? "Active" : "Inactive"}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right">
                            <Link
                              to="/seller/products"
                              className="text-xs font-semibold text-emerald-700 hover:underline"
                            >
                              Edit
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        )}

      </div>
    </div>
  );
}
