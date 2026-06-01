"use client";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import { useT } from "@/i18n/useT";

export default function InventoryPage() {
  const t = useT();
  return (
    <div>
      <PageHeader title={t("inventory")} subtitle="Stock items & low-stock alerts" />
      <ResourceTable
        resource="inventory-items"
        columns={[
          { key: "name", label: "Item" },
          { key: "category", label: "Category" },
          { key: "quantity", label: "Qty" },
          { key: "unit", label: "Unit" },
          { key: "minimum_stock", label: "Min" },
          {
            key: "is_low_stock",
            label: "Status",
            render: (r) =>
              r.is_low_stock ? (
                <span className="badge bg-red-100 text-red-700">Low stock</span>
              ) : (
                <span className="badge bg-green-100 text-green-700">OK</span>
              ),
          },
        ]}
      />
    </div>
  );
}
