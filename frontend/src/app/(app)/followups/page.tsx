"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useT } from "@/i18n/useT";
import PageHeader from "@/components/PageHeader";

function List({ title, items }: { title: string; items?: any[] }) {
  return (
    <div className="card">
      <h2 className="mb-2 font-semibold">{title}</h2>
      {!items || items.length === 0 ? (
        <p className="text-sm text-slate-400">موردی نیست.</p>
      ) : (
        <ul className="divide-y divide-slate-100 text-sm dark:divide-slate-700">
          {items.map((f) => (
            <li key={f.id} className="flex justify-between py-2">
              <span>{f.patient_name}</span>
              <span className="text-slate-400">{f.note || f.type}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function FollowUpsPage() {
  const t = useT();
  const { data } = useQuery({
    queryKey: ["followup-dashboard"],
    queryFn: async () => (await api.get("/follow-ups/dashboard/")).data,
  });
  return (
    <div>
      <PageHeader title={t("followups")} subtitle="یادآوری‌های داخلی" />
      <div className="grid gap-4 md:grid-cols-3">
        <List title="سررسید امروز" items={data?.due_today} />
        <List title="سررسید فردا" items={data?.due_tomorrow} />
        <List title="پیگیری پرداخت‌ها" items={data?.payment_followups} />
      </div>
    </div>
  );
}
