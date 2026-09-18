import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import productService from "@/services/productService";
import categoryService from "@/services/categoryService";
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
    bg: "from-purple-900 via-primary-800 to-indigo-900",
    badgeBg: "bg-amber-400 text-purple-950",
    icon: "🍎🥦",
    categoryId: null,
  },
  {
    id: 2,
    title: "Dairy Essentials",
    discount: "UP TO 30% OFF",
    subtitle: "Pure A2 milk, butter & paneer",
    bg: "from-indigo-900 via-purple-800 to-purple-950",
    badgeBg: "bg-emerald-400 text-slate-900",
    icon: "🥛🧀",
    categoryId: null,
  },
  {
    id: 3,
    title: "Organic Staples",
    discount: "FLAT ₹100 OFF",
    subtitle: "Unpolished pulses & cold-pressed oils",
    bg: "from-purple-950 via-primary-900 to-purple-900",
    badgeBg: "bg-purple-300 text-purple-950",
    icon: "🌾🫒",
    categoryId: null,
  },
  {
    id: 4,
    title: "Fresh & Healthy",
    discount: "BEST DEALS",
    subtitle: "Organic honey, beverages & snacks",
    bg: "from-primary-900 via-purple-900 to-slate-900",
    badgeBg: "bg-amber-300 text-purple-950",
    icon: "🍯🧃",
    categoryId: null,
  },
];

