export default function EmptyState({ title = "No items found", description, action }) {
  return (
    <div className="card my-6 flex flex-col items-center justify-center py-12 text-center animate-fade-in">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-50 text-3xl shadow-xs mb-3">
        📦
      </div>
      <h3 className="font-display text-base font-bold text-gray-900">{title}</h3>
      {description && <p className="mt-1 text-xs text-gray-500 max-w-sm">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

