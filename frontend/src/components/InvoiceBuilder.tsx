"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useToast, apiError } from "@/stores/toast";
import ResourceCombo from "@/components/ResourceCombo";

interface Item { description: string; quantity: number; unit_price: string; }

export default function InvoiceBuilder({ initial }: { initial?: any }) {
  const router = useRouter();
  const qc = useQueryClient();
  const toast = useToast((s) => s.push);
  const editing = !!initial?.id;

  const [patient, setPatient] = useState<number | null>(initial?.patient ?? null);
  const [discount, setDiscount] = useState<string>(initial?.discount ?? "0");
  const [tax, setTax] = useState<string>(initial?.tax ?? "0");
  const [notes, setNotes] = useState<string>(initial?.notes ?? "");
  const [items, setItems] = useState<Item[]>(
    initial?.items?.map((i: any) => ({ description: i.description, quantity: i.quantity, unit_price: String(i.unit_price) })) ?? [
      { description: "", quantity: 1, unit_price: "0" },
    ]
  );

  const num = (s: string) => (isNaN(parseFloat(s)) ? 0 : parseFloat(s));
  const subtotal = items.reduce((s, i) => s + i.quantity * num(i.unit_price), 0);
  const total = subtotal - num(discount) + num(tax);

  const setItem = (idx: number, patch: Partial<Item>) =>
    setItems(items.map((it, i) => (i === idx ? { ...it, ...patch } : it)));

  const save = useMutation({
    mutationFn: () => {
      const payload = {
        patient,
        discount,
        tax,
        notes,
        items: items
          .filter((i) => i.description.trim())
          .map((i) => ({ description: i.description, quantity: i.quantity, unit_price: i.unit_price })),
      };
      return editing
        ? api.patch(`/invoices/${initial.id}/`, payload)
        : api.post("/invoices/", payload);
    },
    onSuccess: (res) => {
      toast("success", editing ? "Invoice updated." : `Invoice ${res.data.number} created.`);
      qc.invalidateQueries({ queryKey: ["invoices"] });
      router.push(`/billing/${res.data.id}`);
    },
    onError: (e) => toast("error", apiError(e)),
  });

  const valid = patient && items.some((i) => i.description.trim());

  return (
    <div className="space-y-4">
      <div className="card max-w-md">
        <label className="label">Patient</label>
        <ResourceCombo resource="patients" value={patient} onChange={setPatient}
          getLabel={(r) => `${r.code} — ${r.full_name}`} placeholder="Search patient…" />
      </div>

      <div className="card overflow-x-auto p-0">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-xs uppercase text-slate-500 dark:bg-slate-700/50">
            <tr>{["Description", "Qty", "Unit Price", "Line Total", ""].map((h) => <th key={h} className="px-3 py-2 text-start font-medium">{h}</th>)}</tr>
          </thead>
          <tbody>
            {items.map((it, idx) => (
              <tr key={idx} className="border-t border-slate-100 dark:border-slate-700">
                <td className="px-3 py-2"><input className="input" value={it.description} onChange={(e) => setItem(idx, { description: e.target.value })} placeholder="Treatment / item" /></td>
                <td className="px-3 py-2 w-20"><input type="number" min={1} className="input" value={it.quantity} onChange={(e) => setItem(idx, { quantity: Number(e.target.value) })} /></td>
                <td className="px-3 py-2 w-32"><input className="input" value={it.unit_price} onChange={(e) => setItem(idx, { unit_price: e.target.value })} /></td>
                <td className="px-3 py-2 w-28">{(it.quantity * num(it.unit_price)).toLocaleString()}</td>
                <td className="px-3 py-2"><button type="button" className="text-red-500" onClick={() => setItems(items.filter((_, i) => i !== idx))}>✕</button></td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="p-3">
          <button type="button" className="btn-ghost" onClick={() => setItems([...items, { description: "", quantity: 1, unit_price: "0" }])}>+ Add line</button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="card space-y-2">
          <div><label className="label">Notes</label><input className="input" value={notes} onChange={(e) => setNotes(e.target.value)} /></div>
        </div>
        <div className="card space-y-2">
          <Row label="Subtotal" value={subtotal.toLocaleString()} />
          <div className="flex items-center justify-between"><span>Discount</span><input className="input w-32 py-1 text-end" value={discount} onChange={(e) => setDiscount(e.target.value)} /></div>
          <div className="flex items-center justify-between"><span>Tax</span><input className="input w-32 py-1 text-end" value={tax} onChange={(e) => setTax(e.target.value)} /></div>
          <hr className="border-slate-200 dark:border-slate-700" />
          <Row label="Total" value={total.toLocaleString()} bold />
        </div>
      </div>

      <div className="flex justify-end gap-2">
        <button className="btn-ghost" onClick={() => router.back()}>Cancel</button>
        <button className="btn-primary" disabled={!valid || save.isPending} onClick={() => save.mutate()}>
          {editing ? "Save Changes" : "Create Invoice"}
        </button>
      </div>
    </div>
  );
}

function Row({ label, value, bold }: { label: string; value: string; bold?: boolean }) {
  return (
    <div className={`flex justify-between ${bold ? "text-lg font-bold" : ""}`}>
      <span>{label}</span><span>{value}</span>
    </div>
  );
}
