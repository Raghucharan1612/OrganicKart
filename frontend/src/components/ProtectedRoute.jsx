import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import Spinner from "@/components/Spinner";

/**
 * Route guard for "must be logged in". Wraps a set of routes via
 * <Route element={<ProtectedRoute />}>...child routes...</Route>.
 * Unauthenticated users are bounced to /login and sent back to the
 * page they wanted after they sign in (via `state.from`).
 */
export default function ProtectedRoute() {
  const { isAuthenticated, isLoading, token, status } = useAuth();
  const location = useLocation();

  // A token exists but we haven't resolved the user yet (e.g. page
  // refresh) — show a spinner instead of bouncing to /login too early.
  if (token && (isLoading || (status !== "failed" && !isAuthenticated))) {
    return <Spinner label="Checking your session…" />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
}
