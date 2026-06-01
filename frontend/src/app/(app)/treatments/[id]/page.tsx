"use client";
import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuth } from "@/stores/auth";
import { hasPerm } from "@/lib/permissions";
import { useToast, apiError } from "@/stores/toast";
import PageHeader from "@/components/PageHeader";
import ResourceCombo from "@/components/ResourceCombo";

const T_STATUS = ["PLANNED", "IN_PROGRESS", "COMPLETED", "CANCELLED"];
const STATUS_COLOR: Record<string, string> = {
  PLANNED: "bg-slate-100 text-slate-700",
  IN_PROGRESS: "bg-blue-100 text-blue-700",
  COMPLETED: "bg-green-100 text-green-700",
  CANCELLED: "bg-red-100 text-red-700",
};

export default function PlanDetailPage() {
  const { id } = useParams<{ id: string }>();
  const qc = useQueryClient();
  const toast = useToast((s) => s.push);
  const permissions = useAuth((s) => s.user?.permissions);
  const canEdit = hasPerm(permissions, "treatments.change");
  const canBill = hasPerm(permissions, "billing.add");

  const { data: plan } = useQuery({
    queryKey: ["treatment-plan", id],
    queryFn: async () => (await api.get(`/treatment-plans/${id}/`)).data,
  });

  const [stageName, setStageName] = useState("");
  const refresh = () => qc.invalidateQueries({ queryKey: ["treatment-plan", id] });
  const onErr = (e: any) => toast("error", apiError(e));

  const addStage = useMutation({
    mutationFn: () => api.post("/treatment-stages/", { plan: id, name: stageName, order: (plan?.stages?.length ?? 0) + 1 }),
    onSuccess: () => { setStageName(""); refresh(); },
    onError: onErr,
  });
  const setTreatmentStatus = useMutation({
    mutationFn: ({ tid, status }: { tid: number; status: string }) => api.patch(`/treatments/${tid}/`, { status }),
    onSuccess: () => { toast("success", "Treatment updated."); refresh(); },
    onError: onErr,
  });
  const saveEstimate = useMutation({
    mutationFn: (val: string) => api.patch(`/treatment-plans/${id}/`, { estimated_cost: val }),
    onSuccess: () => { toast("success", "Estimate saved."); refresh(); },
    onError: onErr,
  });
  const generateInvoice = useMutation({
    mutationFn: (all: boolean) => api.post(`/treatment-plans/${id}/generate-invoice/`, { all }),
    onSuccess: (res) => { toast("success", `Invoice ${res.data.number} created.`); },
    onError: onErr,
  });

  if (!plan) return <div className="text-slate-400">Loading plan…</div>;

  return (
    <div>
      <PageHeader
        title={plan.title}
        subtitle={<>{plan.patient_name} · {plan.status} · <Link className="text-brand-600 hover:underline" href={`/patients/${plan.patient}`}>profile</Link></>}
        action={canBill ? (
          <div className="flex gap-2">
            <button className="btn-ghost" onClick={() => generateInvoice.mutate(false)} disabled={generateInvoice.isPending}>Invoice completed</button>
            <button className="btn-primary" onClick={() => generateInvoice.mutate(true)} disabled={generateInvoice.isPending}>Invoice all</button>
          </div>
        ) : null}
      />

      {/* Progress + costs */}
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <div className="card md:col-span-2">
          <div className="mb-1 flex justify-between text-sm"><span>Completion</span><span className="font-bold">{plan.progress_percent}%</span></div>
          <div className="h-3 w-full rounded-full bg-slate-200"><div className="h-3 rounded-full bg-brand-500 transition-all" style={{ width: `${plan.progress_percent}%` }} /></div>
        </div>
        <EstimateCard value={plan.estimated_cost} onSave={(v) => saveEstimate.mutate(v)} editable={canEdit} />
        <div className="card">
          <div className="text-xs text-slate-400">Planned / Actual</div>
          <div className="text-lg font-bold">{Number(plan.planned_cost).toLocaleString()} <span className="text-sm font-normal text-slate-400">/</span> <span className="text-brand-600">{Number(plan.actual_cost).toLocaleString()}</span></div>
        </div>
      </div>

      {/* Stage timeline */}
      <div className="space-y-4">
        {plan.stages.map((stage: any) => (
          <StageCard key={stage.id} stage={stage} planId={id} canEdit={canEdit}
            onChangeStatus={(tid, status) => setTreatmentStatus.mutate({ tid, status })} onRefresh={refresh} onErr={onErr} />
        ))}
        {plan.stages.length === 0 && <div className="card text-slate-400">No stages yet. Add the first stage below.</div>}
      </div>

      {canEdit && (
        <form onSubmit={(e) => { e.preventDefault(); if (stageName) addStage.mutate(); }} className="mt-4 flex gap-2">
          <input className="input max-w-xs" placeholder="New stage name (e.g. Root Canal)" value={stageName} onChange={(e) => setStageName(e.target.value)} />
          <button className="btn-ghost" disabled={!stageName || addStage.isPending}>+ Add Stage</button>
        </form>
      )}
    </div>
  );

  // status select rendered per-treatment uses T_STATUS / STATUS_COLOR above
}

