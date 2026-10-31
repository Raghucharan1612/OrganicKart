import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import categoryService from "@/services/categoryService";
import productService from "@/services/productService";
import Spinner from "@/components/Spinner";
import ProductCard from "@/features/catalog/components/ProductCard";

const CATEGORY_ICON = {
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

const PROMO_CARDS = [
  {
    id: 1,
    title: "Fruits & Vegetables",
    discount: "UP TO 40% OFF",
    subtitle: "Farm fresh, hand-picked daily",
    bg: "from-primary-900 via-primary-800 to-emerald-900",
    badgeBg: "bg-amber-400 text-primary-950",
    icon: "🍎🥦",
    categoryId: null,
  },
  {
    id: 2,
    title: "Dairy Essentials",
    discount: "UP TO 30% OFF",
    subtitle: "Pure A2 milk, butter & paneer",
    bg: "from-emerald-900 via-emerald-800 to-primary-950",
    badgeBg: "bg-emerald-400 text-slate-900",
    icon: "🥛🧀",
    categoryId: null,
  },
  {
    id: 3,
    title: "Organic Staples",
    discount: "FLAT ₹100 OFF",
    subtitle: "Unpolished pulses & cold-pressed oils",
    bg: "from-primary-950 via-primary-900 to-primary-900",
    badgeBg: "bg-emerald-300 text-primary-950",
    icon: "🌾🫒",
    categoryId: null,
  },
  {
    id: 4,
    title: "Fresh & Healthy",
    discount: "BEST DEALS",
    subtitle: "Organic honey, beverages & snacks",
    bg: "from-primary-900 via-primary-900 to-slate-900",
    badgeBg: "bg-amber-300 text-primary-950",
    icon: "🍯🧃",
    categoryId: null,
  },
];

const BEST_SELLER_ROW_COUNT = 5;
const PRODUCTS_PER_ROW = 6;

const getCatalogItems = (data) =>
  Array.isArray(data?.items) ? data.items : Array.isArray(data) ? data : [];

const splitBestSellerRows = (products) =>
  Array.from({ length: BEST_SELLER_ROW_COUNT }, (_, rowIndex) =>
    products.slice(rowIndex * PRODUCTS_PER_ROW, (rowIndex + 1) * PRODUCTS_PER_ROW)
  );

function CategoryCardItem({ category }) {
  const [imageError, setImageError] = useState(false);

  return (
    <Link
      to={`/products?category_id=${category.id}`}
      className="group flex flex-col items-center justify-between rounded-2xl border border-gray-100 bg-primary-50/20 p-3 text-center transition-all duration-200 hover:-translate-y-0.5 hover:border-primary-300 hover:bg-white hover:shadow-md shrink-0 w-[calc((100%-2*0.75rem)/3)] sm:w-[calc((100%-3*0.75rem)/4)] md:w-[calc((100%-4*1rem)/5)] lg:w-[calc((100%-5*1rem)/6)] xl:w-[calc((100%-6*1rem)/7)] h-[174px]"
    >
      <div className="flex h-16 w-16 shrink-0 items-center justify-center overflow-hidden rounded-2xl bg-white shadow-xs group-hover:scale-105 transition-transform">
        {category.image_url && !imageError ? (
          <img
            src={category.image_url}
            alt={category.name}
            className="h-full w-full object-cover"
            loading="lazy"
            decoding="async"
            width="64"
            height="64"
            onError={() => setImageError(true)}
          />
        ) : (
          <span className="text-3xl">{CATEGORY_ICON[category.name] || "🌿"}</span>
        )}
      </div>
      <div className="flex h-10 w-full items-center justify-center px-1">
        <p className="text-xs font-bold text-gray-800 group-hover:text-primary-700 transition line-clamp-2 leading-tight text-center">
          {category.name}
        </p>
      </div>
      <span className="text-[10px] font-medium text-gray-400 shrink-0">100% Organic</span>
    </Link>
  );
}

export default function HomePage() {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [bestSellerRows, setBestSellerRows] = useState(() => splitBestSellerRows([]));
  const [isBestSellersLoading, setIsBestSellersLoading] = useState(true);
  const [bestSellersError, setBestSellersError] = useState("");
  const categoryScrollRef = useRef(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  const updateCategoryScrollState = () => {
    const el = categoryScrollRef.current;
    if (!el) return;
    const { scrollLeft, scrollWidth, clientWidth } = el;
    setCanScrollLeft(scrollLeft > 6);
    setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 6);
  };

  useEffect(() => {
    const el = categoryScrollRef.current;
    if (!el) return;
    updateCategoryScrollState();
    el.addEventListener("scroll", updateCategoryScrollState, { passive: true });
    window.addEventListener("resize", updateCategoryScrollState);
    return () => {
      el.removeEventListener("scroll", updateCategoryScrollState);
      window.removeEventListener("resize", updateCategoryScrollState);
    };
  }, [categories]);

  const scrollCategories = (dir) => {
    const el = categoryScrollRef.current;
    if (!el) return;
    const cardEl = el.querySelector("a");
    const cardWidth = cardEl ? cardEl.offsetWidth + 16 : 220;
    el.scrollBy({ left: dir * cardWidth * 3, behavior: "smooth" });
  };

  const loadBestSellers = () => {
    setIsBestSellersLoading(true);
    setBestSellersError("");

    productService
      .list({ page: 1, page_size: 100, sort_by: "created_at", sort_order: "desc" })
      .then((catalogData) => {
        const seenProductIds = new Set();
        const visibleProducts = getCatalogItems(catalogData)
          .filter((product) => product.is_active !== false && product.certification === "APPROVED")
          .filter((product) => {
            if (seenProductIds.has(product.id)) return false;
            seenProductIds.add(product.id);
            return true;
          })
          .slice(0, BEST_SELLER_ROW_COUNT * PRODUCTS_PER_ROW);
        setBestSellerRows(splitBestSellerRows(visibleProducts));
      })
      .catch(() => {
        setBestSellersError("Unable to load products right now.");
        setBestSellerRows(splitBestSellerRows([]));
      })
      .finally(() => setIsBestSellersLoading(false));
  };

  useEffect(() => {
    let active = true;
    categoryService.list()
      .then((categoryData) => {
        if (active) setCategories(Array.isArray(categoryData) ? categoryData : []);
      })
      .catch(() => {
        if (active) setCategories([]);
      });
    loadBestSellers();

    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="min-h-screen bg-cream flex flex-col">
      {/* Category Navigation Bar (Horizontally Scrollable) */}
      <div className="border-b border-gray-200/80 bg-white sticky top-[105px] z-30 shadow-xs">
        <div className="mx-auto w-full max-w-[1440px] px-4 py-2.5 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2 overflow-x-auto no-scrollbar scroll-smooth py-1">
            <Link
              to="/products"
              className="flex shrink-0 items-center gap-1.5 rounded-full bg-primary-600 px-4 py-1.5 text-xs font-bold text-white shadow-xs hover:bg-primary-700 transition"
            >
              <span>🌿</span>
              <span>All Categories</span>
            </Link>
            {categories.map((cat) => (
              <Link
                key={cat.id}
                to={`/products?category_id=${cat.id}`}
                className="flex shrink-0 items-center gap-1.5 rounded-full border border-gray-200 bg-gray-50/80 px-3.5 py-1.5 text-xs font-semibold text-gray-700 hover:border-primary-300 hover:bg-primary-50 hover:text-primary-800 transition"
              >
                <span>{CATEGORY_ICON[cat.name] || "📦"}</span>
                <span>{cat.name}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>

      <div className="mx-auto flex w-full max-w-[1440px] flex-1 flex-col space-y-10 px-4 py-6 sm:px-6 lg:px-8">
        {/* HERO SECTION */}
        <section className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-primary-950 via-primary-900 to-primary-950 p-6 sm:p-10 text-white shadow-xl">
          {/* Subtle background glow circles */}
          <div className="absolute -right-10 -top-10 h-64 w-64 rounded-full bg-primary-500/20 blur-3xl" />
          <div className="absolute -left-10 -bottom-10 h-64 w-64 rounded-full bg-emerald-500/20 blur-3xl" />

          <div className="relative z-10 grid gap-8 lg:grid-cols-[1.3fr_0.7fr] lg:items-center">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-3.5 py-1.5 text-xs font-bold uppercase tracking-wider text-accent-300 backdrop-blur border border-white/10">
                ⚡ Delivered in 10 minutes • 100% Certified Organic
              </div>

              <h1 className="mt-4 font-display text-3xl font-extrabold tracking-tight sm:text-5xl leading-tight">
                Organically Fresh. <br className="hidden sm:inline" />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-emerald-300 to-primary-100">
                  Delivered Fast. ⚡
                </span>
              </h1>

              <p className="mt-4 max-w-xl text-base text-primary-100/90 leading-relaxed">
                {isAuthenticated
                  ? `Welcome back, ${user?.full_name?.split(" ")[0]}! Get farm-fresh fruits, vegetables, dairy & organic staples delivered right to your doorstep.`
                  : "Fresh fruits, vegetables, pure dairy & certified organic daily essentials at your doorstep in minutes."}
              </p>

              <div className="mt-6 flex flex-wrap gap-3">
                <Link to="/products" className="btn-primary !bg-white !text-primary-950 hover:!bg-amber-300 font-extrabold text-sm !px-6 !py-3 shadow-lg">
                  Shop Now →
                </Link>
                {isAuthenticated ? (
                  <Link to="/orders" className="btn-secondary !bg-white/10 !text-white !border-white/20 hover:!bg-white/20 text-sm !px-5 !py-3">
                    View Orders
                  </Link>
                ) : (
                  <Link to="/register" className="btn-secondary !bg-white/10 !text-white !border-white/20 hover:!bg-white/20 text-sm !px-5 !py-3">
                    Get Started
                  </Link>
                )}
              </div>

              {/* Stats Bar */}
              <div className="mt-8 grid grid-cols-3 gap-3 border-t border-white/10 pt-6 text-xs text-primary-100">
                <div>
                  <div className="font-display text-2xl font-extrabold text-white">500+</div>
                  <div className="mt-0.5 text-primary-100/80">Organic Items</div>
                </div>
                <div>
                  <div className="font-display text-2xl font-extrabold text-amber-300">10 Min</div>
                  <div className="mt-0.5 text-primary-100/80">Express Delivery</div>
                </div>
                <div>
                  <div className="font-display text-2xl font-extrabold text-emerald-300">4.9 ★</div>
                  <div className="mt-0.5 text-primary-100/80">Customer Rating</div>
                </div>
              </div>
            </div>

            {/* Hero Quick Spotlight */}
            <div className="rounded-2xl bg-white/10 p-5 backdrop-blur border border-white/15 hidden lg:block shadow-2xl">
              <div className="flex items-center justify-between text-xs text-primary-100 border-b border-white/10 pb-3">
                <span className="font-semibold">⚡ Instant Slot Available</span>
                <span className="rounded-full bg-emerald-400/20 px-2 py-0.5 text-emerald-300 font-bold">Live</span>
              </div>

              <div className="mt-4 space-y-3">
                <div className="flex items-center gap-3 rounded-xl bg-white/10 p-2.5 backdrop-blur">
                  <div className="text-2xl">🍎</div>
                  <div className="min-w-0 flex-1">
                    <p className="font-semibold text-sm text-white truncate">Organic Shimla Apples</p>
                    <p className="text-xs text-amber-300 font-bold">₹140.00 / 1 kg</p>
                  </div>
                  <span className="text-[10px] font-bold bg-amber-400 text-primary-950 px-2 py-1 rounded-md">40% OFF</span>
                </div>
                <div className="flex items-center gap-3 rounded-xl bg-white/10 p-2.5 backdrop-blur">
                  <div className="text-2xl">🥛</div>
                  <div className="min-w-0 flex-1">
                    <p className="font-semibold text-sm text-white truncate">Farm Fresh A2 Cow Milk</p>
                    <p className="text-xs text-emerald-300 font-bold">₹65.00 / 1 Litre</p>
                  </div>
                  <span className="text-[10px] font-bold bg-emerald-400 text-slate-900 px-2 py-1 rounded-md">Pure</span>
                </div>
                <div className="flex items-center gap-3 rounded-xl bg-white/10 p-2.5 backdrop-blur">
                  <div className="text-2xl">🥦</div>
                  <div className="min-w-0 flex-1">
                    <p className="font-semibold text-sm text-white truncate">Fresh Organic Broccoli</p>
                    <p className="text-xs text-primary-100 font-bold">₹55.00 / 250g</p>
                  </div>
                  <span className="text-[10px] font-bold bg-white/20 text-white px-2 py-1 rounded-md">Organic</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* PROMOTIONAL CARDS */}
        <section>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {PROMO_CARDS.map((card) => (
              <div
                key={card.id}
                onClick={() => navigate("/products")}
                className={`group relative overflow-hidden rounded-2xl bg-gradient-to-br ${card.bg} p-5 text-white shadow-md cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-xl flex flex-col justify-between min-h-[160px]`}
              >
                <div>
                  <div className="flex items-start justify-between">
                    <span className={`rounded-lg ${card.badgeBg} px-2.5 py-1 text-[10px] font-extrabold uppercase shadow-xs`}>
                      {card.discount}
                    </span>
                    <span className="text-3xl group-hover:scale-110 transition-transform">{card.icon}</span>
                  </div>

                  <h3 className="mt-3 font-display text-lg font-bold text-white">{card.title}</h3>
                  <p className="mt-1 text-xs text-primary-100">{card.subtitle}</p>
                </div>

                <div className="mt-4 flex items-center gap-1 text-xs font-bold text-amber-300 group-hover:underline">
                  <span>Shop Category</span>
                  <span>→</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* SHOP BY CATEGORY — responsive horizontal carousel with arrows */}
        <section className="rounded-3xl border border-gray-100 bg-white p-6 shadow-xs">
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <div>
              <span className="text-xs font-extrabold uppercase tracking-widest text-primary-600">Categories</span>
              <h2 className="mt-1 font-display text-2xl font-bold text-gray-900">Explore Fresh Categories</h2>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => scrollCategories(-1)}
                disabled={!canScrollLeft}
                aria-label="Previous categories"
                className="flex h-8 w-8 items-center justify-center rounded-full border border-gray-200 bg-white text-gray-600 shadow-xs transition hover:border-primary-400 hover:bg-primary-50 hover:text-primary-700 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:border-gray-200 disabled:hover:bg-white disabled:hover:text-gray-600"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <button
                type="button"
                onClick={() => scrollCategories(1)}
                disabled={!canScrollRight}
                aria-label="Next categories"
                className="flex h-8 w-8 items-center justify-center rounded-full border border-gray-200 bg-white text-gray-600 shadow-xs transition hover:border-primary-400 hover:bg-primary-50 hover:text-primary-700 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:border-gray-200 disabled:hover:bg-white disabled:hover:text-gray-600"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
                </svg>
              </button>
              <Link to="/products" className="ml-1 text-sm font-bold text-primary-700 hover:text-primary-900 transition flex items-center gap-1">
                <span>See All ({categories.length})</span>
                <span>→</span>
              </Link>
            </div>
          </div>

          <div
            ref={categoryScrollRef}
            className="flex gap-3 sm:gap-3 md:gap-4 overflow-x-auto no-scrollbar scroll-smooth pb-1"
          >
            {categories.map((category) => (
              <CategoryCardItem key={category.id} category={category} />
            ))}
          </div>
        </section>

        {/* BEST SELLERS */}
        <section className="space-y-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <span className="text-xs font-extrabold uppercase tracking-widest text-primary-600">Fresh picks</span>
              <h2 className="mt-1 font-display text-2xl font-bold text-gray-900">Best Sellers</h2>
            </div>
            <Link to="/products" className="shrink-0 text-sm font-bold text-primary-700 transition hover:text-primary-900">
              View Catalog <span aria-hidden="true">→</span>
            </Link>
          </div>

          {isBestSellersLoading ? (
            <div className="rounded-2xl border border-gray-100 bg-white py-12 shadow-xs">
              <Spinner label="Loading products…" />
            </div>
          ) : bestSellersError ? (
            <div className="rounded-2xl border border-red-100 bg-red-50/50 px-6 py-10 text-center">
              <p className="text-sm font-semibold text-red-600">{bestSellersError}</p>
              <button
                type="button"
                onClick={loadBestSellers}
                className="mt-3 rounded-xl bg-primary-600 px-4 py-2 text-xs font-bold text-white shadow-xs transition hover:bg-primary-700"
              >
                Retry
              </button>
            </div>
          ) : (
            <div className="space-y-5">
              {bestSellerRows.map((products, rowIndex) => (
                <div key={rowIndex} className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-6 lg:gap-4">
                  {products.map((product) => (
                    <ProductCard key={product.id} product={product} />
                  ))}
                </div>
              ))}
            </div>
          )}
        </section>

        {/* WHY ORGANICKART */}
        <section className="rounded-3xl bg-gradient-to-br from-primary-900 to-primary-950 p-8 text-white shadow-lg">
          <div className="text-center max-w-2xl mx-auto">
            <span className="rounded-full bg-accent-400/20 px-3 py-1 text-xs font-bold text-accent-300 border border-accent-400/30 uppercase tracking-widest">
              Why Choose Us
            </span>
            <h2 className="mt-3 font-display text-2xl sm:text-3xl font-extrabold">The OrganicKart Advantage</h2>
            <p className="mt-2 text-sm text-primary-100">
              We bring farm-fresh organic produce directly from certified growers to your kitchen with guaranteed freshness.
            </p>
          </div>

          <div className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            <div className="rounded-2xl bg-white/10 p-4 text-center backdrop-blur border border-white/10 hover:bg-white/15 transition">
              <div className="text-3xl">⚡</div>
              <h4 className="mt-2 text-sm font-bold text-white">10-Min Delivery</h4>
              <p className="mt-1 text-[11px] text-primary-100">Lightning fast doorstep fulfillment</p>
            </div>
            <div className="rounded-2xl bg-white/10 p-4 text-center backdrop-blur border border-white/10 hover:bg-white/15 transition">
              <div className="text-3xl">🥬</div>
              <h4 className="mt-2 text-sm font-bold text-white">100% Certified</h4>
              <p className="mt-1 text-[11px] text-primary-100">Strict lab & admin verified organic</p>
            </div>
            <div className="rounded-2xl bg-white/10 p-4 text-center backdrop-blur border border-white/10 hover:bg-white/15 transition">
              <div className="text-3xl">💰</div>
              <h4 className="mt-2 text-sm font-bold text-white">Best Prices</h4>
              <p className="mt-1 text-[11px] text-primary-100">Direct grower rates without middlemen</p>
            </div>
            <div className="rounded-2xl bg-white/10 p-4 text-center backdrop-blur border border-white/10 hover:bg-white/15 transition">
              <div className="text-3xl">🔒</div>
              <h4 className="mt-2 text-sm font-bold text-white">Safe & Secure</h4>
              <p className="mt-1 text-[11px] text-primary-100">JWT protected digital transactions</p>
            </div>
            <div className="rounded-2xl bg-white/10 p-4 text-center backdrop-blur border border-white/10 hover:bg-white/15 transition">
              <div className="text-3xl">↩</div>
              <h4 className="mt-2 text-sm font-bold text-white">Easy Returns</h4>
              <p className="mt-1 text-[11px] text-primary-100">No questions asked return policy</p>
            </div>
            <div className="rounded-2xl bg-white/10 p-4 text-center backdrop-blur border border-white/10 hover:bg-white/15 transition">
              <div className="text-3xl">💬</div>
              <h4 className="mt-2 text-sm font-bold text-white">24/7 Support</h4>
              <p className="mt-1 text-[11px] text-primary-100">Instant dedicated assistance</p>
            </div>
          </div>
        </section>
      </div>

    </div>
  );
}
