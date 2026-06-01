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
          { key: "due_date", label: "تاریخ سررسید" },
          { key: "amount", label: "مبلغ", render: (r) => Number(r.amount).toLocaleString('en-US') },
          { key: "paid_amount", label: "پرداختی", render: (r) => Number(r.paid_amount).toLocaleString('en-US') },
          { key: "status", label: "وضعیت" },
        ]}
      />
    </div>
  );
}
