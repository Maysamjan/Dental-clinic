"use client";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useWebSocket } from "@/lib/ws";
import { useT } from "@/i18n/useT";
import PageHeader from "@/components/PageHeader";
import type { DashboardSummary } from "@/lib/types";

function Stat({ label, value, accent }: { label: string; value: React.ReactNode; accent?: string }) {
  return (
    <div className="card">
      <div className="text-sm text-slate-400">{label}</div>
      <div className={`mt-1 text-2xl font-bold ${accent ?? ""}`}>{value}</div>
    </div>
  );
}

export default function DashboardPage() {
  const t = useT();
  const qc = useQueryClient();

  const { data } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: async () =>
      (await api.get<DashboardSummary>("/dashboard/summary/")).data,
  });

  // Live refresh on workflow / payment / inventory events.
  useWebSocket("dashboard", () =>
    qc.invalidateQueries({ queryKey: ["dashboard-summary"] })
  );

  return (
    <div>
      <PageHeader title={t("dashboard")} subtitle="Live clinic overview" />

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Stat label={t("total_patients")} value={data?.total_patients ?? "—"} />
        <Stat label={t("todays_patients")} value={data?.todays_patients ?? "—"} />
        <Stat label={t("todays_appointments")} value={data?.todays_appointments ?? "—"} />
        <Stat
          label={t("todays_revenue")}
          value={data ? Number(data.todays_revenue).toLocaleString() : "—"}
          accent="text-brand-600"
        />
        <Stat label={t("outstanding_invoices")} value={data?.outstanding_invoices ?? "—"} />
        <Stat
          label={t("outstanding_balance")}
          value={data ? Number(data.outstanding_balance).toLocaleString() : "—"}
          accent="text-amber-600"
        />
        <Stat label={t("upcoming_followups")} value={data?.upcoming_followups ?? "—"} />
        <Stat
          label={t("inventory_alerts")}
          value={data?.inventory_alerts ?? "—"}
          accent={data && data.inventory_alerts > 0 ? "text-red-500" : ""}
        />
      </div>

      <div className="mt-6 card">
        <h2 className="mb-3 font-semibold">{t("recent_activity")}</h2>
        <ul className="divide-y divide-slate-100 text-sm dark:divide-slate-700">
          {(data?.recent_activities ?? []).map((a, i) => (
            <li key={i} className="flex justify-between py-2">
              <span>
                <span className="badge bg-brand-50 text-brand-700 me-2">
                  {a.action}
                </span>
                {a.summary}
              </span>
              <span className="text-slate-400">
                {new Date(a.created_at).toLocaleString()}
              </span>
            </li>
          ))}
          {(!data || data.recent_activities.length === 0) && (
            <li className="py-2 text-slate-400">No recent activity.</li>
          )}
        </ul>
      </div>
    </div>
  );
}
