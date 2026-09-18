import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import productService from "@/services/productService";
import categoryService from "@/services/categoryService";
import ProductCard from "@/features/catalog/components/ProductCard";
import Pagination from "@/components/Pagination";
import Spinner from "@/components/Spinner";
import EmptyState from "@/components/EmptyState";
import { getApiErrorMessage } from "@/utils/errorUtils";

const SORT_OPTIONS = [
  { value: "newest", label: "Newest Arrivals" },
  { value: "price_asc", label: "Price: Low to High" },
  { value: "price_desc", label: "Price: High to Low" },
  { value: "name_asc", label: "Name: A to Z" },
];

const PAGE_SIZE = 12;

const normalizeResult = (data) => {
  if (Array.isArray(data)) {
    return { items: data, total: data.length, page: 1, page_size: PAGE_SIZE, pages: Math.max(1, Math.ceil(data.length / PAGE_SIZE)) };
  }

  const items = Array.isArray(data?.items) ? data.items : [];
  const total = Number(data?.total || items.length || 0);
  const page = Number(data?.page || 1);
  const pageSize = Number(data?.page_size || PAGE_SIZE);
  const pages = Math.max(1, Number(data?.pages || Math.ceil(total / pageSize) || 1));

  return { items, total, page, page_size: pageSize, pages };
};

