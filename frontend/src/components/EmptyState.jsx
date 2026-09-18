/** Reusable "nothing here yet" placeholder for lists (addresses, orders, etc.). */
export default function EmptyState({ title, description, action }) {
  return (
    <div className="card flex flex-col items-center gap-2 py-12 text-center">
      <h3 className="font-display text-lg font-semibold text-primary-900">{title}</h3>
      {description && <p className="max-w-sm text-sm text-gray-500">{description}</p>}
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
}
