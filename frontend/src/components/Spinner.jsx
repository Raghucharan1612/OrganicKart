/** Full-area loading indicator used for page-level async states. */
export default function Spinner({ label = "Loading…" }) {
  return (
    <div className="flex min-h-[200px] flex-col items-center justify-center gap-3 text-primary-700">
      <span className="h-8 w-8 animate-spin rounded-full border-4 border-primary-100 border-t-primary-600" />
      <span className="text-sm text-gray-500">{label}</span>
    </div>
  );
}
