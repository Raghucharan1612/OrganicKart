/**
 * Reusable pagination control driven entirely by props — the parent
 * page owns the current page number (usually synced to the URL via
 * useSearchParams) and passes it back down here.
 */
export default function Pagination({ page, pages, onPageChange }) {
  if (pages <= 1) return null;

  const goTo = (p) => {
    if (p >= 1 && p <= pages) onPageChange(p);
  };

  // Show a compact window of page numbers around the current page.
  const windowStart = Math.max(1, page - 2);
  const windowEnd = Math.min(pages, windowStart + 4);
  const pageNumbers = [];
  for (let p = windowStart; p <= windowEnd; p++) pageNumbers.push(p);

  return (
    <nav className="flex items-center justify-center gap-1.5" aria-label="Pagination">
      <button
        type="button"
        onClick={() => goTo(page - 1)}
        disabled={page === 1}
        className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-600 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
      >
        Prev
      </button>

      {windowStart > 1 && <span className="px-1 text-gray-400">…</span>}

      {pageNumbers.map((p) => (
        <button
          key={p}
          type="button"
          onClick={() => goTo(p)}
          className={`h-9 w-9 rounded-lg text-sm font-medium transition ${
            p === page
              ? "bg-primary-600 text-white"
              : "border border-gray-200 text-gray-600 hover:bg-gray-50"
          }`}
        >
          {p}
        </button>
      ))}

      {windowEnd < pages && <span className="px-1 text-gray-400">…</span>}

      <button
        type="button"
        onClick={() => goTo(page + 1)}
        disabled={page === pages}
        className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-600 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
      >
        Next
      </button>
    </nav>
  );
}
