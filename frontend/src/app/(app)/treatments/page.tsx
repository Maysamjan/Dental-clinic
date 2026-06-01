"use client";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import { useT } from "@/i18n/useT";

export default function TreatmentsPage() {
  const t = useT();
  return (
    <div>
      <PageHeader title={t("treatments")} subtitle="Treatment plans & progress" />
      <ResourceTable
        resource="treatment-plans"
        columns={[
          { key: "title", label: "Plan" },
          { key: "patient_name", label: "Patient" },
          { key: "doctor_name", label: "Doctor" },
          { key: "status", label: "Status" },
          {
            key: "progress_percent",
            label: "Progress",
            render: (r) => (
              <div className="flex items-center gap-2">
                <div className="h-2 w-24 rounded-full bg-slate-200">
                  <div
                    className="h-2 rounded-full bg-brand-500"
                    style={{ width: `${r.progress_percent}%` }}
                  />
                </div>
                <span className="text-xs">{r.progress_percent}%</span>
              </div>
            ),
          },
        ]}
      />
    </div>
  );
}
