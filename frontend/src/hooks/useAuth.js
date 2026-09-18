import { useDispatch, useSelector } from "react-redux";
import { logout as logoutAction } from "@/store/slices/authSlice";

/**
 * Thin convenience wrapper around the auth slice so components don't
 * need to know Redux selector/dispatch boilerplate to answer
 * "who is logged in and what can they do".
 */
export function useAuth() {
  const dispatch = useDispatch();
  const { user, token, status, error } = useSelector((state) => state.auth);

  return {
    user,
    token,
    status,
    error,
    isAuthenticated: Boolean(token && user),
    isLoading: status === "loading",
    logout: () => dispatch(logoutAction()),
  };
}
