"use client";
import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { api, API_URL } from "@/lib/api";
import { useAuth } from "@/stores/auth";
import { hasPerm } from "@/lib/permissions";
import { useToast, apiError } from "@/stores/toast";
import PageHeader from "@/components/PageHeader";
import Modal from "@/components/Modal";

type Tab = "overview" | "visits" | "treatments" | "prescriptions" | "billing" | "documents" | "followups";

export default function PatientProfilePage() {
  const { id } = useParams<{ id: string }>();
  const qc = useQueryClient();
  const toast = useToast((s) => s.push);
  const permissions = useAuth((s) => s.user?.permissions);
  const canEdit = hasPerm(permissions, "patients.change");
  const canBilling = hasPerm(permissions, "billing.view");
  const [tab, setTab] = useState<Tab>("overview");
  const [editOpen, setEditOpen] = useState(false);

  const { data } = useQuery({
    queryKey: ["patient-history", id],
    queryFn: async () => (await api.get(`/patients/${id}/history/`)).data,
  });
  const p = data?.patient;
  const fin = data?.financial_summary;
  const fmt = (n: any) => Number(n || 0).toLocaleString();

  const tabs: [Tab, string, number][] = [
    ["overview", "Overview", 0],
    ["visits", "Visits", data?.visits?.length ?? 0],
    ["treatments", "Treatments", data?.treatment_plans?.length ?? 0],
    ["prescriptions", "Prescriptions", data?.prescriptions?.length ?? 0],
    ["billing", "Billing", data?.invoices?.length ?? 0],
    ["documents", "Documents", data?.documents?.length ?? 0],
    ["followups", "Follow-Ups", data?.follow_ups?.length ?? 0],
  ];

  return (
    <div>
      <PageHeader
        title={p ? p.full_name : "Patient"}
        subtitle={p ? `${p.code} · ${p.gender} · ${p.age ?? "?"} yrs · ${p.phone || "no phone"}` : ""}
        action={
          <div className="flex gap-2">
            <Link href={`/dental-chart?patient=${id}`} className="btn-ghost">🦷 Chart</Link>
            <Link href="/appointments" className="btn-ghost">📅 Appointment</Link>
            {canEdit && <button className="btn-primary" onClick={() => setEditOpen(true)}>Edit</button>}
          </div>
        }
      />

      {p?.allergies && (
        <div className="mb-4 rounded-lg border border-red-300 bg-red-50 px-4 py-2 font-medium text-red-700">
          ⚠ Allergies: {p.allergies}
        </div>
      )}

      {/* Financial summary */}
      {canBilling && fin && (
        <div className="mb-4 grid grid-cols-3 gap-4">
          <div className="card"><div className="text-xs text-slate-400">Total Billed</div><div className="text-xl font-bold">{fmt(fin.total_billed)}</div></div>
          <div className="card"><div className="text-xs text-slate-400">Total Paid</div><div className="text-xl font-bold text-brand-600">{fmt(fin.total_paid)}</div></div>
          <div className="card"><div className="text-xs text-slate-400">Outstanding</div><div className={`text-xl font-bold ${Number(fin.outstanding_balance) > 0 ? "text-amber-600" : ""}`}>{fmt(fin.outstanding_balance)}</div></div>
        </div>
      )}

      <div className="mb-4 flex flex-wrap gap-2">
        {tabs.map(([key, label, count]) => (
          <button key={key} onClick={() => setTab(key)} className={tab === key ? "btn-primary" : "btn-ghost"}>
            {label}{count > 0 && <span className="ms-1 rounded-full bg-black/10 px-1.5 text-xs">{count}</span>}
          </button>
        ))}
      </div>

      {tab === "overview" && p && (
        <div className="grid gap-4 md:grid-cols-2">
          <Info label="Medical History" value={p.medical_history} />
          <Info label="Allergies" value={p.allergies} danger />
          <Info label="Address" value={p.address} />
          <Info label="Emergency Contact" value={[p.emergency_contact_name, p.emergency_contact_phone].filter(Boolean).join(" · ")} />
          <Info label="Registration Date" value={p.registration_date} />
          <Info label="Notes" value={p.notes} />
        </div>
      )}

      {tab === "visits" && (
        <Table rows={data?.visits} cols={[["visit_date", "Date"], ["doctor_name", "Doctor"], ["diagnosis", "Diagnosis"], ["workflow_status", "Status"]]}
          link={(r) => `/visits/${r.id}`} />
      )}
      {tab === "treatments" && (
        <Table rows={data?.treatment_plans} cols={[["title", "Plan"], ["status", "Status"], ["progress_percent", "Progress %"]]} />
      )}
      {tab === "prescriptions" && (
        <Table rows={data?.prescriptions} cols={[["id", "#"], ["doctor_name", "Doctor"], ["created_at", "Date"]]}
          extra={(r) => <a className="text-brand-600 hover:underline" href={`${API_URL}/prescriptions/${r.id}/pdf/`} target="_blank" rel="noreferrer">PDF ↗</a>} />
      )}
      {tab === "billing" && (
        <div className="space-y-4">
          <Table title="Invoices" rows={data?.invoices} cols={[["number", "Invoice"], ["total", "Total"], ["paid_amount", "Paid"], ["balance", "Balance"], ["status", "Status"]]}
            extra={(r) => <a className="text-brand-600 hover:underline" href={`${API_URL}/invoices/${r.id}/pdf/`} target="_blank" rel="noreferrer">PDF ↗</a>} />
          <Table title="Payments" rows={data?.payments} cols={[["invoice_number", "Invoice"], ["amount", "Amount"], ["method", "Method"], ["paid_at", "Date"]]} />
        </div>
      )}
      {tab === "documents" && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {(data?.documents ?? []).length === 0 && <div className="card text-slate-400">No documents.</div>}
          {(data?.documents ?? []).map((d: any) => (
            <a key={d.id} href={d.file_url} target="_blank" rel="noreferrer" className="card hover:ring-2 hover:ring-brand-300">
              <div className="text-3xl">{d.type === "XRAY" || d.type === "OPG" || d.type === "PHOTO" ? "🖼️" : "📄"}</div>
              <div className="mt-1 truncate text-sm font-medium">{d.title || d.type}</div>
              <div className="text-xs text-slate-400">{d.type}</div>
            </a>
          ))}
        </div>
      )}
      {tab === "followups" && (
        <Table rows={data?.follow_ups} cols={[["due_date", "Due"], ["type", "Type"], ["note", "Note"], ["status", "Status"]]} />
      )}

      {p && (
        <EditModal open={editOpen} onClose={() => setEditOpen(false)} patient={p}
          onSaved={() => { qc.invalidateQueries({ queryKey: ["patient-history", id] }); toast("success", "Patient updated."); }}
          onError={(e) => toast("error", apiError(e))} />
      )}
    </div>
  );
}

