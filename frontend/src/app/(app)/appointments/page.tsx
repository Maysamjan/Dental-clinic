"use client";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import { useT } from "@/i18n/useT";

const STATUS: Record<string, string> = {
  SCHEDULED: "bg-slate-100 text-slate-700",
  CONFIRMED: "bg-blue-100 text-blue-700",
  ARRIVED: "bg-amber-100 text-amber-700",
  COMPLETED: "bg-green-100 text-green-700",
  CANCELLED: "bg-red-100 text-red-700",
  NO_SHOW: "bg-red-100 text-red-700",
};

export default function AppointmentsPage() {
  const t = useT();
  return (
    <div>
      <PageHeader title={t("appointments")} subtitle="Daily / weekly / monthly schedule" />
      <ResourceTable
        resource="appointments"
        columns={[
          { key: "patient_name", label: "Patient" },
          { key: "doctor_name", label: "Doctor" },
          { key: "start", label: "When", render: (r) => new Date(r.start).toLocaleString() },
          { key: "reason", label: "Reason" },
          {
            key: "status",
            label: "Status",
            render: (r) => (
              <span className={`badge ${STATUS[r.status] ?? ""}`}>{r.status}</span>
            ),
          },
        ]}
      />
    </div>
  );
}
