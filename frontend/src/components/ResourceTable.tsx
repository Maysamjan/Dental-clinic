"use client";
import { useState } from "react";
import { useList, rowsOf } from "@/lib/hooks";

export interface Column {
  key: string;
  label: string;
  render?: (row: any) => React.ReactNode;
}

/** Generic searchable, read-oriented list table backed by a DRF endpoint. */
export default function ResourceTable({
  resource,
  columns,
  params = {},
  searchable = true,
}: {
  resource: string;
  columns: Column[];
  params?: Record<string, any>;
  searchable?: boolean;
}) {
  const [search, setSearch] = useState("");
  const { data, isLoading, isError } = useList(resource, {
    ...params,
    ...(search ? { search } : {}),
  });
  const rows = rowsOf(data);

  return (
    <div className="card overflow-hidden p-0">
      {searchable && (
        <div className="border-b border-slate-200 p-3 dark:border-slate-700">
          <input
            className="input max-w-xs"
            placeholder="Search…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-start text-xs uppercase text-slate-500 dark:bg-slate-700/50">
            <tr>
              {columns.map((c) => (
                <th key={c.key} className="px-4 py-2 text-start font-medium">
                  {c.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr>
                <td colSpan={columns.length} className="p-6 text-center text-slate-400">
                  Loading…
                </td>
              </tr>
            )}
            {isError && (
              <tr>
                <td colSpan={columns.length} className="p-6 text-center text-red-500">
                  Failed to load data.
                </td>
              </tr>
            )}
            {!isLoading && rows.length === 0 && (
              <tr>
                <td colSpan={columns.length} className="p-6 text-center text-slate-400">
                  No records.
                </td>
              </tr>
            )}
            {rows.map((row: any) => (
              <tr
                key={row.id}
                className="border-t border-slate-100 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-700/40"
              >
                {columns.map((c) => (
                  <td key={c.key} className="px-4 py-2">
                    {c.render ? c.render(row) : (row[c.key] ?? "—")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
