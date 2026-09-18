import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { useAuth } from "@/hooks/useAuth";
import productService from "@/services/productService";
import Spinner from "@/components/Spinner";
import { getApiErrorMessage } from "@/utils/errorUtils";

export default function AdminPage() {
  const { user } = useAuth();
  const [pendingProducts, setPendingProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [updatingProductId, setUpdatingProductId] = useState(null);

  const loadPendingProducts = async () => {
    setIsLoading(true);
    try {
      const data = await productService.list({ certification: "PENDING", page: 1, page_size: 20 });
      setPendingProducts(Array.isArray(data?.items) ? data.items : []);
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not load pending certifications."));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPendingProducts();
  }, []);

  const handleDecision = async (productId, action) => {
    setUpdatingProductId(productId);
    try {
      if (action === "approve") {
        await productService.approve(productId);
        toast.success("Product approved.");
      } else {
        await productService.reject(productId);
        toast.success("Product rejected.");
      }
      await loadPendingProducts();
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not update certification."));
    } finally {
      setUpdatingProductId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <h1 className="font-display text-2xl font-bold text-primary-900">Admin Area</h1>
        <p className="mt-2 text-sm text-gray-500">
          Welcome, {user?.full_name || "Administrator"}. You are viewing the operational admin workspace for certification approvals and catalog administration.
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link to="/admin/categories" className="btn-secondary">Manage categories</Link>
          <Link to="/products" className="btn-secondary">View storefront</Link>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between gap-3">
          <h2 className="font-display text-xl font-semibold text-primary-900">Pending certifications</h2>
          <span className="rounded-full bg-primary-100 px-2.5 py-1 text-xs font-semibold text-primary-700">
            {pendingProducts.length} waiting
          </span>
        </div>

        {isLoading ? (
          <div className="mt-5"><Spinner label="Loading certification queue…" /></div>
        ) : pendingProducts.length === 0 ? (
          <p className="mt-4 text-sm text-gray-500">No products are currently waiting for certification approval.</p>
        ) : (
          <div className="mt-5 space-y-3">
            {pendingProducts.map((product) => (
              <div key={product.id} className="rounded-xl border border-gray-100 p-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-medium text-primary-900">{product.name}</p>
                    <p className="text-sm text-gray-500">Seller ID: {product.seller_id} · Stock: {product.stock_quantity}</p>
                  </div>
                  <div className="flex gap-2">
                    <button type="button" onClick={() => handleDecision(product.id, "approve")} disabled={updatingProductId !== null} className="btn-primary !py-2">{updatingProductId === product.id ? "Updating…" : "Approve"}</button>
                    <button type="button" onClick={() => handleDecision(product.id, "reject")} disabled={updatingProductId !== null} className="btn-secondary !py-2">Reject</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
