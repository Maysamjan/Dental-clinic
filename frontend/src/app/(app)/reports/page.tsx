"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, API_URL } from "@/lib/api";
import { useT } from "@/i18n/useT";
import PageHeader from "@/components/PageHeader";

const REPORTS = [
  ["revenue", "Revenue"],
  ["payments", "Payments"],
  ["outstanding", "Outstanding Balances"],
  ["expenses", "Expenses"],
  ["profit-loss", "Profit & Loss"],
  ["doctor-performance", "Doctor Performance"],
  ["treatments", "Treatments"],
  ["current-stock", "Current Stock"],
  ["low-stock", "Low Stock"],
  ["inventory-movement", "Inventory Movement"],
];

export default function ReportsPage() {
  const t = useT();
  const [report, setReport] = useState("revenue");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");

  const params = { ...(from ? { from } : {}), ...(to ? { to } : {}) };
  const { data } = useQuery({
    queryKey: ["report", report, params],
    queryFn: async () =>
      (await api.get(`/reports/${report}/`, { params })).data,
  });

  const exportUrl = (fmt: string) => {
    const qs = new URLSearchParams({ ...params, format: fmt }).toString();
    return `${API_URL}/reports/${report}/?${qs}`;
  };

  return (
    <div>
      <PageHeader title={t("reports")} subtitle="Clinical · Financial · Inventory" />

      <div className="mb-4 flex flex-wrap items-end gap-3">
        <div>
          <label className="label">Report</label>
          <select className="input w-auto" value={report} onChange={(e) => setReport(e.target.value)}>
            {REPORTS.map(([k, l]) => (
              <option key={k} value={k}>
                {l}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="label">From</label>
          <input type="date" className="input" value={from} onChange={(e) => setFrom(e.target.value)} />
        </div>
        <div>
          <label className="label">To</label>
          <input type="date" className="input" value={to} onChange={(e) => setTo(e.target.value)} />
        </div>
        <a className="btn-ghost" href={exportUrl("pdf")} target="_blank" rel="noreferrer">
          Export PDF
        </a>
        <a className="btn-ghost" href={exportUrl("excel")} target="_blank" rel="noreferrer">
          Export Excel
        </a>
      </div>

      {data && (
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500 dark:bg-slate-700/50">
              <tr>
                {data.header.map((h: string) => (
                  <th key={h} className="px-4 py-2 text-start font-medium">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.rows.map((row: any[], i: number) => (
                <tr key={i} className="border-t border-slate-100 dark:border-slate-700">
                  {row.map((cell, j) => (
                    <td key={j} className="px-4 py-2">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {data.summary?.length > 0 && (
            <div className="border-t border-slate-200 p-3 text-sm font-medium dark:border-slate-700">
              {data.summary.join(" · ")}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
