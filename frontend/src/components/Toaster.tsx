"use client";
import { useToast } from "@/stores/toast";

const STYLES: Record<string, string> = {
  success: "bg-green-600",
  error: "bg-red-600",
  info: "bg-slate-700",
};
const ICON: Record<string, string> = { success: "✓", error: "!", info: "i" };

export default function Toaster() {
  const { toasts, dismiss } = useToast();
  return (
    <div className="fixed bottom-4 end-4 z-[100] flex flex-col gap-2">
      {toasts.map((t) => (
        <button
          key={t.id}
          onClick={() => dismiss(t.id)}
          className={`flex max-w-sm items-center gap-2 rounded-lg px-4 py-3 text-sm text-white shadow-lg ${STYLES[t.kind]}`}
        >
          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-white/25 text-xs font-bold">
            {ICON[t.kind]}
          </span>
          <span className="text-start">{t.message}</span>
        </button>
      ))}
    </div>
  );
}
