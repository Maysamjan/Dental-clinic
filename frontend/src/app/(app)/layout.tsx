"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/stores/auth";
import Sidebar from "@/components/Sidebar";
import Topbar from "@/components/Topbar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const access = useAuth((s) => s.access);
  const hasHydrated = useAuth((s) => s.hasHydrated);

  useEffect(() => {
    // Only decide after the persisted store has rehydrated, so a hard refresh
    // of a protected page doesn't bounce a logged-in user to /login.
    if (hasHydrated && !access) router.replace("/login");
  }, [hasHydrated, access, router]);

  if (!hasHydrated) return null;
  if (!access) return null;

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar />
        <main className="flex-1 overflow-y-auto p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}
