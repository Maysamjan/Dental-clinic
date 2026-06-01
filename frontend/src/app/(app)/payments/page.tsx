"use client";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import { useT } from "@/i18n/useT";

export default function PaymentsPage() {
  const t = useT();
  return (
    <div>
      <PageHeader title={t("payments")} />
      <ResourceTable
        resource="payments"
        columns={[
          { key: "invoice_number", label: "Invoice" },
          { key: "patient_name", label: "Patient" },
          { key: "amount", label: "Amount", render: (r) => Number(r.amount).toLocaleString() },
          { key: "method", label: "Method" },
          { key: "paid_at", label: "Date", render: (r) => new Date(r.paid_at).toLocaleString() },
        ]}
      />
    </div>
  );
}
