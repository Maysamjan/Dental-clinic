"use client";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import { API_URL } from "@/lib/api";
import { useT } from "@/i18n/useT";

const STATUS: Record<string, string> = {
  PAID: "bg-green-100 text-green-700",
  PARTIAL: "bg-amber-100 text-amber-700",
  UNPAID: "bg-red-100 text-red-700",
};

export default function BillingPage() {
  const t = useT();
  return (
    <div>
      <PageHeader title={t("billing")} subtitle="Invoices" />
      <ResourceTable
        resource="invoices"
        columns={[
          { key: "number", label: "Invoice" },
          { key: "patient_name", label: "Patient" },
          { key: "total", label: "Total", render: (r) => Number(r.total).toLocaleString() },
          { key: "paid_amount", label: "Paid", render: (r) => Number(r.paid_amount).toLocaleString() },
          { key: "balance", label: "Balance", render: (r) => Number(r.balance).toLocaleString() },
          {
            key: "status",
            label: "Status",
            render: (r) => <span className={`badge ${STATUS[r.status]}`}>{r.status}</span>,
          },
          {
            key: "pdf",
            label: "",
            render: (r) => (
              <a className="text-brand-600 hover:underline" href={`${API_URL}/invoices/${r.id}/pdf/`} target="_blank" rel="noreferrer">
                PDF ↗
              </a>
            ),
          },
        ]}
      />
    </div>
  );
}
