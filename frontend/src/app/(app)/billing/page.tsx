"use client";
import Link from "next/link";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import { API_URL } from "@/lib/api";
import { useT } from "@/i18n/useT";
import { useAuth } from "@/stores/auth";
import { hasPerm } from "@/lib/permissions";
import { INVOICE_STATUS_FA } from "@/lib/labels";

const STATUS: Record<string, string> = {
  PAID: "bg-green-100 text-green-700",
  PARTIAL: "bg-amber-100 text-amber-700",
  UNPAID: "bg-red-100 text-red-700",
};

export default function BillingPage() {
  const t = useT();
  const permissions = useAuth((s) => s.user?.permissions);
  const canAdd = hasPerm(permissions, "billing.add");

  return (
    <div>
      <PageHeader
        title={t("billing")}
        subtitle="صورتحساب‌ها"
        action={canAdd ? <Link href="/billing/new" className="btn-primary">+ صورتحساب جدید</Link> : null}
      />
      <ResourceTable
        resource="invoices"
        columns={[
          { key: "number", label: "صورتحساب", render: (r) => <Link className="text-brand-600 hover:underline" href={`/billing/${r.id}`}>{r.number}</Link> },
          { key: "patient_name", label: "بیمار" },
          { key: "total", label: "مجموع", render: (r) => Number(r.total).toLocaleString() },
          { key: "paid_amount", label: "پرداختی", render: (r) => Number(r.paid_amount).toLocaleString() },
          { key: "balance", label: "باقی‌مانده", render: (r) => Number(r.balance).toLocaleString() },
          { key: "status", label: "وضعیت", render: (r) => <span className={`badge ${STATUS[r.status]}`}>{INVOICE_STATUS_FA[r.status] ?? r.status}</span> },
          { key: "pdf", label: "", render: (r) => <a className="text-brand-600 hover:underline" href={`${API_URL}/invoices/${r.id}/pdf/`} target="_blank" rel="noreferrer">PDF ↗</a> },
        ]}
      />
    </div>
  );
}
