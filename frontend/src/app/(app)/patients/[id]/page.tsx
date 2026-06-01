"use client";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import PageHeader from "@/components/PageHeader";

export default function PatientDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data } = useQuery({
    queryKey: ["patient-history", id],
    queryFn: async () => (await api.get(`/patients/${id}/history/`)).data,
  });

  const p = data?.patient;

  return (
    <div>
      <PageHeader
        title={p ? p.full_name : "Patient"}
        subtitle={p ? `${p.code} · ${p.gender} · ${p.age ?? "?"} yrs` : ""}
        action={
          <Link href={`/dental-chart?patient=${id}`} className="btn-ghost">
            🦷 Dental Chart
          </Link>
        }
      />

      {p && (
        <div className="mb-4 grid gap-4 md:grid-cols-3">
          <div className="card">
            <div className="text-xs text-slate-400">Phone</div>
            <div>{p.phone || "—"}</div>
          </div>
          <div className="card">
            <div className="text-xs text-slate-400">Allergies</div>
            <div className="text-red-600">{p.allergies || "None recorded"}</div>
          </div>
          <div className="card">
            <div className="text-xs text-slate-400">Medical History</div>
            <div>{p.medical_history || "—"}</div>
          </div>
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <Section title="Visits" rows={data?.visits} cols={["visit_date", "diagnosis", "workflow_status"]} />
        <Section title="Appointments" rows={data?.appointments} cols={["start", "status", "reason"]} />
        <Section title="Prescriptions" rows={data?.prescriptions} cols={["created_at", "doctor_name"]} />
        <Section title="Invoices" rows={data?.invoices} cols={["number", "total", "balance", "status"]} />
      </div>
    </div>
  );
}

function Section({ title, rows, cols }: { title: string; rows?: any[]; cols: string[] }) {
  return (
    <div className="card">
      <h2 className="mb-2 font-semibold">{title}</h2>
      {!rows || rows.length === 0 ? (
        <p className="text-sm text-slate-400">No records.</p>
      ) : (
        <table className="w-full text-sm">
          <tbody>
            {rows.map((r, i) => (
              <tr key={i} className="border-t border-slate-100 dark:border-slate-700">
                {cols.map((c) => (
                  <td key={c} className="py-1.5 pe-3">
                    {String(r[c] ?? "—").slice(0, 40)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
