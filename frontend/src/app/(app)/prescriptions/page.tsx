"use client";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import { API_URL } from "@/lib/api";
import { useT } from "@/i18n/useT";

export default function PrescriptionsPage() {
  const t = useT();
  return (
    <div>
      <PageHeader title={t("prescriptions")} />
      <ResourceTable
        resource="prescriptions"
        columns={[
          { key: "id", label: "#" },
          { key: "patient_name", label: "Patient" },
          { key: "doctor_name", label: "Doctor" },
          { key: "created_at", label: "Date", render: (r) => new Date(r.created_at).toLocaleDateString() },
          {
            key: "pdf",
            label: "",
            render: (r) => (
              <a
                className="text-brand-600 hover:underline"
                href={`${API_URL}/prescriptions/${r.id}/pdf/`}
                target="_blank"
                rel="noreferrer"
              >
                PDF ↗
              </a>
            ),
          },
        ]}
      />
    </div>
  );
}