export default function HomePage() {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [featured, setFeatured] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;

    Promise.all([
      categoryService.list().catch(() => []),
      productService.list({ certification: "APPROVED", page: 1, page_size: 8, sort_by: "created_at", sort_order: "desc" }).catch(() => ({ items: [] })),
    ])
      .then(([categoriesData, productsData]) => {
        if (!active) return;
        setCategories(Array.isArray(categoriesData) ? categoriesData : []);
        const items = Array.isArray(productsData?.items) ? productsData.items : Array.isArray(productsData) ? productsData : [];
        setFeatured(items);
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="min-h-screen bg-cream flex flex-col">
      {/* Category Navigation Bar (Horizontally Scrollable) */}
      <div className="border-b border-gray-200/80 bg-white sticky top-[105px] z-30 shadow-xs">
        <div className="mx-auto max-w-7xl px-4 py-2.5 sm:px-6 lg:px-8">
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

      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 space-y-10 flex-1 w-full">
        {/* HERO SECTION */}
        <section className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-purple-950 via-primary-900 to-indigo-950 p-6 sm:p-10 text-white shadow-xl">
          {/* Subtle background glow circles */}
          <div className="absolute -right-10 -top-10 h-64 w-64 rounded-full bg-primary-500/20 blur-3xl" />
          <div className="absolute -left-10 -bottom-10 h-64 w-64 rounded-full bg-purple-500/20 blur-3xl" />

          <div className="relative z-10 grid gap-8 lg:grid-cols-[1.3fr_0.7fr] lg:items-center">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-3.5 py-1.5 text-xs font-bold uppercase tracking-wider text-accent-300 backdrop-blur border border-white/10">
                ⚡ Delivered in 10 minutes • 100% Certified Organic
              </div>

              <h1 className="mt-4 font-display text-3xl font-extrabold tracking-tight sm:text-5xl leading-tight">
                Organically Fresh. <br className="hidden sm:inline" />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-emerald-300 to-purple-200">
                  Delivered Fast. ⚡
                </span>
              </h1>

              <p className="mt-4 max-w-xl text-base text-purple-100/90 leading-relaxed">
                {isAuthenticated
                  ? `Welcome back, ${user?.full_name?.split(" ")[0]}! Get farm-fresh fruits, vegetables, dairy & organic staples delivered right to your doorstep.`
                  : "Fresh fruits, vegetables, pure dairy & certified organic daily essentials at your doorstep in minutes."}
              </p>

              <div className="mt-6 flex flex-wrap gap-3">
                <Link to="/products" className="btn-primary !bg-white !text-purple-950 hover:!bg-amber-300 font-extrabold text-sm !px-6 !py-3 shadow-lg">
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
              <div className="mt-8 grid grid-cols-3 gap-3 border-t border-white/10 pt-6 text-xs text-purple-200">
                <div>
                  <div className="font-display text-2xl font-extrabold text-white">500+</div>
                  <div className="mt-0.5 text-purple-200/80">Organic Items</div>
                </div>
                <div>
                  <div className="font-display text-2xl font-extrabold text-amber-300">10 Min</div>
                  <div className="mt-0.5 text-purple-200/80">Express Delivery</div>
                </div>
                <div>
                  <div className="font-display text-2xl font-extrabold text-emerald-300">4.9 ★</div>
                  <div className="mt-0.5 text-purple-200/80">Customer Rating</div>
                </div>
              </div>
            </div>

            {/* Hero Quick Spotlight */}
            <div className="rounded-2xl bg-white/10 p-5 backdrop-blur border border-white/15 hidden lg:block shadow-2xl">
              <div className="flex items-center justify-between text-xs text-purple-200 border-b border-white/10 pb-3">
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
                  <span className="text-[10px] font-bold bg-amber-400 text-purple-950 px-2 py-1 rounded-md">40% OFF</span>
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
                    <p className="text-xs text-purple-200 font-bold">₹55.00 / 250g</p>
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
                className={`group relative overflow-hidden rounded-2xl bg-gradient-to-br ${card.bg} p-5 text-white shadow-md cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-xl`}
              >
                <div className="flex items-start justify-between">
                  <span className={`rounded-lg ${card.badgeBg} px-2.5 py-1 text-[10px] font-extrabold uppercase shadow-sm`}>
                    {card.discount}
                  </span>
                  <span className="text-3xl group-hover:scale-110 transition-transform">{card.icon}</span>
                </div>

                <h3 className="mt-4 font-display text-lg font-bold text-white">{card.title}</h3>
                <p className="mt-1 text-xs text-purple-200">{card.subtitle}</p>

                <div className="mt-4 flex items-center gap-1 text-xs font-bold text-amber-300 group-hover:underline">
                  <span>Shop Category</span>
                  <span>→</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* SHOP BY CATEGORY */}
        <section className="rounded-3xl border border-gray-100 bg-white p-6 shadow-sm">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <span className="text-xs font-extrabold uppercase tracking-widest text-primary-600">Categories</span>
              <h2 className="mt-1 font-display text-2xl font-bold text-gray-900">Explore Fresh Categories</h2>
            </div>
            <Link to="/products" className="text-sm font-bold text-primary-700 hover:text-primary-900 transition">
              See All ({categories.length}) →
            </Link>
          </div>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
            {categories.map((category) => (
              <Link
                key={category.id}
                to={`/products?category_id=${category.id}`}
                className="group flex flex-col items-center rounded-2xl border border-gray-100 bg-primary-50/30 p-4 text-center transition-all duration-200 hover:border-primary-300 hover:bg-white hover:shadow-md"
              >
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white text-3xl shadow-sm group-hover:scale-110 transition-transform">
                  {CATEGORY_ICON[category.name] || "🌿"}
                </div>
                <p className="mt-3 text-sm font-bold text-gray-800 group-hover:text-primary-700 transition">
                  {category.name}
                </p>
                <span className="mt-1 text-[11px] font-medium text-gray-400">100% Organic</span>
              </Link>
            ))}
          </div>
        </section>

        {/* BEST SELLERS / POPULAR PRODUCTS */}
        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-extrabold uppercase tracking-widest text-primary-600">Fresh Harvest</span>
              <h2 className="mt-1 font-display text-2xl font-bold text-gray-900">Best Sellers Today</h2>
            </div>
            <Link to="/products" className="text-sm font-bold text-primary-700 hover:text-primary-900 transition">
              View Catalog →
            </Link>
          </div>

          {isLoading ? (
            <div className="card py-12 text-center">
              <Spinner label="Loading certified organic products…" />
            </div>
          ) : featured.length === 0 ? (
            <div className="card text-center py-10 text-gray-500">
              <p>No products available right now. Check back soon!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {featured.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          )}
        </section>

        {/* WHY ORGANICKART */}
        <section className="rounded-3xl bg-gradient-to-br from-primary-900 to-purple-950 p-8 text-white shadow-lg">
          <div className="text-center max-w-2xl mx-auto">
            <span className="rounded-full bg-accent-400/20 px-3 py-1 text-xs font-bold text-accent-300 border border-accent-400/30 uppercase tracking-widest">
              Why Choose Us
            </span>
            <h2 className="mt-3 font-display text-2xl sm:text-3xl font-extrabold">The OrganicKart Advantage</h2>
            <p className="mt-2 text-sm text-purple-200">
              We bring farm-fresh organic produce directly from certified growers to your kitchen with guaranteed freshness.
            </p>
          </div>

          <div className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            <div className="rounded-2xl bg-white/10 p-4 text-center backdrop-blur border border-white/10 hover:bg-white/15 transition">
              <div className="text-3xl">⚡</div>
              <h4 className="mt-2 text-sm font-bold text-white">10-Min Delivery</h4>
              <p className="mt-1 text-[11px] text-purple-200">Lightning fast doorstep fulfillment</p>
            </div>
            <div className="rounded-2xl bg-white/10 p-4 text-center backdrop-blur border border-white/10 hover:bg-white/15 transition">
              <div className="text-3xl">🥬</div>
              <h4 className="mt-2 text-sm font-bold text-white">100% Certified</h4>
              <p className="mt-1 text-[11px] text-purple-200">Strict lab & admin verified organic</p>
            </div>
            <div className="rounded-2xl bg-white/10 p-4 text-center backdrop-blur border border-white/10 hover:bg-white/15 transition">
              <div className="text-3xl">💰</div>
              <h4 className="mt-2 text-sm font-bold text-white">Best Prices</h4>
              <p className="mt-1 text-[11px] text-purple-200">Direct grower rates without middlemen</p>
            </div>
            <div className="rounded-2xl bg-white/10 p-4 text-center backdrop-blur border border-white/10 hover:bg-white/15 transition">
              <div className="text-3xl">🔒</div>
              <h4 className="mt-2 text-sm font-bold text-white">Safe & Secure</h4>
              <p className="mt-1 text-[11px] text-purple-200">JWT protected digital transactions</p>
            </div>
            <div className="rounded-2xl bg-white/10 p-4 text-center backdrop-blur border border-white/10 hover:bg-white/15 transition">
              <div className="text-3xl">↩</div>
              <h4 className="mt-2 text-sm font-bold text-white">Easy Returns</h4>
              <p className="mt-1 text-[11px] text-purple-200">No questions asked return policy</p>
            </div>
            <div className="rounded-2xl bg-white/10 p-4 text-center backdrop-blur border border-white/10 hover:bg-white/15 transition">
              <div className="text-3xl">💬</div>
              <h4 className="mt-2 text-sm font-bold text-white">24/7 Support</h4>
              <p className="mt-1 text-[11px] text-purple-200">Instant dedicated assistance</p>
            </div>
          </div>
        </section>
      </div>

      {/* FULL FOOTER */}
      <footer className="mt-16 border-t border-gray-200 bg-white text-gray-700">
        <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-5">
            {/* Column 1: Brand */}
            <div className="lg:col-span-2 space-y-4">
              <Link to="/" className="flex items-center gap-2">
                <div className="h-9 w-9 rounded-2xl bg-gradient-to-br from-primary-600 to-purple-800 flex items-center justify-center text-white text-lg font-bold shadow-md">
                  🪻
                </div>
                <span className="font-display text-xl font-bold text-primary-900">OrganicKart</span>
              </Link>
              <p className="text-xs text-gray-500 max-w-sm leading-relaxed">
                India's premier quick-commerce organic marketplace. Delivering farm-fresh certified organic vegetables, fruits, dairy, and daily essentials straight to your kitchen in 10 minutes.
              </p>
              <div className="flex items-center gap-3 pt-2 text-lg text-primary-700">
                <span className="cursor-pointer hover:scale-110 transition">🌐</span>
                <span className="cursor-pointer hover:scale-110 transition">🐦</span>
                <span className="cursor-pointer hover:scale-110 transition">📸</span>
                <span className="cursor-pointer hover:scale-110 transition">💼</span>
              </div>
            </div>

            {/* Column 2: Shop */}
            <div>
              <h4 className="font-display text-sm font-bold text-gray-900 uppercase tracking-wider">Shop</h4>
              <ul className="mt-3 space-y-2 text-xs">
                <li><Link to="/products" className="hover:text-primary-700 transition">Fruits & Vegetables</Link></li>
                <li><Link to="/products" className="hover:text-primary-700 transition">Dairy & A2 Milk</Link></li>
                <li><Link to="/products" className="hover:text-primary-700 transition">Organic Staples</Link></li>
                <li><Link to="/products" className="hover:text-primary-700 transition">Cold Pressed Oils</Link></li>
                <li><Link to="/products" className="hover:text-primary-700 transition">Best Sellers</Link></li>
              </ul>
            </div>

            {/* Column 3: Company */}
            <div>
              <h4 className="font-display text-sm font-bold text-gray-900 uppercase tracking-wider">Company</h4>
              <ul className="mt-3 space-y-2 text-xs">
                <li><a href="#" className="hover:text-primary-700 transition">About Us</a></li>
                <li><a href="#" className="hover:text-primary-700 transition">Careers</a></li>
                <li><a href="#" className="hover:text-primary-700 transition">Organic Farmers</a></li>
                <li><a href="#" className="hover:text-primary-700 transition">Press & News</a></li>
                <li><a href="#" className="hover:text-primary-700 transition">Contact Us</a></li>
              </ul>
            </div>

            {/* Column 4: Help */}
            <div>
              <h4 className="font-display text-sm font-bold text-gray-900 uppercase tracking-wider">Help & Support</h4>
              <ul className="mt-3 space-y-2 text-xs">
                <li><a href="#" className="hover:text-primary-700 transition">FAQs</a></li>
                <li><a href="#" className="hover:text-primary-700 transition">Shipping Policy</a></li>
                <li><a href="#" className="hover:text-primary-700 transition">Returns & Refund</a></li>
                <li><a href="#" className="hover:text-primary-700 transition">Terms & Privacy</a></li>
                <li><a href="#" className="hover:text-primary-700 transition">Customer Care</a></li>
              </ul>
            </div>
          </div>

          {/* App download bar */}
          <div className="mt-10 rounded-2xl bg-primary-50 p-6 flex flex-col sm:flex-row items-center justify-between gap-4 border border-primary-100">
            <div>
              <h4 className="font-display text-base font-bold text-primary-900">Download OrganicKart App</h4>
              <p className="text-xs text-gray-600 mt-0.5">Get 20% cashback on your first app order</p>
            </div>
            <div className="flex gap-3">
              <button className="flex items-center gap-2 bg-black text-white px-4 py-2 rounded-xl text-xs font-semibold hover:bg-gray-800 transition">
                <span>📱</span> App Store
              </button>
              <button className="flex items-center gap-2 bg-black text-white px-4 py-2 rounded-xl text-xs font-semibold hover:bg-gray-800 transition">
                <span>🤖</span> Google Play
              </button>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="mt-8 border-t border-gray-100 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-gray-500 gap-4">
            <p>© 2026 OrganicKart Technologies Ltd. All rights reserved.</p>
            <div className="flex items-center gap-4">
              <span>🇮🇳 India</span>
              <span>English</span>
              <span>100% Organic Certified</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

