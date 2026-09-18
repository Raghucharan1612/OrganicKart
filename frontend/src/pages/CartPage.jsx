import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import orderService from "@/services/orderService";
import productService from "@/services/productService";
import Spinner from "@/components/Spinner";
import { getApiErrorMessage } from "@/utils/errorUtils";

export default function CartPage() {
  const [cart, setCart] = useState({ items: [] });
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState("");
  const [imageUrls, setImageUrls] = useState({});
  const [brokenImages, setBrokenImages] = useState({});

  const loadCart = async () => {
    setIsLoading(true);
    try {
      const data = await orderService.getCart();
      setCart(data || { items: [] });
      const missingImageItems = (data?.items || []).filter((item) => !item.image_url && !imageUrls[item.product_id]);
      if (missingImageItems.length) {
        const resolvedImages = await Promise.all(
          missingImageItems.map(async (item) => {
            try {
              const product = await productService.getById(item.product_id);
              return [item.product_id, product?.image_url || null];
            } catch {
              return [item.product_id, null];
            }
          })
        );
        setImageUrls((current) => ({ ...current, ...Object.fromEntries(resolvedImages) }));
      }
      setError("");
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to load your cart right now."));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCart();
  }, []);

  const updateQuantity = async (itemId, nextQty) => {
    if (nextQty < 1) return removeItem(itemId);
    setIsUpdating(true);
    try {
      await orderService.updateItem(itemId, { quantity: nextQty });
      await loadCart();
      window.dispatchEvent(new Event("cart-updated"));
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to update item quantity."));
    } finally {
      setIsUpdating(false);
    }
  };

  const removeItem = async (itemId) => {
    setIsUpdating(true);
    try {
      await orderService.removeItem(itemId);
      await loadCart();
      window.dispatchEvent(new Event("cart-updated"));
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to remove item."));
    } finally {
      setIsUpdating(false);
    }
  };

  const clearCart = async () => {
    setIsUpdating(true);
    try {
      await orderService.clearCart();
      setCart({ items: [] });
      setError("");
      window.dispatchEvent(new Event("cart-updated"));
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to clear the cart."));
    } finally {
      setIsUpdating(false);
    }
  };

  const subtotal = cart.items.reduce((sum, item) => sum + Number(item.unit_price) * Number(item.quantity), 0);
  const totalQuantity = cart.items.reduce((sum, item) => sum + Number(item.quantity), 0);
  const deliveryFee = 0;

  if (isLoading) return <Spinner label="Loading cart…" />;

  if (error) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="card max-w-xl">
          <h1 className="font-display text-2xl font-bold text-primary-900">Your Cart</h1>
          <p className="mt-3 text-sm text-red-700">{error}</p>
          <button type="button" onClick={loadCart} className="btn-primary mt-5">Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="card">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="font-display text-2xl font-bold text-primary-900">Your Cart</h1>
            <p className="mt-1 text-sm text-gray-500">{totalQuantity} items selected</p>
          </div>
          {cart.items.length > 0 && (
            <button type="button" onClick={clearCart} disabled={isUpdating} className="btn-secondary">
              Clear cart
            </button>
          )}
        </div>

        {cart.items.length === 0 ? (
          <div className="mt-6 rounded-3xl border border-dashed border-gray-200 bg-primary-50/30 p-10 text-center">
            <p className="text-base font-bold text-gray-700">Your cart is empty.</p>
            <p className="text-xs text-gray-500 mt-1">Explore our farm-fresh organic catalog to add items.</p>
            <Link to="/products" className="btn-primary mt-5 inline-flex font-bold">
              Browse Products →
            </Link>
          </div>
        ) : (
          <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
            <div className="space-y-4">
              {cart.items.map((item) => (
                <div key={item.id} className="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm transition hover:border-primary-100">
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex items-center gap-3">
                      {/* Product Image / Icon */}
                      <div className="h-16 w-16 shrink-0 overflow-hidden rounded-xl bg-primary-50 flex items-center justify-center border border-gray-100">
                        {(item.image_url || imageUrls[item.product_id]) && !brokenImages[item.id] ? (
                          <img
                            src={item.image_url || imageUrls[item.product_id]}
                            alt={item.product_name}
                            onError={() => setBrokenImages((current) => ({ ...current, [item.id]: true }))}
                            className="h-full w-full object-cover"
                          />
                        ) : (
                          <span className="text-2xl">🌿</span>
                        )}
                      </div>

                      <div>
                        <Link to={`/products/${item.product_id}`} className="font-bold text-gray-900 hover:text-primary-700 transition">
                          {item.product_name}
                        </Link>
                        <div className="flex items-center gap-2 mt-0.5 text-xs text-gray-500">
                          <span>₹{Number(item.unit_price).toFixed(2)} / {item.unit || "unit"}</span>
                          <span>•</span>
                          <span className="font-semibold text-primary-800">Subtotal: ₹{(Number(item.unit_price) * Number(item.quantity)).toFixed(2)}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between sm:justify-end gap-4 border-t sm:border-t-0 pt-2 sm:pt-0 border-gray-100">
                      <div className="flex items-center gap-2 rounded-xl border border-gray-200 bg-gray-50 px-2 py-1">
                        <button type="button" className="h-7 w-7 rounded-lg text-lg font-bold text-primary-700 hover:bg-primary-100/60 transition" onClick={() => updateQuantity(item.id, Number(item.quantity) - 1)}>
                          −
                        </button>
                        <span className="min-w-6 text-center text-sm font-bold text-gray-900">{item.quantity}</span>
                        <button type="button" className="h-7 w-7 rounded-lg text-lg font-bold text-primary-700 hover:bg-primary-100/60 transition" onClick={() => updateQuantity(item.id, Number(item.quantity) + 1)}>
                          +
                        </button>
                      </div>

                      <button type="button" className="text-xs font-bold text-red-600 hover:text-red-700 px-2 py-1 hover:bg-red-50 rounded-lg transition" onClick={() => removeItem(item.id)}>
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <aside className="rounded-2xl border border-primary-100 bg-primary-50/40 p-6 space-y-4 self-start">
              <h2 className="font-display text-lg font-bold text-primary-900 border-b border-primary-100 pb-3">Order Summary</h2>
              <div className="space-y-3 text-sm text-gray-700">
                <div className="flex justify-between">
                  <span>Subtotal</span>
                  <span className="font-semibold">₹{subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Delivery Fee</span>
                  <span className="font-bold text-emerald-700 text-xs bg-emerald-50 px-2 py-0.5 rounded-md">FREE</span>
                </div>
                <div className="flex justify-between border-t border-primary-200 pt-3 text-base font-extrabold text-primary-900">
                  <span>Total</span>
                  <span className="text-primary-700">₹{(subtotal + deliveryFee).toFixed(2)}</span>
                </div>
              </div>
              <Link to="/checkout" className="btn-primary mt-6 w-full font-bold !py-3 shadow-md">
                Proceed to Checkout ⚡
              </Link>
            </aside>
          </div>
        )}
      </div>
    </div>
  );
}

