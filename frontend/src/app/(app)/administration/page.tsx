"use client";
import { useState } from "react";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import { useT } from "@/i18n/useT";

const TABS = [
  ["users", "Users", "users"],
  ["roles", "Roles", "roles"],
  ["sessions", "Sessions", "sessions"],
  ["activity-logs", "Activity Logs", "activity-logs"],
] as const;

export default function AdministrationPage() {
  const t = useT();
  const [tab, setTab] = useState<string>("users");

  return (
    <div>
      <PageHeader title={t("administration")} subtitle="Users · Roles · Security · Audit" />

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
            { key: "username", label: "Username" },
            { key: "full_name", label: "Name" },
            { key: "role_name", label: "Role" },
            { key: "is_active", label: "Active", render: (r) => (r.is_active ? "Yes" : "No") },
          ]}
        />
      )}
      {tab === "roles" && (
        <ResourceTable
          resource="roles"
          searchable={false}
          columns={[
            { key: "name", label: "Role" },
            { key: "code", label: "Code" },
            {
              key: "permissions",
              label: "Permissions",
              render: (r) => <span className="text-xs text-slate-400">{r.permissions.length} codes</span>,
            },
          ]}
        />
      )}
      {tab === "sessions" && (
        <ResourceTable
          resource="sessions"
          searchable={false}
          columns={[
            { key: "username", label: "User" },
            { key: "ip_address", label: "IP" },
            { key: "login_at", label: "Login", render: (r) => new Date(r.login_at).toLocaleString() },
            { key: "is_active", label: "Active", render: (r) => (r.is_active ? "Yes" : "No") },
          ]}
        />
      )}
      {tab === "activity-logs" && (
        <ResourceTable
          resource="activity-logs"
          columns={[
            { key: "username", label: "User" },
            { key: "action", label: "Action" },
            { key: "summary", label: "Summary" },
            { key: "created_at", label: "When", render: (r) => new Date(r.created_at).toLocaleString() },
          ]}
        />
      )}
    </div>
  );
}
