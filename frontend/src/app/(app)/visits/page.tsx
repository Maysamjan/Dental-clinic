"use client";
import Link from "next/link";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import { useT } from "@/i18n/useT";

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
            label: "Patient",
            render: (r) => (
              <Link className="text-brand-600 hover:underline" href={`/visits/${r.id}`}>
                {r.patient_name}
              </Link>
            ),
          },
          { key: "doctor_name", label: "Doctor" },
          { key: "visit_date", label: "Date" },
          { key: "diagnosis", label: "Diagnosis" },
          { key: "workflow_status", label: "Status" },
          {
            key: "open",
            label: "",
            render: (r) => (
              <Link className="text-brand-600 hover:underline" href={`/visits/${r.id}`}>
                Open →
              </Link>
            ),
          },
        ]}
      />
    </div>
  );
}
