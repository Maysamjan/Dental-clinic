"use client";
import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api, API_URL } from "@/lib/api";
import { useAuth } from "@/stores/auth";
import { hasPerm } from "@/lib/permissions";
import PageHeader from "@/components/PageHeader";
import InvoiceBuilder from "@/components/InvoiceBuilder";

const STATUS: Record<string, string> = {
  PAID: "bg-green-100 text-green-700",
  PARTIAL: "bg-amber-100 text-amber-700",
  UNPAID: "bg-red-100 text-red-700",
};

export default function InvoiceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [editing, setEditing] = useState(false);
  const permissions = useAuth((s) => s.user?.permissions);
  const canEdit = hasPerm(permissions, "billing.change");

  const { data: inv } = useQuery({
    queryKey: ["invoice", id],
    queryFn: async () => (await api.get(`/invoices/${id}/`)).data,
  });

  if (!inv) return <div className="text-slate-400">Loading invoice…</div>;

  if (editing) {
    return (
      <div>
        <PageHeader title={`Edit ${inv.number}`} action={<button className="btn-ghost" onClick={() => setEditing(false)}>Done</button>} />
        <InvoiceBuilder initial={inv} />
      </div>
    );
  }

  const fmt = (n: any) => Number(n || 0).toLocaleString();

  return (
    <div>
      <PageHeader
        title={inv.number}
        subtitle={<><Link className="text-brand-600 hover:underline" href={`/patients/${inv.patient}`}>{inv.patient_name}</Link> · {inv.issue_date}</>}
        action={
          <div className="flex gap-2">
            <a className="btn-ghost" href={`${API_URL}/invoices/${inv.id}/pdf/`} target="_blank" rel="noreferrer">PDF ↗</a>
            {canEdit && inv.status !== "PAID" && <button className="btn-primary" onClick={() => setEditing(true)}>Edit</button>}
          </div>
        }
      />

      <div className="mb-4 flex items-center gap-3">
        <span className={`badge ${STATUS[inv.status]}`}>{inv.status}</span>
        <span className="text-sm text-slate-400">Balance: <b className={Number(inv.balance) > 0 ? "text-amber-600" : ""}>{fmt(inv.balance)}</b></span>
      </div>

      <div className="card overflow-x-auto p-0">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-xs uppercase text-slate-500 dark:bg-slate-700/50">
            <tr>{["Description", "Qty", "Unit Price", "Total"].map((h) => <th key={h} className="px-4 py-2 text-start font-medium">{h}</th>)}</tr>
          </thead>
          <tbody>
            {inv.items.map((it: any) => (
              <tr key={it.id} className="border-t border-slate-100 dark:border-slate-700">
                <td className="px-4 py-2">{it.description}</td>
                <td className="px-4 py-2">{it.quantity}</td>
                <td className="px-4 py-2">{fmt(it.unit_price)}</td>
                <td className="px-4 py-2">{fmt(it.line_total)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 ms-auto max-w-xs space-y-1 text-sm">
        <div className="flex justify-between"><span>Subtotal</span><span>{fmt(inv.subtotal)}</span></div>
        <div className="flex justify-between"><span>Discount</span><span>-{fmt(inv.discount)}</span></div>
        <div className="flex justify-between"><span>Tax</span><span>{fmt(inv.tax)}</span></div>
        <div className="flex justify-between text-lg font-bold"><span>Total</span><span>{fmt(inv.total)}</span></div>
        <div className="flex justify-between text-brand-600"><span>Paid</span><span>{fmt(inv.paid_amount)}</span></div>
      </div>
    </div>
  );
}
