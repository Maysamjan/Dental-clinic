"use client";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api, API_URL } from "@/lib/api";
import { useList, rowsOf } from "@/lib/hooks";
import { useT } from "@/i18n/useT";
import { useAuth } from "@/stores/auth";
import { hasPerm } from "@/lib/permissions";
import { useToast, apiError } from "@/stores/toast";
import PageHeader from "@/components/PageHeader";
import Modal from "@/components/Modal";
import ResourceCombo from "@/components/ResourceCombo";
import ResourceTable from "@/components/ResourceTable";

interface RxItem { medication: string; dosage: string; frequency: string; duration: string; notes: string; }
const emptyItem = (): RxItem => ({ medication: "", dosage: "", frequency: "", duration: "", notes: "" });

export default function PrescriptionsPage() {
  const t = useT();
  const qc = useQueryClient();
  const toast = useToast((s) => s.push);
  const permissions = useAuth((s) => s.user?.permissions);
  const canAdd = hasPerm(permissions, "prescriptions.add");
  const [open, setOpen] = useState(false);

  const [patient, setPatient] = useState<number | null>(null);
  const [doctor, setDoctor] = useState<number | null>(null);
  const [notes, setNotes] = useState("");
  const [items, setItems] = useState<RxItem[]>([emptyItem()]);

  const { data: tplData } = useList("prescription-templates");
  const templates = rowsOf<any>(tplData);

  const reset = () => { setPatient(null); setDoctor(null); setNotes(""); setItems([emptyItem()]); };
  const create = useMutation({
    mutationFn: () => api.post("/prescriptions/", { patient, doctor, notes, items: items.filter((i) => i.medication.trim()) }),
    onSuccess: () => { toast("success", "Prescription created."); qc.invalidateQueries({ queryKey: ["prescriptions"] }); setOpen(false); reset(); },
    onError: (e) => toast("error", apiError(e)),
  });

  const applyTemplate = (tplId: string) => {
    const tpl = templates.find((x) => String(x.id) === tplId);
    if (tpl?.items?.length) setItems(tpl.items.map((i: any) => ({ ...emptyItem(), ...i })));
  };
  const setItem = (idx: number, patch: Partial<RxItem>) => setItems(items.map((it, i) => (i === idx ? { ...it, ...patch } : it)));

  return (
    <div>
      <PageHeader
        title={t("prescriptions")}
        action={canAdd ? <button className="btn-primary" onClick={() => setOpen(true)}>+ New Prescription</button> : null}
      />
      <ResourceTable
        resource="prescriptions"
        columns={[
          { key: "id", label: "#" },
          { key: "patient_name", label: "Patient" },
          { key: "doctor_name", label: "Doctor" },
          { key: "created_at", label: "Date", render: (r) => new Date(r.created_at).toLocaleDateString() },
          { key: "pdf", label: "", render: (r) => <a className="text-brand-600 hover:underline" href={`${API_URL}/prescriptions/${r.id}/pdf/`} target="_blank" rel="noreferrer">PDF ↗</a> },
        ]}
      />

      <Modal open={open} title="New Prescription" onClose={() => setOpen(false)}>
        <form onSubmit={(e) => { e.preventDefault(); create.mutate(); }} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Patient</label>
              <ResourceCombo resource="patients" value={patient} onChange={setPatient} getLabel={(r) => `${r.code} — ${r.full_name}`} placeholder="Search patient…" />
            </div>
            <div>
              <label className="label">Doctor</label>
              <ResourceCombo resource="doctors" value={doctor} onChange={setDoctor} getLabel={(r) => r.name || `Doctor #${r.id}`} placeholder="Select doctor…" />
            </div>
          </div>

          {templates.length > 0 && (
            <div>
              <label className="label">Apply template</label>
              <select className="input" defaultValue="" onChange={(e) => applyTemplate(e.target.value)}>
                <option value="">— none —</option>
                {templates.map((tpl) => <option key={tpl.id} value={tpl.id}>{tpl.name}</option>)}
              </select>
            </div>
          )}

          <div className="space-y-2">
            <label className="label">Medications</label>
            {items.map((it, idx) => (
              <div key={idx} className="grid grid-cols-12 gap-1">
                <input className="input col-span-4" placeholder="Medication" value={it.medication} onChange={(e) => setItem(idx, { medication: e.target.value })} />
                <input className="input col-span-2" placeholder="Dosage" value={it.dosage} onChange={(e) => setItem(idx, { dosage: e.target.value })} />
                <input className="input col-span-2" placeholder="Frequency" value={it.frequency} onChange={(e) => setItem(idx, { frequency: e.target.value })} />
                <input className="input col-span-2" placeholder="Duration" value={it.duration} onChange={(e) => setItem(idx, { duration: e.target.value })} />
                <input className="input col-span-1" placeholder="Notes" value={it.notes} onChange={(e) => setItem(idx, { notes: e.target.value })} />
                <button type="button" className="col-span-1 text-red-500" onClick={() => setItems(items.filter((_, i) => i !== idx))}>✕</button>
              </div>
            ))}
            <button type="button" className="btn-ghost text-xs" onClick={() => setItems([...items, emptyItem()])}>+ Add medication</button>
          </div>

          <div><label className="label">Notes</label><input className="input" value={notes} onChange={(e) => setNotes(e.target.value)} /></div>

          <div className="flex justify-end gap-2 pt-1">
            <button type="button" className="btn-ghost" onClick={() => setOpen(false)}>{t("cancel")}</button>
            <button className="btn-primary" disabled={create.isPending || !patient || !items.some((i) => i.medication.trim())}>{t("save")}</button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
