"use client";
import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useList, rowsOf } from "@/lib/hooks";
import { useT } from "@/i18n/useT";
import PageHeader from "@/components/PageHeader";

const STATUSES = [
  ["HEALTHY", "Healthy", "bg-white text-slate-700 border-slate-300"],
  ["CARIES", "Caries", "bg-red-500 text-white"],
  ["FILLING", "Filling", "bg-blue-500 text-white"],
  ["ROOT_CANAL", "Root Canal", "bg-purple-500 text-white"],
  ["CROWN", "Crown", "bg-amber-500 text-white"],
  ["BRIDGE", "Bridge", "bg-pink-500 text-white"],
  ["IMPLANT", "Implant", "bg-teal-600 text-white"],
  ["EXTRACTION", "Extraction", "bg-slate-800 text-white"],
  ["ORTHODONTIC", "Orthodontic", "bg-emerald-500 text-white"],
] as const;

const colorOf = (status: string) =>
  STATUSES.find((s) => s[0] === status)?.[2] ??
  "bg-white text-slate-700 border-slate-300";

function ChartInner() {
  const t = useT();
  const qc = useQueryClient();
  const sp = useSearchParams();
  const [patientId, setPatientId] = useState<string>(sp.get("patient") ?? "");
  const [active, setActive] = useState<string>("CARIES");

  const { data: patientsData } = useList("patients");
  const patients = rowsOf<any>(patientsData);

  useEffect(() => {
    if (!patientId && patients.length) setPatientId(String(patients[0].id));
  }, [patients, patientId]);

  const { data: chart } = useQuery({
    queryKey: ["chart", patientId],
    enabled: !!patientId,
    queryFn: async () =>
      (await api.get(`/dental-charts/by-patient/${patientId}/`)).data,
  });

  const updateTooth = useMutation({
    mutationFn: ({ toothId, status }: { toothId: number; status: string }) =>
      api.patch(`/teeth/${toothId}/`, { status }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["chart", patientId] }),
  });

  const teeth: any[] = chart?.teeth ?? [];
  const upper = teeth.filter((x) => [1, 2, 5, 6].includes(Math.floor(x.fdi_number / 10)));
  const lower = teeth.filter((x) => [3, 4, 7, 8].includes(Math.floor(x.fdi_number / 10)));

  const Tooth = (tooth: any) => (
    <button
      key={tooth.id}
      title={`${tooth.fdi_number} · ${tooth.name} · ${tooth.status}`}
      onClick={() => updateTooth.mutate({ toothId: tooth.id, status: active })}
      className={`flex h-12 w-10 flex-col items-center justify-center rounded-md border text-[10px] font-semibold ${colorOf(
        tooth.status
      )}`}
    >
      <span>{tooth.fdi_number}</span>
    </button>
  );

  return (
    <div>
      <PageHeader title={t("dental_chart")} subtitle="FDI numbering · click a tooth to apply the selected condition" />

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <select className="input w-auto" value={patientId} onChange={(e) => setPatientId(e.target.value)}>
          {patients.map((p) => (
            <option key={p.id} value={p.id}>
              {p.code} — {p.full_name}
            </option>
          ))}
        </select>
        <span className="text-sm text-slate-400">
          Dentition: {chart?.dentition === "CHILD" ? "Child (20)" : "Adult (32)"}
        </span>
      </div>

      {/* Condition palette */}
      <div className="mb-5 flex flex-wrap gap-2">
        {STATUSES.map(([code, label, cls]) => (
          <button
            key={code}
            onClick={() => setActive(code)}
            className={`badge border px-3 py-1 ${cls} ${
              active === code ? "ring-2 ring-offset-1 ring-brand-500" : ""
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="card space-y-4">
        <div>
          <div className="mb-2 text-xs uppercase text-slate-400">Upper</div>
          <div className="flex flex-wrap gap-1">{upper.map(Tooth)}</div>
        </div>
        <hr className="border-slate-200 dark:border-slate-700" />
        <div>
          <div className="mb-2 text-xs uppercase text-slate-400">Lower</div>
          <div className="flex flex-wrap gap-1">{lower.map(Tooth)}</div>
        </div>
      </div>
    </div>
  );
}

export default function DentalChartPage() {
  return (
    <Suspense fallback={null}>
      <ChartInner />
    </Suspense>
  );
}
