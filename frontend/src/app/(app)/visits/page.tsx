"use client";
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
          { key: "patient_name", label: "Patient" },
          { key: "doctor_name", label: "Doctor" },
          { key: "visit_date", label: "Date" },
          { key: "diagnosis", label: "Diagnosis" },
          { key: "workflow_status", label: "Status" },
        ]}
      />
    </div>
  );
}
