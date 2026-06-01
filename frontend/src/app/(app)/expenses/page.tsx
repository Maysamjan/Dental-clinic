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
          { key: "date", label: "تاریخ" },
          { key: "category_name", label: "دسته‌بندی" },
          { key: "description", label: "شرح" },
          { key: "amount", label: "مبلغ", render: (r) => Number(r.amount).toLocaleString() },
        ]}
      />
    </div>
  );
}
