import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import productService from "@/services/productService";
import categoryService from "@/services/categoryService";
import ProductForm from "@/features/catalog/components/ProductForm";
import Button from "@/components/Button";
import Spinner from "@/components/Spinner";
import EmptyState from "@/components/EmptyState";
import SellerSubNav from "@/components/SellerSubNav";
import { getApiErrorMessage } from "@/utils/errorUtils";

export default function MyProductsPage() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [formMode, setFormMode] = useState(null); // null | "create" | product.id being edited
  const [loadError, setLoadError] = useState("");
  const [deactivateProduct, setDeactivateProduct] = useState(null);
  const [isDeactivating, setIsDeactivating] = useState(false);

  const loadData = async () => {
    setIsLoading(true);
    setLoadError("");
    try {
      const [productsData, categoriesData] = await Promise.all([
        productService.listMine(),
        categoryService.list(),
      ]);
      setProducts(productsData);
      setCategories(categoriesData);
    } catch (err) {
      setLoadError("Could not load your products. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreate = async (payload) => {
    setIsSaving(true);
    try {
      await productService.create(payload);
      toast.success("Product created.");
      setFormMode(null);
      await loadData();
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not create product."));
    } finally {
      setIsSaving(false);
    }
  };

  const handleUpdate = async (productId, payload) => {
    setIsSaving(true);
    try {
      await productService.update(productId, payload);
      toast.success("Product updated.");
      setFormMode(null);
      await loadData();
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not update product."));
    } finally {
      setIsSaving(false);
    }
  };

  const confirmDeactivate = async () => {
    if (!deactivateProduct) return;
    setIsDeactivating(true);
    try {
      await productService.deactivate(deactivateProduct.id);
      toast.success("Product deactivated.");
      setDeactivateProduct(null);
      await loadData();
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not deactivate product."));
    } finally {
      setIsDeactivating(false);
    }
  };

  const editingProduct = typeof formMode === "number" ? products.find((p) => p.id === formMode) : null;

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Seller secondary nav — consistent across all seller pages */}
      <SellerSubNav activeTab="products" />

      <div className="w-full px-4 py-6 sm:px-6 lg:px-8 xl:px-10 2xl:px-12 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-primary-900">My Products</h1>
          <p className="mt-1 text-sm text-gray-500">Manage your OrganicKart product listings.</p>
        </div>
        {formMode === null && <Button onClick={() => setFormMode("create")}>+ Add product</Button>}
      </div>

      {formMode === "create" && (
        <div className="card">
          <h2 className="mb-4 font-display text-lg font-semibold text-primary-900">New product</h2>
          <ProductForm categories={categories} onSubmit={handleCreate} onCancel={() => setFormMode(null)} isSaving={isSaving} />
        </div>
      )}

      {editingProduct && (
        <div className="card">
          <h2 className="mb-4 font-display text-lg font-semibold text-primary-900">Edit product</h2>
          <ProductForm
            categories={categories}
            initialValues={editingProduct}
            onSubmit={(payload) => handleUpdate(editingProduct.id, payload)}
            onCancel={() => setFormMode(null)}
            isSaving={isSaving}
          />
        </div>
      )}

      {isLoading ? (
        <Spinner label="Loading your products…" />
      ) : loadError ? (
        <div className="card text-center text-sm text-red-600">{loadError}</div>
      ) : products.length === 0 && formMode === null ? (
        <EmptyState
          title="No products yet"
          description="List your first organic product to start selling on OrganicKart."
          action={<Button onClick={() => setFormMode("create")}>+ Add product</Button>}
        />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-100">
          <table className="min-w-full divide-y divide-gray-100 text-sm">
            <thead className="bg-gray-50 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
              <tr>
                <th className="px-4 py-3">Product</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Price</th>
                <th className="px-4 py-3">Stock</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {products.map((p) => {
                const categoryName = p.category?.name || categories.find((c) => c.id === p.category_id)?.name || "Uncategorized";
                return (
                  <tr key={p.id}>
                    <td className="px-4 py-3 font-medium text-primary-900">{p.name}</td>
                    <td className="px-4 py-3 text-gray-600">{categoryName}</td>
                    <td className="px-4 py-3 text-gray-600">₹{Number(p.price).toFixed(2)} / {p.unit}</td>
                    <td className="px-4 py-3 text-gray-600">{p.stock_quantity}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                          p.is_active ? "bg-primary-100 text-primary-700" : "bg-gray-100 text-gray-500"
                        }`}
                      >
                        {p.is_active ? "Active" : "Deactivated"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => setFormMode(p.id)}
                        className="mr-3 text-sm font-medium text-primary-700 hover:underline"
                      >
                        Edit
                      </button>
                      {p.is_active && (
                        <button
                          onClick={() => setDeactivateProduct(p)}
                          className="text-sm font-medium text-red-600 hover:underline"
                        >
                          Deactivate
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* In-app Product Deactivation Confirmation Modal */}
      {deactivateProduct && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-xs animate-fade-in">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl space-y-4">
            <h3 className="font-display text-lg font-bold text-gray-900">
              Deactivate Product?
            </h3>
            <p className="text-sm text-gray-600">
              Are you sure you want to deactivate this product?
            </p>
            <div className="flex justify-end gap-3 pt-2">
              <Button
                variant="secondary"
                onClick={() => setDeactivateProduct(null)}
                disabled={isDeactivating}
              >
                Cancel
              </Button>
              <Button
                className="!bg-red-600 hover:!bg-red-700 !text-white"
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
    </div>
  );
}
