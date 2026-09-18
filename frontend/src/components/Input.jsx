/**
 * Reusable labeled text input with inline validation error display.
 * Every auth/profile/address form uses this instead of hand-rolled
 * <input> + <label> markup, so styling and error handling stay consistent.
 */
export default function Input({ label, id, error, className = "", ...rest }) {
  return (
    <div className={className}>
      {label && (
        <label htmlFor={id} className="mb-1.5 block text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      <input id={id} className={`input-field ${error ? "border-red-400 focus:ring-red-100 focus:border-red-400" : ""}`} {...rest} />
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}
