import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import authService from "@/services/authService";
import userService from "@/services/userService";

const TOKEN_KEY = "organickart_token";

/**
 * Auth is the textbook case for Redux: it's read by the navbar, route
 * guards, dashboards, checkout, and more — genuinely global state, not
 * something that belongs in one component's local state.
 */
const storedToken = localStorage.getItem(TOKEN_KEY);

const initialState = {
  user: null,
  token: storedToken || null,
  status: storedToken ? "loading" : "idle", // idle | loading | succeeded | failed
  error: null,
};

// --- Async thunks: each wraps exactly one API call + the side effects
// that must happen around it (storing/clearing the token). ---

export const registerUser = createAsyncThunk(
  "auth/registerUser",
  async (payload, { rejectWithValue }) => {
    try {
      return await authService.register(payload);
    } catch (err) {
      return rejectWithValue(extractErrorMessage(err));
    }
  }
);

export const loginUser = createAsyncThunk(
  "auth/loginUser",
  async (payload, { rejectWithValue }) => {
    try {
      const { access_token } = await authService.login(payload);
      localStorage.setItem(TOKEN_KEY, access_token);
      const user = await authService.getCurrentUser();
      return { token: access_token, user };
    } catch (err) {
      return rejectWithValue(extractErrorMessage(err));
    }
  }
);

export const fetchCurrentUser = createAsyncThunk(
  "auth/fetchCurrentUser",
  async (_, { rejectWithValue }) => {
    try {
      return await authService.getCurrentUser();
    } catch (err) {
      localStorage.removeItem(TOKEN_KEY);
      return rejectWithValue(extractErrorMessage(err));
    }
  }
);

export const updateProfile = createAsyncThunk(
  "auth/updateProfile",
  async (payload, { rejectWithValue }) => {
    try {
      return await userService.updateProfile(payload);
    } catch (err) {
      return rejectWithValue(extractErrorMessage(err));
    }
  }
);

function extractErrorMessage(err) {
  const detail = err?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (typeof detail?.detail === "string") return detail.detail;
  if (typeof detail?.message === "string") return detail.message;
  return "Something went wrong. Please try again.";
}

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logout(state) {
      localStorage.removeItem(TOKEN_KEY);
      state.user = null;
      state.token = null;
      state.status = "idle";
      state.error = null;
    },
    clearAuthError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Register
      .addCase(registerUser.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state) => {
        state.status = "succeeded";
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
      })
      // Login
      .addCase(loginUser.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.token = action.payload.token;
        state.user = action.payload.user;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
      })
      // Fetch current user (app bootstrap / refresh)
      .addCase(fetchCurrentUser.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.user = action.payload;
      })
      .addCase(fetchCurrentUser.rejected, (state) => {
        state.status = "failed";
        state.user = null;
        state.token = null;
      })
      // Update profile
      .addCase(updateProfile.fulfilled, (state, action) => {
        state.user = action.payload;
      });
  },
});

export const { logout, clearAuthError } = authSlice.actions;
export default authSlice.reducer;
