"use client";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useWebSocket } from "@/lib/ws";
import { useT } from "@/i18n/useT";
import PageHeader from "@/components/PageHeader";
import type { QueueItem } from "@/lib/types";

const STATUS_LABEL: Record<string, string> = {
  WAITING: "Waiting",
  IN_CONSULTATION: "In Consultation",
  TREATMENT_IN_PROGRESS: "Treatment In Progress",
  COMPLETED: "Completed",
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

export default function ReceptionPage() {
  const t = useT();
  const qc = useQueryClient();

  const { data: queue = [] } = useQuery({
    queryKey: ["visit-queue"],
    queryFn: async () => (await api.get<QueueItem[]>("/visits/queue/")).data,
  });

  // Live updates as patients arrive / move through the workflow.
  useWebSocket("workflow", () =>
    qc.invalidateQueries({ queryKey: ["visit-queue"] })
  );

  const advance = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      api.post(`/visits/${id}/advance/`, { status }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["visit-queue"] }),
  });

  return (
    <div>
      <PageHeader title={t("reception")} subtitle="Real-time patient flow" />

      {queue.length === 0 && (
        <div className="card text-slate-400">The queue is empty.</div>
      )}

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {queue.map((v) => (
          <div key={v.id} className="card">
            <div className="flex items-start justify-between">
              <div>
                <div className="text-xs text-slate-400">#{v.queue_number}</div>
                <div className="text-lg font-semibold">{v.patient_name}</div>
              </div>
              <span className={`badge ${STATUS_COLOR[v.workflow_status]}`}>
                {STATUS_LABEL[v.workflow_status]}
              </span>
            </div>
            <div className="mt-2 text-xs text-slate-400">
              Arrived:{" "}
              {v.arrival_time
                ? new Date(v.arrival_time).toLocaleTimeString()
                : "—"}
            </div>
            {v.medical_summary && (
              <div className="mt-2 rounded-lg bg-red-50 px-2 py-1 text-xs text-red-700">
                {v.medical_summary}
              </div>
            )}
            {NEXT[v.workflow_status] && (
              <button
                className="btn-primary mt-3 w-full"
                disabled={advance.isPending}
                onClick={() =>
                  advance.mutate({ id: v.id, status: NEXT[v.workflow_status] })
                }
              >
                → {STATUS_LABEL[NEXT[v.workflow_status]]}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
