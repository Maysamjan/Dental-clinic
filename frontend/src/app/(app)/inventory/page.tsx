"use client";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import { useT } from "@/i18n/useT";

export default function InventoryPage() {
  const t = useT();
  return (
    <div>
      <PageHeader title={t("inventory")} subtitle="اقلام انبار و هشدار کمبود موجودی" />
      <ResourceTable
        resource="inventory-items"
        columns={[
          { key: "name", label: "قلم" },
          { key: "category", label: "دسته‌بندی" },
          { key: "quantity", label: "تعداد" },
          { key: "unit", label: "واحد" },
          { key: "minimum_stock", label: "حداقل" },
          {
            key: "is_low_stock",
            label: "وضعیت",
            render: (r) =>
              r.is_low_stock ? (
                <span className="badge bg-red-100 text-red-700">کمبود موجودی</span>
              ) : (
                <span className="badge bg-green-100 text-green-700">مناسب</span>
              ),
          },
        ]}
      />
    </div>
  );
}
