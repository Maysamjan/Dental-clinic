import type { DictKey } from "@/i18n/dictionaries";

export interface NavItem {
  href: string;
  labelKey: DictKey;
  icon: string;
  module: string; // permission module required to view
}

export const navItems: NavItem[] = [
  { href: "/dashboard", labelKey: "dashboard", icon: "📊", module: "dashboard" },
  { href: "/reception", labelKey: "reception", icon: "🪑", module: "visits" },
  { href: "/patients", labelKey: "patients", icon: "👤", module: "patients" },
  { href: "/appointments", labelKey: "appointments", icon: "📅", module: "appointments" },
  { href: "/visits", labelKey: "visits", icon: "🩺", module: "visits" },
  { href: "/dental-chart", labelKey: "dental_chart", icon: "🦷", module: "dental_charts" },
  { href: "/treatments", labelKey: "treatments", icon: "🧩", module: "treatments" },
  { href: "/prescriptions", labelKey: "prescriptions", icon: "💊", module: "prescriptions" },
  { href: "/billing", labelKey: "billing", icon: "🧾", module: "billing" },
  { href: "/payments", labelKey: "payments", icon: "💵", module: "payments" },
  { href: "/installments", labelKey: "installments", icon: "📆", module: "installments" },
  { href: "/expenses", labelKey: "expenses", icon: "📉", module: "expenses" },
  { href: "/inventory", labelKey: "inventory", icon: "📦", module: "inventory" },
  { href: "/documents", labelKey: "documents", icon: "🗂️", module: "documents" },
  { href: "/reports", labelKey: "reports", icon: "📈", module: "reports" },
  { href: "/followups", labelKey: "followups", icon: "🔔", module: "followups" },
  { href: "/administration", labelKey: "administration", icon: "⚙️", module: "users" },
];
