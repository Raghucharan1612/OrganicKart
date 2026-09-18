/**
 * Banner for whole-form errors returned by the API (e.g. "Incorrect
 * email or password"), as opposed to per-field validation errors
 * which render inline via <Input error="...">.
 */
export default function FormError({ message }) {
  if (!message) return null;
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
      {message}
    </div>
  );
}
