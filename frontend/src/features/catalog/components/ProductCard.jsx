import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import orderService from "@/services/orderService";
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
  Dairy: "🥛",
};

function formatPrice(price) {
  return `₹${Number(price).toFixed(2)}`;
}

export default function ProductCard({ product }) {
  const { isAuthenticated } = useAuth();
  const [isAdding, setIsAdding] = useState(false);
  const [imageError, setImageError] = useState(false);

  const categoryName = product.category?.name || product.category_name || "Organic";
  const emoji = CATEGORY_EMOJI[categoryName] || "🌿";
  const outOfStock = Number(product.stock_quantity || 0) <= 0;
  const isAvailable = product.certification === "APPROVED" && product.is_active !== false && !outOfStock;

  // Optional mock discount display calculation for visual quick-commerce appeal
  const originalPrice = product.original_price || (Number(product.price) * 1.15).toFixed(2);
  const hasDiscount = Number(originalPrice) > Number(product.price);

  const handleAddToCart = async (event) => {
    event.preventDefault();
    event.stopPropagation();

    if (!isAuthenticated) {
      toast("Please login to add items to your cart", { icon: "🔒" });
      window.location.href = "/login";
      return;
    }

    if (!isAvailable) {
      toast.error("This product is currently unavailable.");
      return;
    }

    setIsAdding(true);

    try {
      await orderService.addItem({ product_id: Number(product.id), quantity: 1 });
      toast.success(`${product.name} added to cart!`, { icon: "🛒" });
      // Dispatch custom event to refresh cart count in navbar
      window.dispatchEvent(new Event("cart-updated"));
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Unable to add this item to cart."));
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <Link
      to={`/products/${product.id}`}
      className="group relative flex flex-col rounded-2xl border border-gray-100 bg-white p-3 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:border-primary-200 hover:shadow-md"
    >
      {/* Discount / Certification Badge */}
      <div className="absolute left-3 top-3 z-10 flex flex-col gap-1">
        {hasDiscount && (
          <span className="rounded-lg bg-amber-500 px-2 py-0.5 text-[10px] font-extrabold uppercase text-white shadow-sm">
            OFFER
          </span>
        )}
        {product.certification === "APPROVED" && (
          <span className="rounded-lg bg-primary-700 px-2 py-0.5 text-[10px] font-bold uppercase text-white shadow-sm">
            Organic ✓
          </span>
        )}
      </div>

      {/* Image Area */}
      <div className="relative mb-3 flex h-40 w-full items-center justify-center overflow-hidden rounded-xl bg-gray-50/80 group-hover:bg-primary-50/40 transition-colors">
        {product.image_url && !imageError ? (
          <img
            src={product.image_url}
            alt={product.name}
            onError={() => setImageError(true)}
            className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="flex flex-col items-center justify-center text-4xl">
            <span>{emoji}</span>
            <span className="mt-1 text-[11px] font-medium text-gray-400">100% Organic</span>
          </div>
        )}

        {outOfStock && (
          <div className="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-[1px]">
            <span className="rounded-lg bg-red-100 px-2.5 py-1 text-xs font-bold text-red-700">
              Out of stock
            </span>
          </div>
        )}
      </div>

      {/* Details */}
      <div className="flex flex-1 flex-col justify-between">
        <div>
          <div className="flex items-center justify-between text-[11px] font-medium text-gray-500">
            <span className="truncate text-primary-700 font-semibold">{categoryName}</span>
            <span>{product.unit || "unit"}</span>
          </div>

          <h3 className="mt-1 font-display text-sm font-bold text-gray-900 line-clamp-2 group-hover:text-primary-700 transition">
            {product.name}
          </h3>
        </div>

        {/* Price & Add Action */}
        <div className="mt-4 flex items-center justify-between gap-2 border-t border-gray-50 pt-2.5">
          <div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-base font-extrabold text-primary-900">{formatPrice(product.price)}</span>
              {hasDiscount && (
                <span className="text-xs text-gray-400 line-through">{formatPrice(originalPrice)}</span>
              )}
            </div>
            <p className="text-[10px] text-gray-400">Incl. all taxes</p>
          </div>

          <button
            type="button"
            onClick={handleAddToCart}
            disabled={!isAvailable || isAdding}
            className="flex h-9 items-center justify-center rounded-xl bg-primary-50 px-3 py-1.5 text-xs font-bold text-primary-700 border border-primary-200 transition-all hover:bg-primary-600 hover:text-white hover:border-primary-600 active:scale-95 disabled:cursor-not-allowed disabled:border-gray-200 disabled:bg-gray-100 disabled:text-gray-400"
          >
            {isAdding ? (
              <span className="flex items-center gap-1">
                <svg className="h-3 w-3 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                ...
              </span>
            ) : isAvailable ? (
              "ADD +"
            ) : (
              "Sold Out"
            )}
          </button>
        </div>
      </div>
    </Link>
  );
}

