"use client";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import { useT } from "@/i18n/useT";

export default function InstallmentsPage() {
  const t = useT();
  return (
    <div>
      <PageHeader title={t("installments")} />
      <ResourceTable
        resource="installments"
        searchable={false}
        columns={[
          { key: "id", label: "#" },
          { key: "due_date", label: "Due Date" },
          { key: "amount", label: "Amount", render: (r) => Number(r.amount).toLocaleString() },
          { key: "paid_amount", label: "Paid", render: (r) => Number(r.paid_amount).toLocaleString() },
          { key: "status", label: "Status" },
        ]}
      />
    </div>
  );
}
