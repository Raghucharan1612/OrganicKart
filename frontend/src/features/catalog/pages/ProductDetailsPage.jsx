import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import productService from "@/services/productService";
import categoryService from "@/services/categoryService";
import orderService from "@/services/orderService";
import Spinner from "@/components/Spinner";
import { useAuth } from "@/hooks/useAuth";
import toast from "react-hot-toast";
import { getApiErrorMessage } from "@/utils/errorUtils";

const CATEGORY_EMOJI = {
  Fruits: "🍎",
  Vegetables: "🥦",
  "Organic Oils": "🫒",
  "Juices & Beverages": "🧃",
  "Grains & Pulses": "🌾",
  Spices: "🌶️",
  Snacks: "🥜",
  "Honey & Sweeteners": "🍯",
  "Personal Care": "🧴",
};

export default function ProductDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [product, setProduct] = useState(null);
  const [categoryName, setCategoryName] = useState("Organic");
  const [quantity, setQuantity] = useState(1);
  const [isAdding, setIsAdding] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError("");

    productService
      .getById(id)
      .then((data) => {
        if (cancelled) return;
        setProduct(data);
        if (data?.category_id) {
          categoryService
            .get(data.category_id)
            .then((category) => setCategoryName(category?.name || "Organic"))
            .catch(() => setCategoryName("Organic"));
        }
      })
      .catch((err) => {
        if (!cancelled) {
          const message = getApiErrorMessage(err, "This product could not be found.");
          setError(message);
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [id]);

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      navigate("/login", { state: { from: { pathname: `/products/${id}` } }, replace: true });
      return;
    }

    if (!product || product.certification !== "APPROVED" || product.is_active === false || Number(product.stock_quantity || 0) <= 0) {
      toast.error("This product is unavailable for purchase.");
      return;
    }

    setIsAdding(true);
    try {
      await orderService.addItem({ product_id: Number(product.id), quantity });
      toast.success(`${product.name} added to cart.`);
      window.dispatchEvent(new Event("cart-updated"));
    } catch (err) {
      const message = getApiErrorMessage(err, "Unable to add this item to your cart.");
      toast.error(message);
    } finally {
      setIsAdding(false);
    }
  };

  if (isLoading) return <Spinner label="Loading product…" />;

  if (error || !product) {
    return (
      <div className="card mx-auto max-w-md text-center">
        <h1 className="font-display text-xl font-bold text-primary-900">Product not found</h1>
        <p className="mt-2 text-sm text-gray-500">{error || "The item you selected is unavailable."}</p>
        <Link to="/products" className="btn-primary mt-4 inline-flex">
          Back to shop
        </Link>
      </div>
    );
  }

  const unavailable = product.certification !== "APPROVED" || product.is_active === false || Number(product.stock_quantity || 0) <= 0;
  const outOfStock = Number(product.stock_quantity || 0) <= 0;
  const emoji = CATEGORY_EMOJI[categoryName] || "🌿";

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <Link to="/products" className="inline-flex items-center text-sm font-medium text-primary-700 hover:underline">← Back to catalog</Link>

      <div className="grid max-w-5xl grid-cols-1 gap-8 md:grid-cols-2">
        <div className="flex h-72 items-center justify-center overflow-hidden rounded-[28px] bg-primary-50 text-8xl shadow-sm md:h-full">
          {product.image_url ? (
            <img src={product.image_url} alt={product.name} className="h-full w-full object-cover" />
          ) : (
            <span>{emoji}</span>
          )}
        </div>

        <div className="rounded-[28px] border border-gray-100 bg-white p-5 shadow-sm sm:p-6">
          <Link to={`/products?category_id=${product.category_id}`} className="text-xs font-medium uppercase tracking-[0.2em] text-primary-600 hover:underline">
            {categoryName}
          </Link>

          <h1 className="mt-2 font-display text-3xl font-bold text-primary-900">{product.name}</h1>

          <div className="mt-4 flex flex-wrap items-center gap-2">
            {product.certification && (
              <span className="rounded-full bg-primary-100 px-2.5 py-1 text-xs font-semibold text-primary-700">
                🌱 {product.certification}
              </span>
            )}
            {!unavailable && (
              <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-medium text-emerald-700">
                Fresh stock ready
              </span>
            )}
          </div>

          <p className="mt-5 text-3xl font-bold text-primary-900">
            ₹{Number(product.price).toFixed(2)}
            <span className="text-base font-normal text-gray-500"> / {product.unit}</span>
          </p>

          <p className="mt-2 text-sm">
            {outOfStock ? (
              <span className="font-medium text-red-600">Out of stock</span>
            ) : (
              <span className="font-medium text-primary-700">
                {product.stock_quantity} units available
              </span>
            )}
          </p>

          {product.description && <p className="mt-5 leading-relaxed text-gray-600">{product.description}</p>}

          <div className="mt-6 flex flex-col gap-2 rounded-2xl border border-primary-100 bg-primary-50/40 p-4">
            <div className="flex items-center justify-between">
              <label className="text-sm font-bold text-primary-900">Select Quantity / Weight</label>
              <span className="text-xs font-semibold text-primary-700">
                Total: ₹{(Number(product.price) * quantity).toFixed(2)}
              </span>
            </div>
            <div className="flex items-center gap-3 mt-1">
              <div className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-2 py-1 shadow-xs">
                <button type="button" className="h-8 w-8 rounded-md text-lg text-primary-700 hover:bg-primary-50 font-bold" onClick={() => setQuantity((q) => Math.max(1, q - 1))}>
                  −
                </button>
                <span className="min-w-6 text-center text-sm font-bold text-gray-900">{quantity}</span>
                <button type="button" className="h-8 w-8 rounded-md text-lg text-primary-700 hover:bg-primary-50 font-bold" onClick={() => setQuantity((q) => Math.min(Math.max(1, Number(product.stock_quantity || 1)), q + 1))}>
                  +
                </button>
              </div>
              <span className="text-xs text-gray-600 font-medium">
                ({quantity} × {product.unit} = <span className="font-bold text-gray-900">{quantity * (parseInt(product.unit, 10) || 1)}{product.unit.replace(/[0-9]/g, '') || " units"}</span>)
              </span>
            </div>
          </div>

          <div className="mt-6 rounded-2xl border border-gray-100 bg-gray-50 p-4 text-sm text-gray-600">
            <div>Seller ID: <span className="font-medium text-primary-800">{product.seller_id}</span></div>
            <div className="mt-1">Category: <span className="font-medium text-primary-800">{categoryName}</span></div>
          </div>

          <button
            type="button"
            onClick={handleAddToCart}
            disabled={unavailable || isAdding}
            className="btn-primary mt-6 w-full disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isAdding ? "Adding…" : unavailable ? "Unavailable for purchase" : `Add to cart · ₹${(Number(product.price) * quantity).toFixed(2)}`}
          </button>
        </div>
      </div>
    </div>
  );
}
