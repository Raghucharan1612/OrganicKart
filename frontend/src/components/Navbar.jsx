import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import orderService from "@/services/orderService";
import notificationService from "@/services/notificationService";

export default function Navbar() {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [cartCount, setCartCount] = useState(0);
  const [unreadCount, setUnreadCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState(searchParams.get("search") || "");
  const [location, setLocation] = useState("Bengaluru, 560001");
  const cartRefreshVersion = useRef(0);
  const isCustomer = user?.role === "CUSTOMER";
  const isPartner = user?.role === "DELIVERY_PARTNER";

  const refreshCounts = async () => {
    const refreshVersion = ++cartRefreshVersion.current;
    if (!isAuthenticated) {
      setCartCount(0);
      setUnreadCount(0);
      return;
    }

    try {
      const [cartData, notifications] = await Promise.all([
        isCustomer ? orderService.getCart().catch(() => ({ items: [] })) : Promise.resolve({ items: [] }),
        notificationService.list().catch(() => []),
      ]);

      // Ignore an older in-flight fetch so a cart mutation cannot be
      // overwritten by a stale response after `cart-updated` fires.
      if (refreshVersion !== cartRefreshVersion.current) return;
      const cartItems = Array.isArray(cartData?.items) ? cartData.items : [];
      const notificationItems = Array.isArray(notifications) ? notifications : [];
      setCartCount(cartItems.reduce((sum, item) => sum + Number(item.quantity || 0), 0));
      setUnreadCount(notificationItems.filter((item) => String(item.status).toUpperCase() !== "READ").length);
    } catch {
      if (refreshVersion !== cartRefreshVersion.current) return;
      setCartCount(0);
      setUnreadCount(0);
    }
  };

  useEffect(() => {
    refreshCounts();
    const handleCartUpdate = () => refreshCounts();
    window.addEventListener("cart-updated", handleCartUpdate);
    return () => window.removeEventListener("cart-updated", handleCartUpdate);
  }, [isAuthenticated, isCustomer]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/products?search=${encodeURIComponent(searchQuery.trim())}`);
    } else {
      navigate("/products");
    }
  };

  return (
    <div className="sticky top-0 z-40 bg-white shadow-sm border-b border-gray-100">
      {/* Top Promotional Bar */}
      <div className="bg-gradient-to-r from-primary-900 via-primary-800 to-purple-900 text-white text-xs py-1.5 px-4 font-medium">
        <div className="mx-auto max-w-7xl flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 bg-primary-700/60 px-2 py-0.5 rounded-full text-[11px] font-semibold text-accent-300">
              ⚡ 10-Min Delivery
            </span>
            <span className="hidden sm:inline text-purple-200">• Fresh & 100% Organic • Best Prices Guaranteed</span>
          </div>
          <div className="flex items-center gap-4 text-purple-200">
            <span className="hidden md:inline">📞 Support: 1800-ORGANIC</span>
            <span className="cursor-pointer hover:text-white transition">🇮🇳 ENG</span>
          </div>
        </div>
      </div>

      {/* Main Navbar */}
      <header className="bg-white">
        <div className="mx-auto max-w-7xl px-4 py-3 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between gap-4">
            {/* Logo */}
            <Link to={isPartner ? "/delivery" : "/"} className="flex items-center gap-2 group shrink-0">
              <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-primary-600 to-purple-800 flex items-center justify-center text-white text-xl shadow-md group-hover:scale-105 transition-transform">
                🪻
              </div>
              <div className="flex flex-col">
                <span className="font-display text-xl font-bold tracking-tight text-primary-900 group-hover:text-primary-700 transition">
                  OrganicKart
                </span>
                <span className="text-[10px] font-semibold uppercase tracking-widest text-primary-600 -mt-1">
                  Quick Commerce
                </span>
              </div>
            </Link>

            {/* Delivery Location Indicator */}
            {!isPartner && <div className="hidden lg:flex items-center gap-2 rounded-2xl bg-primary-50 px-3.5 py-2 border border-primary-100/80 cursor-pointer hover:bg-primary-100/50 transition">
              <span className="text-lg">📍</span>
              <div className="flex flex-col text-left">
                <span className="text-[10px] font-bold uppercase tracking-wider text-primary-700">Deliver to</span>
                <span className="text-xs font-semibold text-gray-800 truncate max-w-[140px]">{location}</span>
              </div>
              <span className="text-xs text-primary-600 font-bold ml-1">▼</span>
            </div>}

            {/* Global Search Bar */}
            {!isPartner && <form onSubmit={handleSearchSubmit} className="flex-1 max-w-lg hidden md:flex items-center relative">
              <div className="relative w-full">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search fresh veggies, fruits, organic milk, oils…"
                  className="w-full rounded-2xl border border-gray-200 bg-gray-50/80 pl-11 pr-24 py-2.5 text-sm text-gray-800 placeholder:text-gray-400 focus:bg-white focus:border-primary-500 focus:ring-4 focus:ring-primary-100 focus:outline-none transition-all shadow-inner"
                />
                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 text-base">🔍</span>
                <button
                  type="submit"
                  className="absolute right-1.5 top-1/2 -translate-y-1/2 bg-primary-600 text-white text-xs font-semibold px-4 py-1.5 rounded-xl hover:bg-primary-700 transition shadow-sm"
                >
                  Search
                </button>
              </div>
            </form>}

            {/* Right Actions */}
            <nav className="flex items-center gap-2 sm:gap-3">
              {!isPartner && <Link
                to="/products"
                className="hidden sm:inline-flex items-center px-3 py-2 text-sm font-semibold text-gray-700 hover:text-primary-700 hover:bg-primary-50 rounded-xl transition"
              >
                Catalog
              </Link>}

              {isAuthenticated ? (
                <>
                  {isPartner && (
                    <>
                      <Link to="/delivery" className="hidden md:inline-flex items-center px-3 py-2 text-sm font-semibold text-gray-700 hover:text-primary-700 hover:bg-primary-50 rounded-xl transition">Dashboard</Link>
                      <Link to="/delivery" className="hidden md:inline-flex items-center px-3 py-2 text-sm font-semibold text-gray-700 hover:text-primary-700 hover:bg-primary-50 rounded-xl transition">Deliveries</Link>
                    </>
                  )}
                  {isCustomer && (
                    <Link
                      to="/orders"
                      className="hidden md:inline-flex items-center px-3 py-2 text-sm font-semibold text-gray-700 hover:text-primary-700 hover:bg-primary-50 rounded-xl transition"
                    >
                      Orders
                    </Link>
                  )}

                  {!isPartner && <Link
                    to="/notifications"
                    className="relative p-2.5 text-gray-700 hover:text-primary-700 hover:bg-primary-50 rounded-2xl transition"
                    title="Notifications"
                  >
                    <span className="text-lg">🔔</span>
                    {unreadCount > 0 && (
                      <span className="absolute top-1.5 right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-amber-500 text-[10px] font-bold text-white shadow-sm ring-2 ring-white">
                        {unreadCount}
                      </span>
                    )}
                  </Link>}

                  {isCustomer && (
                    <Link
                      to="/cart"
                      className="relative flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-2xl font-semibold text-sm shadow-sm hover:bg-primary-700 transition active:scale-95"
                    >
                      <span className="text-lg">🛒</span>
                      <span className="hidden sm:inline">Cart</span>
                      <span className="bg-white/25 px-2 py-0.5 rounded-full text-xs font-extrabold text-white">
                        {cartCount}
                      </span>
                    </Link>
                  )}

                  {/* Profile & Role badge */}
                  <div className="flex items-center gap-2 pl-1">
                    <Link
                      to="/profile"
                      className="hidden xl:flex items-center gap-2 text-left p-1.5 rounded-2xl hover:bg-gray-100 transition"
                    >
                      <div className="h-8 w-8 rounded-full bg-primary-100 text-primary-800 font-bold flex items-center justify-center text-xs">
                        {user?.full_name ? user.full_name.charAt(0).toUpperCase() : "U"}
                      </div>
                      <div className="flex flex-col">
                        <span className="text-xs font-semibold text-gray-800 truncate max-w-[100px]">
                          {user?.full_name?.split(" ")[0]}
                        </span>
                        <span className="text-[10px] font-semibold text-primary-600 uppercase">
                          {user?.role}
                        </span>
                      </div>
                    </Link>

                    {user?.role === "ADMIN" || user?.role === "SUPER_ADMIN" ? (
                      <Link
                        to="/admin"
                        className="hidden lg:inline-flex px-3 py-1.5 rounded-xl bg-amber-100 text-amber-800 text-xs font-bold hover:bg-amber-200 transition"
                      >
                        Admin
                      </Link>
                    ) : user?.role === "VENDOR" ? (
                      <Link
                        to="/seller"
                        className="hidden lg:inline-flex px-3 py-1.5 rounded-xl bg-primary-100 text-primary-800 text-xs font-bold hover:bg-primary-200 transition"
                      >
                        Seller
                      </Link>
                    ) : null}

                  </div>
                </>
              ) : (
                <div className="flex items-center gap-2">
                  <Link
                    to="/login"
                    className="px-4 py-2 text-sm font-semibold text-primary-700 hover:bg-primary-50 rounded-xl transition"
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="btn-primary !py-2 !px-4 !rounded-xl text-sm"
                  >
                    Sign Up
                  </Link>
                </div>
              )}
            </nav>
          </div>




          {/* Mobile Search Bar */}
          {!isPartner && <form onSubmit={handleSearchSubmit} className="mt-3 flex md:hidden relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search groceries..."
              className="w-full rounded-xl border border-gray-200 bg-gray-50 pl-10 pr-20 py-2 text-sm focus:bg-white focus:border-primary-500 focus:outline-none"
            />
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">🔍</span>
            <button
              type="submit"
              className="absolute right-1 top-1/2 -translate-y-1/2 bg-primary-600 text-white text-xs font-semibold px-3 py-1 rounded-lg"
            >
              Search
            </button>
          </form>}
        </div>
      </header>

      {/* Mobile Bottom Floating Nav */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-gray-200 bg-white/95 backdrop-blur py-2 px-4 md:hidden shadow-lg">
        {isPartner ? (
          <div className="grid grid-cols-3 gap-1 text-center text-[11px] font-medium text-gray-600">
            <Link to="/delivery" className="flex flex-col items-center gap-0.5 py-1 text-primary-700 font-bold"><span className="text-base">🚚</span><span>Dashboard</span></Link>
            <Link to="/delivery" className="flex flex-col items-center gap-0.5 py-1 hover:text-primary-700"><span className="text-base">📦</span><span>Deliveries</span></Link>
            <Link to="/profile" className="flex flex-col items-center gap-0.5 py-1 hover:text-primary-700"><span className="text-base">👤</span><span>Profile</span></Link>
          </div>
        ) : (
        <div className="grid grid-cols-4 gap-1 text-center text-[11px] font-medium text-gray-600">
          <Link to="/" className="flex flex-col items-center gap-0.5 py-1 text-primary-700 font-bold">
            <span className="text-base">🏠</span>
            <span>Home</span>
          </Link>
          <Link to="/products" className="flex flex-col items-center gap-0.5 py-1 hover:text-primary-700">
            <span className="text-base">🛍️</span>
            <span>Shop</span>
          </Link>
          <Link to={isCustomer ? "/cart" : isAuthenticated ? "/profile" : "/login"} className="relative flex flex-col items-center gap-0.5 py-1 hover:text-primary-700">
            <span className="text-base">{isCustomer ? "🛒" : isAuthenticated ? "👤" : "🔑"}</span>
            <span>{isCustomer ? "Cart" : isAuthenticated ? "Profile" : "Login"}</span>
            {isCustomer && cartCount > 0 && (
              <span className="absolute top-0 right-4 bg-primary-600 text-white text-[9px] font-extrabold px-1.5 rounded-full">
                {cartCount}
              </span>
            )}
          </Link>
          <Link to={isCustomer ? "/orders" : isAuthenticated ? "/notifications" : "/login"} className="flex flex-col items-center gap-0.5 py-1 hover:text-primary-700">
            <span className="text-base">{isCustomer ? "📦" : isAuthenticated ? "🔔" : "🔑"}</span>
            <span>{isCustomer ? "Orders" : isAuthenticated ? "Alerts" : "Login"}</span>
          </Link>
        </div>
        )}
      </nav>
    </div>
  );
}
