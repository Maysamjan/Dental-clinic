"use client";
import { useState } from "react";
import Link from "next/link";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useList, rowsOf } from "@/lib/hooks";
import { useWebSocket } from "@/lib/ws";
import { useT } from "@/i18n/useT";
import { useToast, apiError } from "@/stores/toast";
import { APPT_STATUS_FA } from "@/lib/labels";
import PageHeader from "@/components/PageHeader";
import type { QueueItem } from "@/lib/types";

const STATUS_LABEL: Record<string, string> = {
  WAITING: "در انتظار",
  IN_CONSULTATION: "در حال معاینه",
  TREATMENT_IN_PROGRESS: "در حال تداوی",
  COMPLETED: "تکمیل‌شده",
};
const STATUS_COLOR: Record<string, string> = {
  WAITING: "bg-amber-100 text-amber-700",
  IN_CONSULTATION: "bg-blue-100 text-blue-700",
  TREATMENT_IN_PROGRESS: "bg-purple-100 text-purple-700",
  COMPLETED: "bg-green-100 text-green-700",
};
const NEXT: Record<string, string> = {
  WAITING: "IN_CONSULTATION",
  IN_CONSULTATION: "TREATMENT_IN_PROGRESS",
  TREATMENT_IN_PROGRESS: "COMPLETED",
};

function today() {
  return new Date().toISOString().slice(0, 10);
}

export default function ReceptionPage() {
  const t = useT();
  const qc = useQueryClient();
  const toast = useToast((s) => s.push);
  const [tab, setTab] = useState<"queue" | "appointments" | "completed">("queue");

  const { data: queue = [] } = useQuery({
    queryKey: ["visit-queue"],
    queryFn: async () => (await api.get<QueueItem[]>("/visits/queue/")).data,
  });
  const { data: apptData } = useList("appointments", { from: today(), to: today(), ordering: "start" });
  const appts = rowsOf<any>(apptData);
  const { data: completedData } = useList("visits", { visit_date: today(), workflow_status: "COMPLETED" });
  const completed = rowsOf<any>(completedData);

  const refresh = () => {
    qc.invalidateQueries({ queryKey: ["visit-queue"] });
    qc.invalidateQueries({ queryKey: ["appointments"] });
    qc.invalidateQueries({ queryKey: ["visits"] });
  };
  useWebSocket("workflow", refresh);

  const advance = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => api.post(`/visits/${id}/advance/`, { status }),
    onSuccess: refresh,
    onError: (e) => toast("error", apiError(e)),
  });
  const arrive = useMutation({
    mutationFn: (id: number) => api.post(`/appointments/${id}/arrive/`),
    onSuccess: () => { toast("success", "بیمار به صف اضافه شد."); refresh(); },
    onError: (e) => toast("error", apiError(e)),
  });

  const waitingCount = queue.filter((q) => q.workflow_status === "WAITING").length;

  const Tab = ({ id, label, count }: { id: typeof tab; label: string; count: number }) => (
    <button onClick={() => setTab(id)} className={tab === id ? "btn-primary" : "btn-ghost"}>
      {label} <span className="ms-1 rounded-full bg-black/10 px-1.5 text-xs">{count}</span>
    </button>
  );

  return (
    <div>
      <PageHeader title={t("reception")} subtitle="جریان زنده بیماران" />

      <div className="mb-4 flex flex-wrap gap-2">
        <Tab id="queue" label="صف انتظار" count={queue.length} />
        <Tab id="appointments" label="نوبت‌های امروز" count={appts.length} />
        <Tab id="completed" label="تکمیل‌شده" count={completed.length} />
        <span className="ms-auto self-center text-sm text-slate-400">
          {waitingCount} نفر در انتظار
        </span>
      </div>

      {tab === "queue" && (
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {queue.length === 0 && <div className="card text-slate-400">صف خالی است.</div>}
          {queue.map((v) => (
            <div key={v.id} className="card">
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-xs text-slate-400">#{v.queue_number}</div>
                  <div className="text-lg font-semibold">{v.patient_name}</div>
                </div>
                <span className={`badge ${STATUS_COLOR[v.workflow_status]}`}>{STATUS_LABEL[v.workflow_status]}</span>
              </div>
              <div className="mt-2 text-xs text-slate-400">
                زمان حضور: {v.arrival_time ? new Date(v.arrival_time).toLocaleTimeString() : "—"}
              </div>
              {v.medical_summary && (
                <div className="mt-2 rounded-lg bg-red-50 px-2 py-1 text-xs text-red-700">⚠ {v.medical_summary}</div>
              )}
              <div className="mt-3 flex gap-2">
                <Link href={`/visits/${v.id}`} className="btn-ghost flex-1">باز کردن</Link>
                {NEXT[v.workflow_status] && (
                  <button
                    className="btn-primary flex-1"
                    disabled={advance.isPending}
                    onClick={() => advance.mutate({ id: v.id, status: NEXT[v.workflow_status] })}
                  >
                    → {STATUS_LABEL[NEXT[v.workflow_status]]}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "appointments" && (
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500 dark:bg-slate-700/50">
              <tr>{[t("time"), t("patient"), t("doctor"), t("status"), ""].map((h, i) => <th key={i} className="px-4 py-2 text-start font-medium">{h}</th>)}</tr>
            </thead>
            <tbody>
              {appts.length === 0 && <tr><td colSpan={5} className="p-6 text-center text-slate-400">امروز نوبتی ثبت نشده است.</td></tr>}
              {appts.map((a) => (
                <tr key={a.id} className="border-t border-slate-100 dark:border-slate-700">
                  <td className="px-4 py-2">{new Date(a.start).toLocaleTimeString('en-US', { hour: "2-digit", minute: "2-digit" })}</td>
                  <td className="px-4 py-2">{a.patient_name}</td>
                  <td className="px-4 py-2">{a.doctor_name || "—"}</td>
                  <td className="px-4 py-2"><span className={`badge ${STATUS_COLOR[a.status] || "bg-slate-100 text-slate-700"}`}>{APPT_STATUS_FA[a.status] ?? a.status}</span></td>
                  <td className="px-4 py-2">
                    {["SCHEDULED", "CONFIRMED"].includes(a.status) && (
                      <button className="btn-primary px-3 py-1 text-xs" disabled={arrive.isPending} onClick={() => arrive.mutate(a.id)}>
                        ثبت حضور
                      </button>
                    )}
                    {a.status === "ARRIVED" && <span className="text-xs text-amber-600">در صف</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === "completed" && (
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500 dark:bg-slate-700/50">
              <tr>{["#", t("patient"), t("doctor"), "تشخیص"].map((h, i) => <th key={i} className="px-4 py-2 text-start font-medium">{h}</th>)}</tr>
            </thead>
            <tbody>
              {completed.length === 0 && <tr><td colSpan={4} className="p-6 text-center text-slate-400">امروز ویزیت تکمیل‌شده‌ای نیست.</td></tr>}
              {completed.map((v) => (
                <tr key={v.id} className="border-t border-slate-100 dark:border-slate-700">
                  <td className="px-4 py-2">{v.queue_number}</td>
                  <td className="px-4 py-2">{v.patient_name}</td>
                  <td className="px-4 py-2">{v.doctor_name || "—"}</td>
                  <td className="px-4 py-2">{v.diagnosis || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
