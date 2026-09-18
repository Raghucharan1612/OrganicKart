import { configureStore } from "@reduxjs/toolkit";
import authReducer from "./slices/authSlice";

/**
 * Root Redux store. Sprint 2 registers only the `auth` slice.
 * Cart and wishlist slices (Sprint 6) will be added the same way —
 * one slice per genuinely global concern, not for every UI state.
 */
export const store = configureStore({
  reducer: {
    auth: authReducer,
  },
});