export default function ProductListingPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const search = searchParams.get("search") || "";
  const categoryId = searchParams.get("category_id") || "";
  const sortBy = searchParams.get("sort_by") || "newest";
  const minPrice = searchParams.get("min_price") || "";
  const maxPrice = searchParams.get("max_price") || "";
  const certification = searchParams.get("certification") || "";
  const page = Number(searchParams.get("page") || 1);

  const [searchInput, setSearchInput] = useState(search);
  const [categories, setCategories] = useState([]);
  const [result, setResult] = useState({ items: [], total: 0, pages: 1, page: 1, page_size: PAGE_SIZE });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;
    categoryService
      .list()
      .then((data) => {
        if (!cancelled) setCategories(Array.isArray(data) ? data : []);
      })
      .catch(() => {
        if (!cancelled) setCategories([]);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError("");

    const params = { page, page_size: PAGE_SIZE };
    const apiSort = { newest: "created_at", price_asc: "price", price_desc: "price", name_asc: "name" }[sortBy] || "created_at";
    const apiOrder = sortBy === "price_asc" || sortBy === "name_asc" ? "asc" : "desc";

    params.sort_by = apiSort;
    params.sort_order = apiOrder;

    if (search) params.search = search;
    if (categoryId) params.category_id = categoryId;
    if (minPrice) params.min_price = minPrice;
    if (maxPrice) params.max_price = maxPrice;
    if (certification) params.certification = certification;

    productService
      .list(params)
      .then((data) => {
        if (!cancelled) setResult(normalizeResult(data));
      })
      .catch((err) => {
        if (!cancelled) {
          const message = getApiErrorMessage(err, "Could not load products. Please try again.");
          setError(message);
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [search, categoryId, sortBy, minPrice, maxPrice, certification, page]);

  const categoryMap = useMemo(() => Object.fromEntries(categories.map((cat) => [String(cat.id), cat.name])), [categories]);

  const updateParams = (updates) => {
    const next = new URLSearchParams(searchParams);
    Object.entries(updates).forEach(([key, value]) => {
      if (value === "" || value === undefined || value === null) {
        next.delete(key);
      } else {
        next.set(key, value);
      }
    });
    if (!("page" in updates)) next.set("page", "1");
    setSearchParams(next);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    updateParams({ search: searchInput });
  };

  const clearAllFilters = () => {
    setSearchInput("");
    setSearchParams(new URLSearchParams());
  };

  const activeFilterCount = [categoryId, minPrice, maxPrice, certification, search].filter(Boolean).length;

  const FilterSidebarContent = () => (
    <div className="space-y-6">
      {/* Category List */}
      <div>
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">Categories</h3>
        <div className="space-y-1">
          <button
            type="button"
            onClick={() => updateParams({ category_id: "" })}
            className={`w-full text-left px-3 py-2 rounded-xl text-sm font-semibold transition ${
              !categoryId
                ? "bg-primary-600 text-white shadow-sm"
                : "text-gray-700 hover:bg-primary-50 hover:text-primary-700"
            }`}
          >
            🌿 All Categories
          </button>
          {categories.map((cat) => {
            const isSelected = String(cat.id) === String(categoryId);
            return (
              <button
                key={cat.id}
                type="button"
                onClick={() => updateParams({ category_id: cat.id })}
                className={`w-full text-left px-3 py-2 rounded-xl text-sm font-semibold transition ${
                  isSelected
                    ? "bg-primary-600 text-white shadow-sm"
                    : "text-gray-700 hover:bg-primary-50 hover:text-primary-700"
                }`}
              >
                {cat.name}
              </button>
            );
          })}
        </div>
      </div>

      {/* Price Range */}
      <div className="border-t border-gray-100 pt-5">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">Price Range (₹)</h3>
        <div className="grid grid-cols-2 gap-2">
          <input
            type="number"
            min="0"
            value={minPrice}
            onChange={(e) => updateParams({ min_price: e.target.value })}
            placeholder="Min ₹"
            className="input-field text-xs"
          />
          <input
            type="number"
            min="0"
            value={maxPrice}
            onChange={(e) => updateParams({ max_price: e.target.value })}
            placeholder="Max ₹"
            className="input-field text-xs"
          />
        </div>
      </div>

      {/* Certification Status */}
      <div className="border-t border-gray-100 pt-5">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">Certification</h3>
        <select
          value={certification}
          onChange={(e) => updateParams({ certification: e.target.value })}
          className="input-field text-xs"
        >
          <option value="">All Certifications</option>
          <option value="APPROVED">Approved Organic</option>
          <option value="PENDING">Pending Certification</option>
        </select>
      </div>

      {/* Clear Filters Action */}
      {activeFilterCount > 0 && (
        <button
          type="button"
          onClick={clearAllFilters}
          className="w-full text-center py-2 px-3 rounded-xl border border-red-200 text-xs font-bold text-red-600 hover:bg-red-50 transition"
        >
          Clear All Filters ({activeFilterCount})
        </button>
      )}
    </div>
  );

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-6">
      {/* Header & Search */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-extrabold text-primary-900">Shop Organic</h1>
          <p className="mt-1 text-sm text-gray-500">
            {result.total > 0 ? `${result.total} certified organic products available` : "Browse our organic catalog"}
          </p>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} className="flex gap-2 max-w-md w-full">
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search produce, milk, honey..."
            className="input-field"
          />
          <button type="submit" className="btn-primary shrink-0 font-bold">
            Search
          </button>
        </form>
      </div>

      {/* Mobile Filter Toggle & Sort Bar */}
      <div className="flex lg:hidden items-center justify-between gap-3 bg-white p-3 rounded-2xl border border-gray-100 shadow-sm">
        <button
          type="button"
          onClick={() => setIsMobileFilterOpen(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary-50 text-primary-800 text-xs font-bold border border-primary-200"
        >
          <span>⚙️ Filters</span>
          {activeFilterCount > 0 && (
            <span className="bg-primary-600 text-white px-1.5 py-0.5 rounded-full text-[10px]">
              {activeFilterCount}
            </span>
          )}
        </button>

        <select
          value={sortBy}
          onChange={(e) => updateParams({ sort_by: e.target.value })}
          className="input-field text-xs !w-auto"
        >
          {SORT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Main Grid & Left Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-[260px_minmax(0,1fr)] gap-8">
        {/* DESKTOP SIDEBAR */}
        <aside className="hidden lg:block space-y-6 bg-white p-5 rounded-2xl border border-gray-100 shadow-sm self-start sticky top-24">
          <div className="flex items-center justify-between border-b border-gray-100 pb-3">
            <h2 className="font-display text-base font-bold text-gray-900 flex items-center gap-2">
              <span>⚙️</span> Filters
            </h2>
            <select
              value={sortBy}
              onChange={(e) => updateParams({ sort_by: e.target.value })}
              className="text-xs border-0 bg-transparent font-semibold text-primary-700 focus:ring-0 cursor-pointer"
            >
              {SORT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          <FilterSidebarContent />
        </aside>

        {/* MOBILE FILTER MODAL/SHEET */}
        {isMobileFilterOpen && (
          <div className="fixed inset-0 z-50 flex bg-black/50 backdrop-blur-xs lg:hidden">
            <div className="ml-auto w-4/5 max-w-xs bg-white h-full p-6 space-y-6 overflow-y-auto shadow-2xl">
              <div className="flex items-center justify-between border-b border-gray-100 pb-4">
                <h2 className="font-display text-lg font-bold text-gray-900">Filters</h2>
                <button
                  type="button"
                  onClick={() => setIsMobileFilterOpen(false)}
                  className="text-gray-500 font-bold text-xl p-1"
                >
                  ✕
                </button>
              </div>
              <FilterSidebarContent />
              <button
                type="button"
                onClick={() => setIsMobileFilterOpen(false)}
                className="btn-primary w-full py-2.5 text-sm font-bold"
              >
                Apply Filters
              </button>
            </div>
          </div>
        )}

        {/* PRODUCT LISTING SECTION */}
        <main className="space-y-6">
          {isLoading ? (
            <Spinner label="Loading organic products…" />
          ) : error ? (
            <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-center text-sm font-medium text-red-700">
              {error}
            </div>
          ) : result.items.length === 0 ? (
            <EmptyState title="No products found" description="Try selecting a different category or clearing your search filters." />
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
                {result.items.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={{
                      ...product,
                      category: { name: categoryMap[String(product.category_id)] || "Organic" },
                    }}
                  />
                ))}
              </div>

              <div className="pt-4 border-t border-gray-100">
                <Pagination page={page} pages={result.pages} onPageChange={(p) => updateParams({ page: p })} />
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
