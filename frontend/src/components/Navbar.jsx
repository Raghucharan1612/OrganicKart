import { Link, useNavigate, useSearchParams, useLocation } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import orderService from "@/services/orderService";
import notificationService from "@/services/notificationService";

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const locationState = useLocation();
  const [searchParams] = useSearchParams();
  const [cartCount, setCartCount] = useState(0);
  const [unreadCount, setUnreadCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState(searchParams.get("search") || "");
  const [location] = useState("Bengaluru, 560001");
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const cartRefreshVersion = useRef(0);

  const isCustomer = user?.role === "CUSTOMER";
  const isPartner = user?.role === "DELIVERY_PARTNER";
  const isAdmin = user?.role === "ADMIN" || user?.role === "SUPER_ADMIN";
  const isSeller = user?.role === "VENDOR" || user?.role === "FARMER";

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

  // Auto-close mobile drawer on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [locationState.pathname]);

  // Handle ESC key to close drawer
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") setIsMobileMenuOpen(false);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/products?search=${encodeURIComponent(searchQuery.trim())}`);
    } else {
      navigate("/products");
    }
    setIsMobileMenuOpen(false);
  };

  const handleLogout = () => {
    setIsMobileMenuOpen(false);
    logout();
    navigate("/login");
  };

  return (
    <div className="sticky top-0 z-40 bg-white shadow-xs border-b border-gray-100">
      {/* Top Promotional Bar */}
      <div className="bg-gradient-to-r from-primary-900 via-primary-800 to-primary-950 text-white text-xs py-1.5 px-4 font-medium">
        <div className="mx-auto max-w-7xl flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 bg-primary-700/60 px-2 py-0.5 rounded-full text-[11px] font-semibold text-primary-200">
              ⚡ 10-Min Delivery
            </span>
            <span className="hidden sm:inline text-primary-100">• Fresh & 100% Organic • Best Prices Guaranteed</span>
          </div>
          <div className="flex items-center gap-4 text-primary-100">
            <span className="hidden md:inline">📞 Support: 1800-ORGANIC</span>
            <span className="cursor-pointer hover:text-white transition">🌐 ENG</span>
          </div>
        </div>
      </div>

      {/* Main Navbar Header */}
      <header className="bg-white">
        <div className="mx-auto max-w-7xl px-4 py-3 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between gap-3 md:gap-4">
            {/* Logo */}
            <Link to={isPartner ? "/delivery" : "/"} className="flex items-center gap-2 group shrink-0">
              <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-primary-600 to-primary-800 flex items-center justify-center text-white text-xl shadow-md group-hover:scale-105 transition-transform">
                🌿
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
            {!isPartner && (
              <div className="hidden lg:flex items-center gap-2 rounded-2xl bg-primary-50 px-3.5 py-2 border border-primary-100/80 cursor-pointer hover:bg-primary-100/50 transition">
                <span className="text-lg">📍</span>
                <div className="flex flex-col text-left">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-primary-700">Deliver to</span>
                  <span className="text-xs font-semibold text-gray-800 truncate max-w-[140px]">{location}</span>
                </div>
                <span className="text-xs text-primary-600 font-bold ml-1">▾</span>
              </div>
            )}

            {/* Global Search Bar (Desktop/Tablet) */}
            {!isPartner && (
              <form onSubmit={handleSearchSubmit} className="flex-1 max-w-lg hidden md:flex items-center relative">
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
                    className="absolute right-1.5 top-1/2 -translate-y-1/2 bg-primary-600 text-white text-xs font-semibold px-4 py-1.5 rounded-xl hover:bg-primary-700 transition shadow-xs"
                  >
                    Search
                  </button>
                </div>
              </form>
            )}

            {/* Right Desktop Actions */}
            <nav className="flex items-center gap-2 sm:gap-3">
              {!isPartner && (
                <Link
                  to="/products"
                  className="hidden sm:inline-flex items-center px-3 py-2 text-sm font-semibold text-gray-700 hover:text-primary-700 hover:bg-primary-50 rounded-xl transition"
                >
                  Catalog
                </Link>
              )}

              {isAuthenticated ? (
                <>
                  {isPartner && (
                    <Link to="/delivery" className="hidden md:inline-flex items-center px-3 py-2 text-sm font-semibold text-gray-700 hover:text-primary-700 hover:bg-primary-50 rounded-xl transition">
                      Dashboard
                    </Link>
                  )}
                  {isCustomer && (
                    <Link
                      to="/orders"
                      className="hidden md:inline-flex items-center px-3 py-2 text-sm font-semibold text-gray-700 hover:text-primary-700 hover:bg-primary-50 rounded-xl transition"
                    >
                      Orders
                    </Link>
                  )}

                  {!isPartner && (
                    <Link
                      to="/notifications"
                      className="relative p-2.5 text-gray-700 hover:text-primary-700 hover:bg-primary-50 rounded-2xl transition"
                      title="Notifications"
                    >
                      <span className="text-lg">🔔</span>
                      {unreadCount > 0 && (
                        <span className="absolute top-1.5 right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-amber-500 text-[10px] font-bold text-white shadow-xs ring-2 ring-white">
                          {unreadCount}
                        </span>
                      )}
                    </Link>
                  )}

                  {isCustomer && (
                    <Link
                      to="/cart"
                      className="relative flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-2xl font-semibold text-sm shadow-xs hover:bg-primary-700 transition active:scale-95"
                    >
                      <span className="text-lg">🛒</span>
                      <span className="hidden sm:inline">Cart</span>
                      <span className="bg-white/25 px-2 py-0.5 rounded-full text-xs font-extrabold text-white">
                        {cartCount}
                      </span>
                    </Link>
                  )}

                  {/* Desktop Role badge / Link */}
                  {isAdmin ? (
                    <Link
                      to="/admin"
                      className="hidden lg:inline-flex px-3 py-1.5 rounded-xl bg-amber-100 text-amber-800 text-xs font-bold hover:bg-amber-200 transition"
                    >
                      Admin
                    </Link>
                  ) : isSeller ? (
                    <Link
                      to="/seller"
                      className="hidden lg:inline-flex px-3 py-1.5 rounded-xl bg-primary-100 text-primary-800 text-xs font-bold hover:bg-primary-200 transition"
                    >
                      Seller
                    </Link>
                  ) : null}

                  {/* Desktop Profile Icon */}
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
                </>
              ) : (
                <div className="hidden sm:flex items-center gap-2">
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

              {/* Mobile Drawer Hamburger Button */}
              <button
                type="button"
                onClick={() => setIsMobileMenuOpen((prev) => !prev)}
                className="flex h-10 w-10 items-center justify-center rounded-2xl border border-gray-200 bg-gray-50 text-gray-700 hover:bg-primary-50 hover:text-primary-700 lg:hidden transition"
                aria-label="Toggle Menu"
              >
                <span className="text-xl leading-none">{isMobileMenuOpen ? "✕" : "☰"}</span>
              </button>
            </nav>
          </div>

          {/* Mobile Search Bar */}
          {!isPartner && (
            <form onSubmit={handleSearchSubmit} className="mt-3 flex md:hidden relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search fresh groceries..."
                className="w-full rounded-xl border border-gray-200 bg-gray-50 pl-10 pr-20 py-2 text-sm focus:bg-white focus:border-primary-500 focus:outline-none"
              />
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">🔍</span>
              <button
                type="submit"
                className="absolute right-1 top-1/2 -translate-y-1/2 bg-primary-600 text-white text-xs font-semibold px-3 py-1 rounded-lg"
              >
                Search
              </button>
            </form>
          )}
        </div>
      </header>

      {/* ========================================================================= */}
      {/* MOBILE SLIDE-OVER NAVIGATION DRAWER */}
      {/* ========================================================================= */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 overflow-hidden lg:hidden animate-fade-in">
          {/* Backdrop Overlay */}
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-xs transition-opacity"
            onClick={() => setIsMobileMenuOpen(false)}
          />

          {/* Slide-over Panel */}
          <aside className="fixed inset-y-0 right-0 max-w-full flex pl-10 animate-slide-in-right">
            <div className="w-screen max-w-xs bg-white shadow-2xl flex flex-col justify-between">
              {/* Top Drawer Header */}
              <div className="p-5 border-b border-gray-100 flex items-center justify-between bg-primary-50/50">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">🌿</span>
                  <span className="font-display font-bold text-lg text-primary-900">OrganicKart</span>
                </div>
                <button
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="h-9 w-9 rounded-xl border border-gray-200 bg-white flex items-center justify-center text-gray-500 hover:text-gray-900 transition"
                  aria-label="Close menu"
                >
                  ✕
                </button>
              </div>

              {/* Drawer Content Body (Scrollable) */}
              <div className="flex-1 overflow-y-auto p-5 space-y-6">
                {/* User Status Card */}
                {isAuthenticated ? (
                  <div className="rounded-2xl border border-primary-100 bg-primary-50/60 p-4 flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-primary-600 text-white font-bold flex items-center justify-center text-sm shadow-xs">
                      {user?.full_name ? user.full_name.charAt(0).toUpperCase() : "U"}
                    </div>
                    <div className="flex flex-col min-w-0">
                      <span className="font-bold text-sm text-gray-900 truncate">{user?.full_name}</span>
                      <span className="text-xs text-gray-500 truncate">{user?.email}</span>
                      <span className="inline-block mt-1 text-[10px] font-extrabold uppercase tracking-wider text-primary-700">
                        Role: {user?.role}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="rounded-2xl border border-gray-100 bg-gray-50 p-4 text-center space-y-3">
                    <p className="text-xs font-semibold text-gray-600">Sign in to manage orders & express checkout</p>
                    <div className="flex gap-2">
                      <Link to="/login" className="btn-secondary flex-1 !py-1.5 text-xs">Login</Link>
                      <Link to="/register" className="btn-primary flex-1 !py-1.5 text-xs">Sign Up</Link>
                    </div>
                  </div>
                )}

                {/* Navigation Group: Main */}
                <div className="space-y-1">
                  <h4 className="text-[10px] font-extrabold uppercase tracking-widest text-gray-400 px-2 mb-2">Navigation</h4>
                  {!isPartner && (
                    <Link
                      to="/"
                      className="flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-800 transition"
                    >
                      <span className="text-lg">🏠</span> Home
                    </Link>
                  )}
                  {!isPartner && (
                    <Link
                      to="/products"
                      className="flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-800 transition"
                    >
                      <span className="text-lg">📦</span> Shop Catalog
                    </Link>
                  )}
                </div>

                {/* Role Specific Actions */}
                {isAuthenticated && (
                  <div className="space-y-1 border-t border-gray-100 pt-4">
                    <h4 className="text-[10px] font-extrabold uppercase tracking-widest text-gray-400 px-2 mb-2">
                      {isCustomer ? "Customer Dashboard" : isSeller ? "Seller Portal" : isPartner ? "Delivery Portal" : "Admin Panel"}
                    </h4>

                    {isCustomer && (
                      <>
                        <Link
                          to="/cart"
                          className="flex items-center justify-between px-3 py-2.5 rounded-xl font-semibold text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-800 transition"
                        >
                          <span className="flex items-center gap-3"><span className="text-lg">🛒</span> Shopping Cart</span>
                          {cartCount > 0 && (
                            <span className="bg-primary-600 text-white text-xs font-bold px-2 py-0.5 rounded-full">{cartCount}</span>
                          )}
                        </Link>
                        <Link
                          to="/orders"
                          className="flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-800 transition"
                        >
                          <span className="text-lg">📋</span> My Orders
                        </Link>
                      </>
                    )}

                    {isSeller && (
                      <Link
                        to="/seller"
                        className="flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-800 transition"
                      >
                        <span className="text-lg">🌾</span> Seller Dashboard
                      </Link>
                    )}

                    {isPartner && (
                      <Link
                        to="/delivery"
                        className="flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-800 transition"
                      >
                        <span className="text-lg">🚚</span> Active Deliveries
                      </Link>
                    )}

                    {isAdmin && (
                      <>
                        <Link
                          to="/admin"
                          className="flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-800 transition"
                        >
                          <span className="text-lg">🛡️</span> Admin Dashboard
                        </Link>
                        <Link
                          to="/admin/categories"
                          className="flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-800 transition"
                        >
                          <span className="text-lg">🏷️</span> Category Taxonomy
                        </Link>
                      </>
                    )}

                    <Link
                      to="/notifications"
                      className="flex items-center justify-between px-3 py-2.5 rounded-xl font-semibold text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-800 transition"
                    >
                      <span className="flex items-center gap-3"><span className="text-lg">🔔</span> Notifications</span>
                      {unreadCount > 0 && (
                        <span className="bg-amber-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">{unreadCount}</span>
                      )}
                    </Link>
                  </div>
                )}

                {/* Account Section */}
                {isAuthenticated && (
                  <div className="space-y-1 border-t border-gray-100 pt-4">
                    <h4 className="text-[10px] font-extrabold uppercase tracking-widest text-gray-400 px-2 mb-2">Account</h4>
                    <Link
                      to="/profile"
                      className="flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-800 transition"
                    >
                      <span className="text-lg">👤</span> User Profile & Settings
                    </Link>
                  </div>
                )}
              </div>

              {/* Bottom Drawer Footer */}
              {isAuthenticated && (
                <div className="p-5 border-t border-gray-100 bg-gray-50/50">
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center justify-center gap-2 rounded-xl border border-red-200 bg-red-50 py-2.5 text-sm font-bold text-red-600 hover:bg-red-100 transition"
                  >
                    🚪 Log Out
                  </button>
                </div>
              )}
            </div>
          </aside>
        </div>
      )}

      {/* Mobile Bottom Floating Nav */}
      <nav className="fixed bottom-0 left-0 right-0 z-40 border-t border-gray-200 bg-white/95 backdrop-blur py-2 px-4 md:hidden shadow-lg">
        {isPartner ? (
          <div className="grid grid-cols-3 gap-1 text-center text-[11px] font-medium text-gray-600">
            <Link to="/delivery" className="flex flex-col items-center gap-0.5 py-1 text-primary-700 font-bold"><span className="text-base">📊</span><span>Dashboard</span></Link>
            <Link to="/delivery" className="flex flex-col items-center gap-0.5 py-1 hover:text-primary-700"><span className="text-base">🚚</span><span>Deliveries</span></Link>
            <Link to="/profile" className="flex flex-col items-center gap-0.5 py-1 hover:text-primary-700"><span className="text-base">👤</span><span>Profile</span></Link>
          </div>
        ) : (
          <div className="grid grid-cols-4 gap-1 text-center text-[11px] font-medium text-gray-600">
            <Link to="/" className="flex flex-col items-center gap-0.5 py-1 text-primary-700 font-bold">
              <span className="text-base">🏠</span>
              <span>Home</span>
            </Link>
            <Link to="/products" className="flex flex-col items-center gap-0.5 py-1 hover:text-primary-700">
              <span className="text-base">📦</span>
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
              <span className="text-base">{isCustomer ? "📋" : isAuthenticated ? "🔔" : "🔑"}</span>
              <span>{isCustomer ? "Orders" : isAuthenticated ? "Alerts" : "Login"}</span>
            </Link>
          </div>
        )}
      </nav>
    </div>
  );
}
