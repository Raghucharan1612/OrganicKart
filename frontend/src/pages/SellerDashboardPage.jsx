import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import productService from "@/services/productService";
import Spinner from "@/components/Spinner";
import EmptyState from "@/components/EmptyState";
import { getApiErrorMessage } from "@/utils/errorUtils";

const badgeClasses = {
  PENDING: "bg-amber-100 text-amber-700",
  APPROVED: "bg-emerald-100 text-emerald-700",
  REJECTED: "bg-rose-100 text-rose-700",
};

export default function SellerDashboardPage() {
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const data = await productService.listMine();
      setProducts(Array.isArray(data) ? data : []);
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not load your dashboard."));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const stats = useMemo(() => {
    const total = products.length;
    const pending = products.filter((p) => p.certification === "PENDING").length;
    const approved = products.filter((p) => p.certification === "APPROVED").length;
    const rejected = products.filter((p) => p.certification === "REJECTED").length;
    const active = products.filter((p) => p.is_active).length;
    const outOfStock = products.filter((p) => Number(p.stock_quantity || 0) === 0).length;

    return { total, pending, approved, rejected, active, outOfStock };
  }, [products]);

  const summaryCards = [
    { label: "Total Products", value: stats.total },
    { label: "Pending", value: stats.pending },
    { label: "Approved", value: stats.approved },
    { label: "Rejected", value: stats.rejected },
    { label: "Active", value: stats.active },
    { label: "Out of stock", value: stats.outOfStock },
  ];

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-primary-900">Seller dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">Track product health, pending reviews, and inventory status.</p>
        </div>
        <Link to="/seller/products" className="btn-primary">Manage products</Link>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {summaryCards.map((card) => (
          <div key={card.label} className="card">
            <p className="text-sm text-gray-500">{card.label}</p>
            <p className="mt-3 text-3xl font-bold text-primary-900">{card.value}</p>
          </div>
        ))}
      </div>

      {isLoading ? (
        <Spinner label="Loading seller dashboard…" />
      ) : products.length === 0 ? (
        <EmptyState
          title="No products yet"
          description="Add your first listing and submit it for admin certification."
          action={<Link to="/seller/products" className="btn-primary">Add product</Link>}
        />
      ) : (
        <div className="card overflow-hidden">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-xl font-semibold text-primary-900">Recent listings</h2>
            <Link to="/seller/products" className="text-sm font-medium text-primary-700 hover:underline">View all</Link>
          </div>

          <div className="space-y-3">
            {products.slice(0, 6).map((product) => (
              <div key={product.id} className="flex flex-col gap-3 rounded-xl border border-gray-100 p-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-3">
                  <img
                    src={product.image_url || "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=200&q=80"}
                    alt={product.name}
                    className="h-14 w-14 rounded-lg object-cover"
                  />
                  <div>
                    <p className="font-medium text-primary-900">{product.name}</p>
                    <p className="text-sm text-gray-500">{product.category?.name || "Organic"} · ₹{Number(product.price).toFixed(2)} / {product.unit}</p>
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`rounded-full px-2 py-1 text-xs font-medium ${badgeClasses[product.certification] || "bg-gray-100 text-gray-600"}`}>
                    {product.certification || "PENDING"}
                  </span>
                  <span className={`rounded-full px-2 py-1 text-xs font-medium ${product.is_active ? "bg-emerald-100 text-emerald-700" : "bg-gray-100 text-gray-600"}`}>
                    {product.is_active ? "Active" : "Inactive"}
                  </span>
                  <span className="rounded-full bg-primary-100 px-2 py-1 text-xs font-medium text-primary-700">
                    {Number(product.stock_quantity || 0) === 0 ? "Out of stock" : Number(product.stock_quantity || 0) <= 10 ? "Low stock" : "In stock"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
