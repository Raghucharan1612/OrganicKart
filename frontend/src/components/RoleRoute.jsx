import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import Spinner from "@/components/Spinner";

/**
 * Route guard for "must be logged in AND have one of these roles".
 * Usage: <Route element={<RoleRoute allowedRoles={["ADMIN", "SUPER_ADMIN"]} />}>
 *
 * This is the frontend mirror of the backend's require_roles dependency —
 * it keeps unauthorized users from ever seeing the page shell, though the
 * backend remains the real authority (frontend checks are UX, not security).
 */
export default function RoleRoute({ allowedRoles = [] }) {
  const { user, isAuthenticated, isLoading, token, status } = useAuth();

  if (token && (isLoading || (status !== "failed" && !isAuthenticated))) {
    return <Spinner label="Checking session permissions…" />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!allowedRoles.includes(user?.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
}
