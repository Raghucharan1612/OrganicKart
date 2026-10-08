import { Outlet } from "react-router-dom";
import VendorAIAssistant from "@/components/ai/VendorAIAssistant";

/**
 * SellerLayout — Full-screen layout for VENDOR / FARMER pages.
 * Intentionally has NO Navbar so that SellerDashboardPage can own
 * the entire viewport with its own sidebar + workspace structure.
 * VendorAIAssistant is kept here so it floats above all seller pages.
 */
export default function SellerLayout() {
  return (
    <div className="h-screen w-screen overflow-hidden bg-slate-50 text-slate-800">
      <Outlet />
      <VendorAIAssistant />
    </div>
  );
}
