"use client";
import { useRouter } from "next/navigation";
import { useAuth } from "@/stores/auth";
import { useUI } from "@/stores/ui";
import { useT } from "@/i18n/useT";
import { ROLE_FA } from "@/lib/labels";

export default function Topbar() {
  const router = useRouter();
  const t = useT();
  const user = useAuth((s) => s.user);
  const logout = useAuth((s) => s.logout);
  const { theme, toggleTheme, toggleSidebar } = useUI();

  function doLogout() {
    logout();
    router.replace("/login");
  }

  return (
    <header className="flex h-14 items-center justify-between border-b border-slate-200 bg-white px-4 dark:border-slate-700 dark:bg-slate-800">
      <button onClick={toggleSidebar} className="btn-ghost px-2 py-1" aria-label="منو">
        ☰
      </button>

      <div className="flex items-center gap-3">
        <button onClick={toggleTheme} className="btn-ghost px-2 py-1" aria-label="پوسته">
          {theme === "light" ? "🌙" : "☀️"}
        </button>

        <div className="hidden text-right sm:block">
          <div className="text-sm font-medium">{user?.full_name}</div>
          <div className="text-xs text-slate-400">{user?.role_code ? (ROLE_FA[user.role_code] ?? user?.role_name) : user?.role_name}</div>
        </div>

        <button onClick={doLogout} className="btn-ghost px-3 py-1">
          {t("logout")}
        </button>
      </div>
    </header>
  );
}
