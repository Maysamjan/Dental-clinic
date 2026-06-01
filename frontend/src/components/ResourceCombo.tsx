"use client";
import { useState, useRef, useEffect } from "react";
import { useList, rowsOf } from "@/lib/hooks";

/**
 * Searchable single-select backed by a DRF list endpoint.
 * `getLabel` renders each option; the selected value is the row id.
 */
export default function ResourceCombo({
  resource,
  value,
  onChange,
  getLabel,
  placeholder = "Search…",
  params = {},
}: {
  resource: string;
  value: number | null;
  onChange: (id: number | null, row?: any) => void;
  getLabel: (row: any) => string;
  placeholder?: string;
  params?: Record<string, any>;
}) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const ref = useRef<HTMLDivElement>(null);
  const { data } = useList(resource, { ...params, ...(search ? { search } : {}), page_size: 20 });
  const rows = rowsOf<any>(data);
  const selected = rows.find((r) => r.id === value);

  useEffect(() => {
    function onDoc(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        className="input flex items-center justify-between text-start"
        onClick={() => setOpen((o) => !o)}
      >
        <span className={selected ? "" : "text-slate-400"}>
          {selected ? getLabel(selected) : placeholder}
        </span>
        <span className="text-slate-400">▾</span>
      </button>
      {open && (
        <div className="absolute z-20 mt-1 w-full rounded-lg border border-slate-200 bg-white shadow-lg dark:border-slate-600 dark:bg-slate-800">
          <input
            autoFocus
            className="input m-2 w-[calc(100%-1rem)]"
            placeholder={placeholder}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <ul className="max-h-56 overflow-y-auto pb-2 text-sm">
            {rows.length === 0 && (
              <li className="px-3 py-2 text-slate-400">No results.</li>
            )}
            {rows.map((r) => (
              <li key={r.id}>
                <button
                  type="button"
                  className="block w-full px-3 py-2 text-start hover:bg-brand-50 dark:hover:bg-slate-700"
                  onClick={() => {
                    onChange(r.id, r);
                    setOpen(false);
                    setSearch("");
                  }}
                >
                  {getLabel(r)}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
