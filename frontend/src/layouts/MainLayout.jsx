import { Outlet } from "react-router-dom";
import Navbar from "@/components/Navbar";

export default function MainLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-cream text-gray-900">
      <Navbar />
      <main className="flex-1 w-full">
        <Outlet />
      </main>
    </div>
  );
}

