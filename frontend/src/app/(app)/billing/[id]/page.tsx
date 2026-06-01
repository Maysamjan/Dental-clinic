"use client";
import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { api, API_URL } from "@/lib/api";
import { rowsOf } from "@/lib/hooks";
import { useAuth } from "@/stores/auth";
import { hasPerm } from "@/lib/permissions";
import { INVOICE_STATUS_FA, PAYMENT_METHOD_FA } from "@/lib/labels";
import { useToast, apiError } from "@/stores/toast";
import PageHeader from "@/components/PageHeader";
import Modal from "@/components/Modal";
import InvoiceBuilder from "@/components/InvoiceBuilder";

const STATUS: Record<string, string> = {
  PAID: "bg-green-100 text-green-700",
  PARTIAL: "bg-amber-100 text-amber-700",
  UNPAID: "bg-red-100 text-red-700",
};

export default function InvoiceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const qc = useQueryClient();
  const toast = useToast((s) => s.push);
  const permissions = useAuth((s) => s.user?.permissions);
  const canEdit = hasPerm(permissions, "billing.change");
  const canPay = hasPerm(permissions, "payments.add");
  const canInstall = hasPerm(permissions, "installments.add");

  const [editing, setEditing] = useState(false);
  const [payOpen, setPayOpen] = useState(false);

  const { data: inv } = useQuery({ queryKey: ["invoice", id], queryFn: async () => (await api.get(`/invoices/${id}/`)).data });
  const { data: payData } = useQuery({ queryKey: ["payments", { invoice: id }], queryFn: async () => (await api.get(`/payments/`, { params: { invoice: id } })).data });
  const { data: planData } = useQuery({ queryKey: ["installment-plans", { invoice: id }], queryFn: async () => (await api.get(`/installment-plans/`, { params: { invoice: id } })).data });
  const payments = rowsOf<any>(payData);
  const plan = rowsOf<any>(planData)[0];

  const refresh = () => {
    qc.invalidateQueries({ queryKey: ["invoice", id] });
    qc.invalidateQueries({ queryKey: ["payments", { invoice: id }] });
    qc.invalidateQueries({ queryKey: ["installment-plans", { invoice: id }] });
  };

  const fmt = (n: any) => Number(n || 0).toLocaleString();

  if (!inv) return <div className="text-slate-400">در حال بارگذاری…</div>;
  if (editing) {
    return (
      <div>
        <PageHeader title={`ویرایش ${inv.number}`} action={<button className="btn-ghost" onClick={() => setEditing(false)}>پایان</button>} />
        <InvoiceBuilder initial={inv} />
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title={inv.number}
        subtitle={<><Link className="text-brand-600 hover:underline" href={`/patients/${inv.patient}`}>{inv.patient_name}</Link> · {inv.issue_date}</>}
        action={
          <div className="flex gap-2">
            <a className="btn-ghost" href={`${API_URL}/invoices/${inv.id}/pdf/`} target="_blank" rel="noreferrer">PDF ↗</a>
            {canEdit && inv.status !== "PAID" && <button className="btn-ghost" onClick={() => setEditing(true)}>ویرایش</button>}
            {canPay && Number(inv.balance) > 0 && <button className="btn-primary" onClick={() => setPayOpen(true)}>ثبت پرداخت</button>}
          </div>
        }
      />

      <div className="mb-4 flex items-center gap-3">
        <span className={`badge ${STATUS[inv.status]}`}>{INVOICE_STATUS_FA[inv.status] ?? inv.status}</span>
        <span className="text-sm text-slate-400">باقی‌مانده: <b className={Number(inv.balance) > 0 ? "text-amber-600" : ""}>{fmt(inv.balance)}</b></span>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <div className="card overflow-x-auto p-0">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500 dark:bg-slate-700/50">
                <tr>{["شرح", "تعداد", "قیمت واحد", "مجموع"].map((h) => <th key={h} className="px-4 py-2 text-start font-medium">{h}</th>)}</tr>
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

          <div className="card mt-4 p-0">
            <div className="border-b border-slate-200 px-4 py-2 font-semibold dark:border-slate-700">سابقه پرداخت‌ها</div>
            <table className="w-full text-sm">
              <tbody>
                {payments.length === 0 && <tr><td className="p-4 text-slate-400">هنوز پرداختی ثبت نشده است.</td></tr>}
                {payments.map((p) => (
                  <tr key={p.id} className="border-t border-slate-100 dark:border-slate-700">
                    <td className="px-4 py-2">{new Date(p.paid_at).toLocaleString()}</td>
                    <td className="px-4 py-2">{PAYMENT_METHOD_FA[p.method] ?? p.method}</td>
                    <td className="px-4 py-2">{fmt(p.amount)}</td>
                    <td className="px-4 py-2 text-end"><a className="text-brand-600 hover:underline" href={`${API_URL}/payments/${p.id}/receipt/`} target="_blank" rel="noreferrer">رسید ↗</a></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="space-y-4">
          <div className="card space-y-1 text-sm">
            <div className="flex justify-between"><span>جمع جزء</span><span>{fmt(inv.subtotal)}</span></div>
            <div className="flex justify-between"><span>تخفیف</span><span>-{fmt(inv.discount)}</span></div>
            <div className="flex justify-between"><span>مالیات</span><span>{fmt(inv.tax)}</span></div>
            <div className="flex justify-between text-lg font-bold"><span>مجموع کل</span><span>{fmt(inv.total)}</span></div>
            <div className="flex justify-between text-brand-600"><span>پرداخت‌شده</span><span>{fmt(inv.paid_amount)}</span></div>
          </div>

          <InstallmentPanel invoice={inv} plan={plan} canInstall={canInstall} canPay={canPay} refresh={refresh} toast={toast} />
        </div>
      </div>

      {payOpen && (
        <PaymentModal invoiceId={inv.id} balance={Number(inv.balance)} onClose={() => setPayOpen(false)}
          onDone={() => { setPayOpen(false); refresh(); toast("success", "پرداخت ثبت شد."); }}
          onErr={(e) => toast("error", apiError(e))} />
      )}
    </div>
  );
}

function PaymentModal({ invoiceId, balance, onClose, onDone, onErr, installmentId }: {
  invoiceId: number; balance: number; onClose: () => void; onDone: () => void; onErr: (e: any) => void; installmentId?: number;
}) {
  const [amount, setAmount] = useState(String(balance));
  const [method, setMethod] = useState("CASH");
  const [reference, setReference] = useState("");
  const pay = useMutation({
    mutationFn: () => api.post("/payments/", { invoice: invoiceId, amount, method, reference, installment: installmentId ?? null }),
    onSuccess: onDone,
    onError: onErr,
  });
  return (
    <Modal open title="ثبت پرداخت" onClose={onClose}>
      <form onSubmit={(e) => { e.preventDefault(); pay.mutate(); }} className="space-y-3">
        <div><label className="label">مبلغ</label><input className="input" value={amount} onChange={(e) => setAmount(e.target.value)} /></div>
        <div>
          <label className="label">روش پرداخت</label>
          <select className="input" value={method} onChange={(e) => setMethod(e.target.value)}>
            <option value="CASH">نقد</option>
            <option value="BANK_TRANSFER">انتقال بانکی</option>
          </select>
        </div>
        <div><label className="label">Reference (optional)</label><input className="input" value={reference} onChange={(e) => setReference(e.target.value)} /></div>
        <div className="flex justify-end gap-2 pt-1">
          <button type="button" className="btn-ghost" onClick={onClose}>انصراف</button>
          <button className="btn-primary" disabled={pay.isPending}>ذخیره</button>
        </div>
      </form>
    </Modal>
  );
}

function InstallmentPanel({ invoice, plan, canInstall, canPay, refresh, toast }: any) {
  const [count, setCount] = useState(3);
  const [payFor, setPayFor] = useState<any | null>(null);
  const createPlan = useMutation({
    mutationFn: () => api.post("/installment-plans/", { invoice: invoice.id, total_amount: invoice.balance, number_of_installments: count }),
    onSuccess: () => { refresh(); toast("success", "پلان اقساط ایجاد شد."); },
    onError: (e: any) => toast("error", apiError(e)),
  });

  if (!plan) {
    if (!canInstall || Number(invoice.balance) <= 0) return null;
    return (
      <div className="card">
        <h3 className="mb-2 font-semibold">پلان اقساط</h3>
        <div className="flex items-end gap-2">
          <div><label className="label">تعداد اقساط</label><input type="number" min={2} className="input w-20" value={count} onChange={(e) => setCount(Number(e.target.value))} /></div>
          <button className="btn-ghost" disabled={createPlan.isPending} onClick={() => createPlan.mutate()}>ایجاد</button>
        </div>
      </div>
    );
  }

  return (
    <div className="card p-0">
      <div className="border-b border-slate-200 px-4 py-2 font-semibold dark:border-slate-700">اقساط</div>
      <table className="w-full text-sm">
        <tbody>
          {plan.installments.map((ins: any) => (
            <tr key={ins.id} className="border-t border-slate-100 dark:border-slate-700">
              <td className="px-4 py-2">{ins.due_date}</td>
              <td className="px-4 py-2">{Number(ins.amount).toLocaleString()}</td>
              <td className="px-4 py-2"><span className="badge bg-slate-100 text-slate-700">{ins.status}</span></td>
              <td className="px-4 py-2 text-end">
                {canPay && ins.status !== "PAID" && (
                  <button className="btn-ghost px-2 py-1 text-xs" onClick={() => setPayFor(ins)}>پرداخت</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {payFor && (
        <PaymentModal invoiceId={invoice.id} balance={Number(payFor.amount) - Number(payFor.paid_amount)} installmentId={payFor.id}
          onClose={() => setPayFor(null)}
          onDone={() => { setPayFor(null); refresh(); toast("success", "قسط پرداخت شد."); }}
          onErr={(e: any) => toast("error", apiError(e))} />
      )}
    </div>
  );
}
