import { Route, Routes } from "react-router-dom";
import MainLayout from "@/layouts/MainLayout";
import ProtectedRoute from "@/components/ProtectedRoute";
import RoleRoute from "@/components/RoleRoute";

import HomePage from "@/pages/HomePage";
import UnauthorizedPage from "@/pages/UnauthorizedPage";
import AdminPage from "@/pages/AdminPage";
import AdminCategoriesPage from "@/pages/AdminCategoriesPage";
import AddressBookPage from "@/pages/AddressBookPage";
import LoginPage from "@/features/auth/pages/LoginPage";
import RegisterPage from "@/features/auth/pages/RegisterPage";
import ForgotPasswordPage from "@/features/auth/pages/ForgotPasswordPage";
import ResetPasswordPage from "@/features/auth/pages/ResetPasswordPage";
import ProfilePage from "@/features/auth/pages/ProfilePage";
import ProductListingPage from "@/features/catalog/pages/ProductListingPage";
import ProductDetailsPage from "@/features/catalog/pages/ProductDetailsPage";
import MyProductsPage from "@/features/catalog/pages/MyProductsPage";
import SellerDashboardPage from "@/pages/SellerDashboardPage";
import CartPage from "@/pages/CartPage";
import CheckoutPage from "@/pages/CheckoutPage";
import OrdersPage from "@/pages/OrdersPage";
import OrderDetailsPage from "@/pages/OrderDetailsPage";
import DeliveryPage from "@/pages/DeliveryPage";
import NotificationsPage from "@/pages/NotificationsPage";

/**
 * Central route table. All pages use MainLayout so the global Navbar
 * is always present. The seller secondary nav (SellerSubNav) renders
 * inside SellerDashboardPage itself — no separate layout needed.
 */
export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        {/* Public routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/products" element={<ProductListingPage />} />
        <Route path="/products/:id" element={<ProductDetailsPage />} />
        <Route path="/categories" element={<ProductListingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/unauthorized" element={<UnauthorizedPage />} />

        {/* Authenticated routes (any role) */}
        <Route element={<ProtectedRoute />}>
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/addresses" element={<AddressBookPage />} />
          <Route path="/delivery" element={<DeliveryPage />} />
          <Route path="/delivery/:id" element={<DeliveryPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />

          {/* Customer-only routes */}
          <Route element={<RoleRoute allowedRoles={["CUSTOMER"]} />}>
            <Route path="/cart" element={<CartPage />} />
            <Route path="/checkout" element={<CheckoutPage />} />
            <Route path="/orders" element={<OrdersPage />} />
            <Route path="/orders/:id" element={<OrderDetailsPage />} />
          </Route>

          {/* Seller (VENDOR/FARMER) routes — share MainLayout so Navbar shows */}
          <Route element={<RoleRoute allowedRoles={["VENDOR", "FARMER", "ADMIN", "SUPER_ADMIN"]} />}>
            <Route path="/seller" element={<SellerDashboardPage />} />
            <Route path="/seller/products" element={<MyProductsPage />} />
            <Route path="/seller/products/new" element={<MyProductsPage />} />
            <Route path="/seller/products/:id/edit" element={<MyProductsPage />} />
            <Route path="/my-products" element={<MyProductsPage />} />
          </Route>

          {/* Admin routes */}
          <Route element={<RoleRoute allowedRoles={["ADMIN", "SUPER_ADMIN"]} />}>
            <Route path="/admin" element={<AdminPage />} />
            <Route path="/admin/products" element={<AdminPage />} />
            <Route path="/admin/certifications" element={<AdminPage />} />
            <Route path="/admin/categories" element={<AdminCategoriesPage />} />
          </Route>
        </Route>
      </Route>
    </Routes>
  );
}
