"use client";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import { useT } from "@/i18n/useT";

export default function DocumentsPage() {
  const t = useT();
  return (
    <div>
      <PageHeader title={t("documents")} subtitle="Photos · X-Rays · OPG · PDFs · Lab files" />
      <ResourceTable
        resource="documents"
        searchable={false}
        columns={[
          { key: "title", label: "Title" },
          { key: "type", label: "Type" },
          { key: "created_at", label: "Uploaded", render: (r) => new Date(r.created_at).toLocaleDateString() },
          {
            key: "file_url",
            label: "",
            render: (r) =>
              r.file_url ? (
                <a className="text-brand-600 hover:underline" href={r.file_url} target="_blank" rel="noreferrer">
                  Open ↗
                </a>
              ) : null,
          },
        ]}
      />
    </div>
  );
}
