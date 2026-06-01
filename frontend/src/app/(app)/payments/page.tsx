"use client";
import Link from "next/link";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import { API_URL } from "@/lib/api";
import { useT } from "@/i18n/useT";
import { PAYMENT_METHOD_FA } from "@/lib/labels";

export default function PaymentsPage() {
  const t = useT();
  return (
    <div>
      <PageHeader title={t("payments")} />
      <ResourceTable
        resource="payments"
        columns={[
          { key: "invoice_number", label: "صورتحساب", render: (r) => <Link className="text-brand-600 hover:underline" href={`/billing/${r.invoice}`}>{r.invoice_number}</Link> },
          { key: "patient_name", label: "بیمار" },
          { key: "amount", label: "مبلغ", render: (r) => Number(r.amount).toLocaleString() },
          { key: "method", label: "روش", render: (r) => PAYMENT_METHOD_FA[r.method] ?? r.method },
          { key: "paid_at", label: "تاریخ", render: (r) => new Date(r.paid_at).toLocaleString() },
          { key: "receipt", label: "", render: (r) => <a className="text-brand-600 hover:underline" href={`${API_URL}/payments/${r.id}/receipt/`} target="_blank" rel="noreferrer">رسید ↗</a> },
        ]}
      />
    </div>
  );
}
