import { useEffect } from "react";
import { BrowserRouter } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import AppRoutes from "@/routes/AppRoutes";
import { fetchCurrentUser } from "@/store/slices/authSlice";

function App() {
  const dispatch = useDispatch();
  const token = useSelector((state) => state.auth.token);
  const user = useSelector((state) => state.auth.user);

  // On app load (including a hard refresh), if a token is stored but we
  // haven't loaded the user object yet, fetch it. This is what keeps a
  // logged-in session alive across page refreshes without re-entering
  // credentials, without ever trusting client-side state as the source
  // of truth about who the user is.
  useEffect(() => {
    if (token && !user) {
      dispatch(fetchCurrentUser());
    }
  }, [token, user, dispatch]);

  return (
    <BrowserRouter future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}>
      <AppRoutes />
    </BrowserRouter>
  );
}

export default App;
