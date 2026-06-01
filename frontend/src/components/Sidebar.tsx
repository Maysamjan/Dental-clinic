"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { navItems, navGroups } from "@/lib/nav";
import { canViewModule } from "@/lib/permissions";
import { useAuth } from "@/stores/auth";
import { useUI } from "@/stores/ui";
import { useT } from "@/i18n/useT";

export default function Sidebar() {
  const pathname = usePathname();
  const t = useT();
  const permissions = useAuth((s) => s.user?.permissions);
  const sidebarOpen = useUI((s) => s.sidebarOpen);

  const items = navItems.filter((i) => canViewModule(permissions, i.module));

  return (
    <aside
      className={clsx(
        "shrink-0 overflow-y-auto border-e border-slate-200 bg-white transition-all dark:border-slate-700 dark:bg-slate-800",
        sidebarOpen ? "w-64" : "w-0 md:w-16"
      )}
    >
      <div className="flex h-14 items-center gap-2 px-4 text-brand-700 dark:text-brand-100">
        <span className="text-2xl">🦷</span>
        {sidebarOpen && <span className="font-bold">{t("app_name")}</span>}
      </div>

      <nav className="px-2 pb-6">
        {navGroups.map((group) => {
          const groupItems = items.filter((i) => i.group === group);
          if (groupItems.length === 0) return null;
          return (
            <div key={group} className="mb-2">
              {sidebarOpen && (
                <div className="px-3 pb-1 pt-3 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                  {group}
                </div>
              )}
              {groupItems.map((item) => {
                const active = pathname.startsWith(item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={clsx(
                      "my-0.5 flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm",
                      active
                        ? "bg-brand-50 font-semibold text-brand-700 dark:bg-slate-700 dark:text-brand-100"
                        : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
                    )}
                  >
                    <span className="text-lg">{item.icon}</span>
                    {sidebarOpen && <span>{t(item.labelKey)}</span>}
                  </Link>
                );
              })}
            </div>
          );
        })}
      </nav>
    </aside>
  );
}
