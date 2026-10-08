import { Outlet } from "react-router-dom";
import Navbar from "@/components/Navbar";
import CustomerAIAssistant from "@/components/ai/CustomerAIAssistant";
import VendorAIAssistant from "@/components/ai/VendorAIAssistant";
import AdminAIAssistant from "@/components/ai/AdminAIAssistant";

export default function MainLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-cream text-gray-900">
      <Navbar />
      <main className="flex-1 w-full">
        <Outlet />
      </main>
      <CustomerAIAssistant />
      <VendorAIAssistant />
      <AdminAIAssistant />
    </div>
  );
}