function Info({ label, value, danger }: { label: string; value?: string; danger?: boolean }) {
  return (
    <div className="card">
      <div className="text-xs text-slate-400">{label}</div>
      <div className={danger && value ? "text-red-600" : ""}>{value || "—"}</div>
    </div>
  );
}

function Table({ title, rows, cols, link, extra }: {
  title?: string; rows?: any[]; cols: [string, string][];
  link?: (r: any) => string; extra?: (r: any) => React.ReactNode;
}) {
  return (
    <div className="card overflow-x-auto p-0">
      {title && <div className="border-b border-slate-200 px-4 py-2 font-semibold dark:border-slate-700">{title}</div>}
      <table className="w-full text-sm">
        <thead className="bg-slate-50 text-xs uppercase text-slate-500 dark:bg-slate-700/50">
          <tr>{cols.map(([, l]) => <th key={l} className="px-4 py-2 text-start font-medium">{l}</th>)}{extra && <th />}</tr>
        </thead>
        <tbody>
          {(!rows || rows.length === 0) && <tr><td colSpan={cols.length + 1} className="p-6 text-center text-slate-400">No records.</td></tr>}
          {rows?.map((r, i) => (
            <tr key={i} className="border-t border-slate-100 dark:border-slate-700">
              {cols.map(([k], j) => (
                <td key={k} className="px-4 py-2">
                  {j === 0 && link ? <Link className="text-brand-600 hover:underline" href={link(r)}>{String(r[k] ?? "—")}</Link> : String(r[k] ?? "—")}
                </td>
              ))}
              {extra && <td className="px-4 py-2">{extra(r)}</td>}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function EditModal({ open, onClose, patient, onSaved, onError }: {
  open: boolean; onClose: () => void; patient: any; onSaved: () => void; onError: (e: any) => void;
}) {
  const [form, setForm] = useState({
    full_name: patient.full_name, phone: patient.phone || "", address: patient.address || "",
    allergies: patient.allergies || "", medical_history: patient.medical_history || "",
    emergency_contact_name: patient.emergency_contact_name || "", emergency_contact_phone: patient.emergency_contact_phone || "",
    notes: patient.notes || "",
  });
  const save = useMutation({
    mutationFn: () => api.patch(`/patients/${patient.id}/`, form),
    onSuccess: () => { onSaved(); onClose(); },
    onError,
  });
  return (
    <Modal open={open} title="Edit Patient" onClose={onClose}>
      <form onSubmit={(e) => { e.preventDefault(); save.mutate(); }} className="grid grid-cols-2 gap-3">
        <Field label="Full Name" v={form.full_name} on={(x) => setForm({ ...form, full_name: x })} span />
        <Field label="Phone" v={form.phone} on={(x) => setForm({ ...form, phone: x })} />
        <Field label="Address" v={form.address} on={(x) => setForm({ ...form, address: x })} />
        <Field label="Emergency Name" v={form.emergency_contact_name} on={(x) => setForm({ ...form, emergency_contact_name: x })} />
        <Field label="Emergency Phone" v={form.emergency_contact_phone} on={(x) => setForm({ ...form, emergency_contact_phone: x })} />
        <Field label="Allergies" v={form.allergies} on={(x) => setForm({ ...form, allergies: x })} span />
        <Field label="Medical History" v={form.medical_history} on={(x) => setForm({ ...form, medical_history: x })} span />
        <Field label="Notes" v={form.notes} on={(x) => setForm({ ...form, notes: x })} span />
        <div className="col-span-2 flex justify-end gap-2 pt-1">
          <button type="button" className="btn-ghost" onClick={onClose}>Cancel</button>
          <button className="btn-primary" disabled={save.isPending}>Save</button>
        </div>
      </form>
    </Modal>
  );
}

function Field({ label, v, on, span }: { label: string; v: string; on: (x: string) => void; span?: boolean }) {
  return (
    <div className={span ? "col-span-2" : ""}>
      <label className="label">{label}</label>
      <input className="input" value={v} onChange={(e) => on(e.target.value)} />
    </div>
  );
}
