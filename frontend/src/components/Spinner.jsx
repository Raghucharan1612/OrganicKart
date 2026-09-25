export default function Spinner({ label = "Loading…" }) {
  return (
    <div className="flex flex-col items-center justify-center p-6 text-center animate-fade-in">
      <div className="h-8 w-8 animate-spin rounded-full border-3 border-primary-200 border-t-primary-600" />
      {label && <p className="mt-3 text-xs font-semibold text-gray-500 animate-pulse">{label}</p>}
    </div>
  );
}