function EstimateCard({ value, onSave, editable }: { value: string; onSave: (v: string) => void; editable: boolean }) {
  const [v, setV] = useState(value);
  return (
    <div className="card">
      <div className="text-xs text-slate-400">Estimated Cost</div>
      {editable ? (
        <div className="flex gap-1">
          <input className="input py-1" value={v} onChange={(e) => setV(e.target.value)} onBlur={() => v !== value && onSave(v)} />
        </div>
      ) : (
        <div className="text-lg font-bold">{Number(value).toLocaleString()}</div>
      )}
    </div>
  );
}

function StageCard({ stage, planId, canEdit, onChangeStatus, onRefresh, onErr }: {
  stage: any; planId: string; canEdit: boolean;
  onChangeStatus: (tid: number, status: string) => void; onRefresh: () => void; onErr: (e: any) => void;
}) {
  const [open, setOpen] = useState(false);
  const [tForm, setTForm] = useState<{ catalog_item: number | null; description: string; quantity: number; unit_price: string; status: string }>({
    catalog_item: null, description: "", quantity: 1, unit_price: "0", status: "PLANNED",
  });

  const addTreatment = useMutation({
    mutationFn: () => api.post("/treatments/", { stage: stage.id, ...tForm }),
    onSuccess: () => { setOpen(false); setTForm({ catalog_item: null, description: "", quantity: 1, unit_price: "0", status: "PLANNED" }); onRefresh(); },
    onError: onErr,
  });

  return (
    <div className="card">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="font-semibold">{stage.order}. {stage.name}</h3>
        {canEdit && <button className="btn-ghost px-2 py-1 text-xs" onClick={() => setOpen((o) => !o)}>+ Procedure</button>}
      </div>

      <table className="w-full text-sm">
        <tbody>
          {stage.treatments.length === 0 && <tr><td className="py-2 text-slate-400">No procedures.</td></tr>}
          {stage.treatments.map((tr: any) => (
            <tr key={tr.id} className="border-t border-slate-100 dark:border-slate-700">
              <td className="py-2">{tr.description || tr.catalog_name}{tr.tooth_number ? ` (tooth ${tr.tooth_number})` : ""}</td>
              <td className="py-2 text-slate-400">×{tr.quantity}</td>
              <td className="py-2">{Number(tr.total).toLocaleString()}</td>
              <td className="py-2 text-end">
                {canEdit ? (
                  <select className="input w-auto py-1" value={tr.status} onChange={(e) => onChangeStatus(tr.id, e.target.value)}>
                    {T_STATUS.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                ) : (
                  <span className={`badge ${STATUS_COLOR[tr.status]}`}>{tr.status}</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {open && (
        <form onSubmit={(e) => { e.preventDefault(); addTreatment.mutate(); }} className="mt-3 grid grid-cols-2 gap-2 rounded-lg bg-slate-50 p-3 dark:bg-slate-700/40">
          <div className="col-span-2">
            <label className="label">Procedure (catalog)</label>
            <ResourceCombo resource="treatment-catalog" value={tForm.catalog_item}
              onChange={(id, row) => setTForm({ ...tForm, catalog_item: id, description: row?.name ?? tForm.description, unit_price: row ? String(row.default_price) : tForm.unit_price })}
              getLabel={(r) => `${r.name} (${Number(r.default_price).toLocaleString()})`} placeholder="Select procedure…" />
          </div>
          <div><label className="label">Qty</label><input type="number" min={1} className="input" value={tForm.quantity} onChange={(e) => setTForm({ ...tForm, quantity: Number(e.target.value) })} /></div>
          <div><label className="label">Unit Price</label><input className="input" value={tForm.unit_price} onChange={(e) => setTForm({ ...tForm, unit_price: e.target.value })} /></div>
          <div className="col-span-2 flex justify-end gap-2">
            <button type="button" className="btn-ghost" onClick={() => setOpen(false)}>Cancel</button>
            <button className="btn-primary" disabled={addTreatment.isPending}>Add</button>
          </div>
        </form>
      )}
    </div>
  );
}
