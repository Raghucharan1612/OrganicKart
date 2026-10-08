import { Link, useLocation } from "react-router-dom";

const NAV_ITEMS = [
  { label: "Dashboard", href: "/seller", tab: "overview" },
  { label: "Products", href: "/seller/products", tab: "products" },
  { label: "Orders", href: null, tab: "orders" },
  { label: "Certification", href: null, tab: "certifications" },
  { label: "Analytics", href: null, tab: "analytics" },
];

/**
 * SellerSubNav — Compact secondary horizontal navigation bar shown below the main Navbar
 * for VENDOR and FARMER users.
 */
export default function SellerSubNav({ activeTab, onTabChange, pendingCount = 0 }) {
  const location = useLocation();

  const isProductsPage = location.pathname.startsWith("/seller/products");

  const handleItemClick = (item) => {
    if (item.href === null && onTabChange) {
      onTabChange(item.tab);
    }
  };

  const isActive = (item) => {
    if (item.tab === "products" && isProductsPage) return true;
    if (item.tab === "overview" && location.pathname === "/seller" && activeTab === "overview") return true;
    return !isProductsPage && activeTab === item.tab;
  };

  return (
    <div className="bg-white border-b border-slate-200 shadow-2xs">
      <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-10 2xl:px-12 flex items-center justify-between">
        {/* Horizontal scrollable nav tabs */}
        <nav
          className="flex items-center space-x-1 sm:space-x-2 overflow-x-auto scrollbar-hide py-2"
          aria-label="Seller navigation"
        >
          {NAV_ITEMS.map((item) => {
            const active = isActive(item);

            if (item.href && item.tab !== "overview") {
              return (
                <Link
                  key={item.tab}
                  to={item.href}
                  className={`inline-flex items-center gap-1.5 whitespace-nowrap px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all shrink-0 ${
                    active
                      ? "bg-emerald-50 text-emerald-800 border border-emerald-200/80 shadow-2xs"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                  }`}
                >
                  <span>{item.label}</span>
                </Link>
              );
            }

            if (item.tab === "overview") {
              return (
                <Link
                  key={item.tab}
                  to="/seller"
                  onClick={() => onTabChange && onTabChange("overview")}
                  className={`inline-flex items-center gap-1.5 whitespace-nowrap px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all shrink-0 ${
                    active
                      ? "bg-emerald-50 text-emerald-800 border border-emerald-200/80 shadow-2xs"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                  }`}
                >
                  <span>{item.label}</span>
                </Link>
              );
            }

            return (
              <button
                key={item.tab}
                type="button"
                onClick={() => handleItemClick(item)}
                className={`inline-flex items-center gap-1.5 whitespace-nowrap px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all shrink-0 ${
                  active
                    ? "bg-emerald-50 text-emerald-800 border border-emerald-200/80 shadow-2xs"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <span>{item.label}</span>
                {item.tab === "certifications" && pendingCount > 0 && (
                  <span className="rounded-full bg-amber-500 text-white text-[10px] font-bold px-1.5 py-0.2 leading-none">
                    {pendingCount}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
}

