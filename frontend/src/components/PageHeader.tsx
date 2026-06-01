"use client";

export default function PageHeader({
  title,
  subtitle,
  action,
}: {
  title: string;
  subtitle?: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <div className="mb-5 flex items-end justify-between gap-3">
      <div>
        <h1 className="text-xl font-bold">{title}</h1>
        {subtitle && (
          <p className="text-sm text-slate-400">{subtitle}</p>
        )}
      </div>
      {action}
    </div>
  );
}
