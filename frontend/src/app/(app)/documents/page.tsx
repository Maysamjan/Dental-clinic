"use client";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import { useT } from "@/i18n/useT";
import { DOC_TYPE_FA } from "@/lib/labels";

export default function DocumentsPage() {
  const t = useT();
  return (
    <div>
      <PageHeader title={t("documents")} subtitle="عکس · رادیوگرافی · OPG · PDF · فایل لابراتوار" />
      <ResourceTable
        resource="documents"
        searchable={false}
        columns={[
          { key: "title", label: "عنوان" },
          { key: "type", label: "نوع", render: (r) => DOC_TYPE_FA[r.type] ?? r.type },
          { key: "created_at", label: "تاریخ بارگذاری", render: (r) => new Date(r.created_at).toLocaleDateString() },
          {
            key: "file_url",
            label: "",
            render: (r) =>
              r.file_url ? (
                <a className="text-brand-600 hover:underline" href={r.file_url} target="_blank" rel="noreferrer">
                  باز کردن ↗
                </a>
              ) : null,
          },
        ]}
      />
    </div>
  );
}
