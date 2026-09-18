/**
 * Reusable button. `variant` picks the visual style, `isLoading` shows
 * a spinner and disables the button so users can't double-submit forms.
 */
export default function Button({
  children,
  variant = "primary",
  isLoading = false,
  type = "button",
  className = "",
  ...rest
}) {
  const base = variant === "primary" ? "btn-primary" : "btn-secondary";
  return (
    <button type={type} className={`${base} ${className}`} disabled={isLoading || rest.disabled} {...rest}>
      {isLoading ? (
        <span className="flex items-center gap-2">
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
          Please wait…
        </span>
      ) : (
        children
      )}
    </button>
  );
}
