"use client";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { rowsOf } from "@/lib/hooks";
import { useToast, apiError } from "@/stores/toast";
import { GENDER_FA } from "@/lib/labels";
import PageHeader from "@/components/PageHeader";

const STATUS_FLOW = ["WAITING", "IN_CONSULTATION", "TREATMENT_IN_PROGRESS", "COMPLETED"];
const STATUS_LABEL: Record<string, string> = {
  WAITING: "در انتظار",
  IN_CONSULTATION: "در حال معاینه",
  TREATMENT_IN_PROGRESS: "در حال تداوی",
  COMPLETED: "تکمیل‌شده",
};

export default function ConsultationPage() {
  const { id } = useParams<{ id: string }>();
  const qc = useQueryClient();
  const toast = useToast((s) => s.push);

  const { data: visit } = useQuery({
    queryKey: ["visit", id],
    queryFn: async () => (await api.get(`/visits/${id}/`)).data,
  });
  const patientId = visit?.patient;

  const { data: patient } = useQuery({
    queryKey: ["patient", patientId],
    enabled: !!patientId,
    queryFn: async () => (await api.get(`/patients/${patientId}/`)).data,
  });
  const { data: rxData } = useQuery({
    queryKey: ["prescriptions", { patient: patientId }],
    enabled: !!patientId,
    queryFn: async () => (await api.get(`/prescriptions/`, { params: { patient: patientId } })).data,
  });
  const { data: planData } = useQuery({
    queryKey: ["treatment-plans", { patient: patientId }],
    enabled: !!patientId,
    queryFn: async () => (await api.get(`/treatment-plans/`, { params: { patient: patientId } })).data,
  });

  const [form, setForm] = useState({ chief_complaint: "", clinical_findings: "", diagnosis: "", notes: "" });
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    if (visit) {
      setForm({
        chief_complaint: visit.chief_complaint || "",
        clinical_findings: visit.clinical_findings || "",
        diagnosis: visit.diagnosis || "",
        notes: visit.notes || "",
      });
      setDirty(false);
    }
  }, [visit?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  const save = useMutation({
    mutationFn: () => api.patch(`/visits/${id}/`, form),
    onSuccess: () => { toast("success", "معاینه ذخیره شد."); setDirty(false); qc.invalidateQueries({ queryKey: ["visit", id] }); },
    onError: (e) => toast("error", apiError(e)),
  });
  const advance = useMutation({
    mutationFn: (status: string) => api.post(`/visits/${id}/advance/`, { status }),
    onSuccess: () => { toast("success", "وضعیت بروزرسانی شد."); qc.invalidateQueries({ queryKey: ["visit", id] }); },
    onError: (e) => toast("error", apiError(e)),
  });

  if (!visit) return <div className="text-slate-400">در حال بارگذاری…</div>;

  const idx = STATUS_FLOW.indexOf(visit.workflow_status);
  const next = idx >= 0 && idx < STATUS_FLOW.length - 1 ? STATUS_FLOW[idx + 1] : null;

  const field = (key: keyof typeof form, label: string, rows = 3) => (
    <div>
      <label className="label">{label}</label>
      <textarea
        className="input"
        rows={rows}
        value={form[key]}
        onChange={(e) => { setForm({ ...form, [key]: e.target.value }); setDirty(true); }}
      />
    </div>
  );

  return (
    <div>
      <PageHeader
        title={`معاینه — ${visit.patient_name}`}
        subtitle={`ویزیت #${visit.id} · ${visit.visit_date} · نوبت #${visit.queue_number ?? "—"}`}
        action={
          <span className="badge bg-brand-50 text-brand-700">{STATUS_LABEL[visit.workflow_status]}</span>
        }
      />

      {patient?.allergies && (
        <div className="mb-4 rounded-lg border border-red-300 bg-red-50 px-4 py-2 font-medium text-red-700">
          ⚠ حساسیت‌ها: {patient.allergies}
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        {/* یادداشت‌های کلینیکی */}
        <div className="card space-y-3 lg:col-span-2">
          <h2 className="font-semibold">سابقه کلینیکی</h2>
          {field("chief_complaint", "شکایت اصلی", 2)}
          {field("clinical_findings", "یافته‌های کلینیکی")}
          {field("diagnosis", "تشخیص", 2)}
          {field("notes", "یادداشت‌ها", 2)}
          <div className="flex items-center justify-between">
            <button className="btn-primary" disabled={save.isPending || !dirty} onClick={() => save.mutate()}>
              {dirty ? "ذخیره معاینه" : "ذخیره شد"}
            </button>
            {next && (
              <button className="btn-ghost" disabled={advance.isPending} onClick={() => advance.mutate(next)}>
                مرحله بعد → {STATUS_LABEL[next]}
              </button>
            )}
          </div>
        </div>

        {/* پنل کناری: اطلاعات بیمار و میان‌برها */}
        <div className="space-y-4">
          <div className="card">
            <h2 className="mb-2 font-semibold">بیمار</h2>
            <div className="text-sm">
              <div>{patient?.code} · {patient?.gender ? (GENDER_FA[patient.gender] ?? patient.gender) : ""} · {patient?.age ?? "?"} سال</div>
              <div className="text-slate-400">{patient?.phone}</div>
              {patient?.medical_history && (
                <div className="mt-2 text-xs text-slate-500">سوابق: {patient.medical_history}</div>
              )}
            </div>
            <div className="mt-3 flex flex-col gap-2">
              <Link href={`/dental-chart?patient=${patientId}`} className="btn-ghost justify-start">🦷 نمودار دندان</Link>
              <Link href={`/patients/${patientId}`} className="btn-ghost justify-start">👤 پروفایل کامل</Link>
            </div>
          </div>

          <div className="card">
            <h2 className="mb-2 font-semibold">پلان‌های تداوی</h2>
            {rowsOf<any>(planData).length === 0 ? (
              <p className="text-sm text-slate-400">هنوز موردی نیست.</p>
            ) : (
              <ul className="text-sm">
                {rowsOf<any>(planData).map((p) => (
                  <li key={p.id} className="flex justify-between py-1">
                    <span>{p.title}</span>
                    <span className="text-slate-400">{p.progress_percent}%</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="card">
            <h2 className="mb-2 font-semibold">نسخه‌ها</h2>
            {rowsOf<any>(rxData).length === 0 ? (
              <p className="text-sm text-slate-400">هنوز موردی نیست.</p>
            ) : (
              <ul className="text-sm">
                {rowsOf<any>(rxData).map((r) => (
                  <li key={r.id} className="py-1">#{r.id} · {new Date(r.created_at).toLocaleDateString('en-US')}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
