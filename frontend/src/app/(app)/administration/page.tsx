"use client";
import { useState } from "react";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import { useT } from "@/i18n/useT";
import { ROLE_FA, ACTION_FA } from "@/lib/labels";

const TABS = [
  ["users", "کاربران", "users"],
  ["roles", "نقش‌ها", "roles"],
  ["sessions", "نشست‌ها", "sessions"],
  ["activity-logs", "گزارش فعالیت‌ها", "activity-logs"],
] as const;

export default function AdministrationPage() {
  const t = useT();
  const [tab, setTab] = useState<string>("users");

  return (
    <div>
      <PageHeader title={t("administration")} subtitle="کاربران · نقش‌ها · امنیت · حسابرسی" />

      <div className="mb-4 flex gap-2">
        {TABS.map(([key, label]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={tab === key ? "btn-primary" : "btn-ghost"}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "users" && (
        <ResourceTable
          resource="users"
          columns={[
            { key: "username", label: "نام کاربری" },
            { key: "full_name", label: "نام" },
            { key: "role_name", label: "نقش", render: (r) => ROLE_FA[r.role_code] ?? r.role_name },
            { key: "is_active", label: "فعال", render: (r) => (r.is_active ? "بله" : "خیر") },
          ]}
        />
      )}
      {tab === "roles" && (
        <ResourceTable
          resource="roles"
          searchable={false}
          columns={[
            { key: "name", label: "نقش", render: (r) => ROLE_FA[r.code] ?? r.name },
            { key: "code", label: "کد" },
            {
              key: "permissions",
              label: "دسترسی‌ها",
              render: (r) => <span className="text-xs text-slate-400">{r.permissions.length} مورد</span>,
            },
          ]}
        />
      )}
      {tab === "sessions" && (
        <ResourceTable
          resource="sessions"
          searchable={false}
          columns={[
            { key: "username", label: "کاربر" },
            { key: "ip_address", label: "آی‌پی" },
            { key: "login_at", label: "ورود", render: (r) => new Date(r.login_at).toLocaleString('en-US') },
            { key: "is_active", label: "فعال", render: (r) => (r.is_active ? "بله" : "خیر") },
          ]}
        />
      )}
      {tab === "activity-logs" && (
        <ResourceTable
          resource="activity-logs"
          columns={[
            { key: "username", label: "کاربر" },
            { key: "action", label: "عملیات", render: (r) => ACTION_FA[r.action] ?? r.action },
            { key: "summary", label: "شرح" },
            { key: "created_at", label: "زمان", render: (r) => new Date(r.created_at).toLocaleString('en-US') },
          ]}
        />
      )}
    </div>
  );
}
