"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
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

export default function TreatmentsPage() {
  const t = useT();
  const qc = useQueryClient();
  const router = useRouter();
  const toast = useToast((s) => s.push);
  const permissions = useAuth((s) => s.user?.permissions);
  const canAdd = hasPerm(permissions, "treatments.add");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<{ patient: number | null; doctor: number | null; title: string }>({
    patient: null, doctor: null, title: "",
  });

  const { data } = useList("treatment-plans");
  const plans = rowsOf<any>(data);

  const create = useMutation({
    mutationFn: () => api.post("/treatment-plans/", { ...form, status: "ACTIVE" }),
    onSuccess: (res) => {
      toast("success", "Treatment plan created.");
      qc.invalidateQueries({ queryKey: ["treatment-plans"] });
      setOpen(false);
      router.push(`/treatments/${res.data.id}`);
    },
    onError: (e) => toast("error", apiError(e)),
  });

  return (
    <div>
      <PageHeader
        title={t("treatments")}
        subtitle="Treatment plans & progress"
        action={canAdd ? <button className="btn-primary" onClick={() => setOpen(true)}>+ New Plan</button> : null}
      />

      <div className="card overflow-x-auto p-0">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-xs uppercase text-slate-500 dark:bg-slate-700/50">
            <tr>{["Plan", "Patient", "Status", "Progress", "Est. Cost", ""].map((h) => <th key={h} className="px-4 py-2 text-start font-medium">{h}</th>)}</tr>
          </thead>
          <tbody>
            {plans.length === 0 && <tr><td colSpan={6} className="p-6 text-center text-slate-400">No treatment plans.</td></tr>}
            {plans.map((p) => (
              <tr key={p.id} className="border-t border-slate-100 dark:border-slate-700">
                <td className="px-4 py-2"><Link className="text-brand-600 hover:underline" href={`/treatments/${p.id}`}>{p.title}</Link></td>
                <td className="px-4 py-2">{p.patient_name}</td>
                <td className="px-4 py-2">{p.status}</td>
                <td className="px-4 py-2">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-24 rounded-full bg-slate-200"><div className="h-2 rounded-full bg-brand-500" style={{ width: `${p.progress_percent}%` }} /></div>
                    <span className="text-xs">{p.progress_percent}%</span>
                  </div>
                </td>
                <td className="px-4 py-2">{Number(p.estimated_cost).toLocaleString()}</td>
                <td className="px-4 py-2"><Link className="text-brand-600 hover:underline" href={`/treatments/${p.id}`}>Open →</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal open={open} title="New Treatment Plan" onClose={() => setOpen(false)}>
        <form onSubmit={(e) => { e.preventDefault(); create.mutate(); }} className="space-y-3">
          <div>
            <label className="label">Patient</label>
            <ResourceCombo resource="patients" value={form.patient} onChange={(id) => setForm({ ...form, patient: id })}
              getLabel={(r) => `${r.code} — ${r.full_name}`} placeholder="Search patient…" />
          </div>
          <div>
            <label className="label">Doctor</label>
            <ResourceCombo resource="doctors" value={form.doctor} onChange={(id) => setForm({ ...form, doctor: id })}
              getLabel={(r) => r.name || `Doctor #${r.id}`} placeholder="Select doctor…" />
          </div>
          <div>
            <label className="label">Title</label>
            <input className="input" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="e.g. Full-mouth rehabilitation" />
          </div>
          <div className="flex justify-end gap-2 pt-1">
            <button type="button" className="btn-ghost" onClick={() => setOpen(false)}>Cancel</button>
            <button className="btn-primary" disabled={create.isPending || !form.patient || !form.title}>Create</button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
