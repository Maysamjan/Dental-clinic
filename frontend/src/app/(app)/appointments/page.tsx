"use client";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useList, rowsOf } from "@/lib/hooks";
import { useT } from "@/i18n/useT";
import { useAuth } from "@/stores/auth";
import { hasPerm } from "@/lib/permissions";
import { useToast, apiError } from "@/stores/toast";
import PageHeader from "@/components/PageHeader";
import Modal from "@/components/Modal";
import ResourceCombo from "@/components/ResourceCombo";

const STATUS: Record<string, string> = {
  SCHEDULED: "bg-slate-100 text-slate-700",
  CONFIRMED: "bg-blue-100 text-blue-700",
  ARRIVED: "bg-amber-100 text-amber-700",
  COMPLETED: "bg-green-100 text-green-700",
  CANCELLED: "bg-red-100 text-red-700",
  NO_SHOW: "bg-red-100 text-red-700",
};

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}

export default function AppointmentsPage() {
  const t = useT();
  const qc = useQueryClient();
  const toast = useToast((s) => s.push);
  const permissions = useAuth((s) => s.user?.permissions);
  const canManage = hasPerm(permissions, "appointments.change");

  const [day, setDay] = useState(todayStr());
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<{ patient: number | null; doctor: number | null; start: string; reason: string }>({
    patient: null,
    doctor: null,
    start: "",
    reason: "",
  });

  const params = { from: day, to: day, ordering: "start" };
  const { data, isLoading } = useList("appointments", params);
  const rows = rowsOf<any>(data);

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ["appointments"] });
    qc.invalidateQueries({ queryKey: ["visit-queue"] });
  };

  const create = useMutation({
    mutationFn: () =>
      api.post("/appointments/", {
        patient: form.patient,
        doctor: form.doctor,
        start: new Date(form.start).toISOString(),
        reason: form.reason,
      }),
    onSuccess: () => {
      toast("success", "Appointment scheduled.");
      invalidate();
      setOpen(false);
      setForm({ patient: null, doctor: null, start: "", reason: "" });
    },
    onError: (e) => toast("error", apiError(e)),
  });

  const act = useMutation({
    mutationFn: ({ id, action }: { id: number; action: string }) =>
      api.post(`/appointments/${id}/${action}/`),
    onSuccess: (_d, v) => {
      toast("success", v.action === "arrive" ? "Patient sent to queue." : "Updated.");
      invalidate();
    },
    onError: (e) => toast("error", apiError(e)),
  });

  return (
    <div>
      <PageHeader
        title={t("appointments")}
        subtitle="Daily schedule"
        action={
          canManage ? (
            <button className="btn-primary" onClick={() => setOpen(true)}>
              + New Appointment
            </button>
          ) : null
        }
      />

      <div className="mb-4 flex items-center gap-2">
        <label className="label mb-0">Date</label>
        <input type="date" className="input w-auto" value={day} onChange={(e) => setDay(e.target.value)} />
      </div>

      <div className="card overflow-x-auto p-0">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-xs uppercase text-slate-500 dark:bg-slate-700/50">
            <tr>
              {["Time", "Patient", "Doctor", "Reason", "Status", ""].map((h) => (
                <th key={h} className="px-4 py-2 text-start font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr><td colSpan={6} className="p-6 text-center text-slate-400">Loading…</td></tr>
            )}
            {!isLoading && rows.length === 0 && (
              <tr><td colSpan={6} className="p-6 text-center text-slate-400">No appointments for this day.</td></tr>
            )}
            {rows.map((a) => (
              <tr key={a.id} className="border-t border-slate-100 dark:border-slate-700">
                <td className="px-4 py-2">{new Date(a.start).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</td>
                <td className="px-4 py-2">{a.patient_name}</td>
                <td className="px-4 py-2">{a.doctor_name || "—"}</td>
                <td className="px-4 py-2">{a.reason || "—"}</td>
                <td className="px-4 py-2"><span className={`badge ${STATUS[a.status]}`}>{a.status}</span></td>
                <td className="px-4 py-2">
                  {canManage && (
                    <div className="flex gap-1">
                      {["SCHEDULED"].includes(a.status) && (
                        <button className="btn-ghost px-2 py-1 text-xs" onClick={() => act.mutate({ id: a.id, action: "confirm" })}>Confirm</button>
                      )}
                      {["SCHEDULED", "CONFIRMED"].includes(a.status) && (
                        <button className="btn-primary px-2 py-1 text-xs" onClick={() => act.mutate({ id: a.id, action: "arrive" })}>Arrive</button>
                      )}
                      {["SCHEDULED", "CONFIRMED"].includes(a.status) && (
                        <button className="btn-ghost px-2 py-1 text-xs" onClick={() => act.mutate({ id: a.id, action: "no-show" })}>No-Show</button>
                      )}
                      {!["CANCELLED", "COMPLETED"].includes(a.status) && (
                        <button className="btn-ghost px-2 py-1 text-xs text-red-600" onClick={() => act.mutate({ id: a.id, action: "cancel" })}>Cancel</button>
                      )}
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal open={open} title="New Appointment" onClose={() => setOpen(false)}>
        <form
          onSubmit={(e) => { e.preventDefault(); create.mutate(); }}
          className="space-y-3"
        >
          <div>
            <label className="label">Patient</label>
            <ResourceCombo
              resource="patients"
              value={form.patient}
              onChange={(id) => setForm({ ...form, patient: id })}
              getLabel={(r) => `${r.code} — ${r.full_name}`}
              placeholder="Search patient…"
            />
          </div>
          <div>
            <label className="label">Doctor</label>
            <ResourceCombo
              resource="doctors"
              value={form.doctor}
              onChange={(id) => setForm({ ...form, doctor: id })}
              getLabel={(r) => r.name || `Doctor #${r.id}`}
              placeholder="Select doctor…"
            />
          </div>
          <div>
            <label className="label">Date &amp; Time</label>
            <input
              type="datetime-local"
              className="input"
              required
              value={form.start}
              onChange={(e) => setForm({ ...form, start: e.target.value })}
            />
          </div>
          <div>
            <label className="label">Reason</label>
            <input className="input" value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" className="btn-ghost" onClick={() => setOpen(false)}>{t("cancel")}</button>
            <button className="btn-primary" disabled={create.isPending || !form.patient}>{t("save")}</button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
