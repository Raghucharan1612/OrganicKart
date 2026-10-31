import { useLocation } from "react-router-dom";
import SellerDashboardPage from "@/pages/SellerDashboardPage";

/**
 * MyProductsPage — routes directly to the upgraded SellerDashboardPage
 * with the appropriate tab (products, add, or edit).
 */
export default function MyProductsPage() {
  const location = useLocation();

  const tab = location.pathname.includes("/new")
    ? "add"
    : location.pathname.includes("/edit")
    ? "edit"
    : "products";

  return <SellerDashboardPage defaultTab={tab} />;
}
