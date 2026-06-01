import type { DictKey } from "@/i18n/dictionaries";

export interface NavItem {
  href: string;
  labelKey: DictKey;
  icon: string;
  module: string; // permission module required to view
  group: string; // Persian section heading
}

// Grouped navigation keeps the sidebar scannable instead of a long flat list.
export const navItems: NavItem[] = [
  // اصلی
  { href: "/dashboard", labelKey: "dashboard", icon: "📊", module: "dashboard", group: "اصلی" },
  { href: "/reception", labelKey: "reception", icon: "🪑", module: "visits", group: "اصلی" },
  { href: "/patients", labelKey: "patients", icon: "👤", module: "patients", group: "اصلی" },
  { href: "/appointments", labelKey: "appointments", icon: "📅", module: "appointments", group: "اصلی" },

  // بالینی
  { href: "/visits", labelKey: "visits", icon: "🩺", module: "visits", group: "بالینی" },
  { href: "/dental-chart", labelKey: "dental_chart", icon: "🦷", module: "dental_charts", group: "بالینی" },
  { href: "/treatments", labelKey: "treatments", icon: "🧩", module: "treatments", group: "بالینی" },
  { href: "/prescriptions", labelKey: "prescriptions", icon: "💊", module: "prescriptions", group: "بالینی" },

  // مالی
  { href: "/billing", labelKey: "billing", icon: "🧾", module: "billing", group: "مالی" },
  { href: "/payments", labelKey: "payments", icon: "💵", module: "payments", group: "مالی" },
  { href: "/installments", labelKey: "installments", icon: "📆", module: "installments", group: "مالی" },
  { href: "/expenses", labelKey: "expenses", icon: "📉", module: "expenses", group: "مالی" },

  // سیستم
  { href: "/inventory", labelKey: "inventory", icon: "📦", module: "inventory", group: "سیستم" },
  { href: "/documents", labelKey: "documents", icon: "🗂️", module: "documents", group: "سیستم" },
  { href: "/reports", labelKey: "reports", icon: "📈", module: "reports", group: "سیستم" },
  { href: "/followups", labelKey: "followups", icon: "🔔", module: "followups", group: "سیستم" },
  { href: "/administration", labelKey: "administration", icon: "⚙️", module: "users", group: "سیستم" },
];

export const navGroups = ["اصلی", "بالینی", "مالی", "سیستم"];
