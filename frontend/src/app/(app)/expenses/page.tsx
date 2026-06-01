"use client";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import { useT } from "@/i18n/useT";

export default function ExpensesPage() {
  const t = useT();
  return (
    <div>
      <PageHeader title={t("expenses")} />
      <ResourceTable
        resource="expenses"
        columns={[
          { key: "date", label: "Date" },
          { key: "category_name", label: "Category" },
          { key: "description", label: "Description" },
          { key: "amount", label: "Amount", render: (r) => Number(r.amount).toLocaleString() },
        ]}
      />
    </div>
  );
}
