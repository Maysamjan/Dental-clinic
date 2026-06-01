"use client";
import Link from "next/link";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import { useT } from "@/i18n/useT";
import { WORKFLOW_FA } from "@/lib/labels";

export default function VisitsPage() {
  const t = useT();
  return (
    <div>
      <PageHeader title={t("visits")} />
      <ResourceTable
        resource="visits"
        columns={[
          { key: "id", label: "#" },
          {
            key: "patient_name",
            label: "بیمار",
            render: (r) => (
              <Link className="text-brand-600 hover:underline" href={`/visits/${r.id}`}>
                {r.patient_name}
              </Link>
            ),
          },
          { key: "doctor_name", label: "داکتر" },
          { key: "visit_date", label: "تاریخ" },
          { key: "diagnosis", label: "تشخیص" },
          { key: "workflow_status", label: "وضعیت", render: (r) => WORKFLOW_FA[r.workflow_status] ?? r.workflow_status },
          {
            key: "open",
            label: "",
            render: (r) => (
              <Link className="text-brand-600 hover:underline" href={`/visits/${r.id}`}>
                باز کردن →
              </Link>
            ),
          },
        ]}
      />
    </div>
  );
}
