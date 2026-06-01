"use client";
import { create } from "zustand";

export type ToastKind = "success" | "error" | "info";
export interface Toast {
  id: number;
  kind: ToastKind;
  message: string;
}

interface ToastState {
  toasts: Toast[];
  push: (kind: ToastKind, message: string) => void;
  dismiss: (id: number) => void;
}

let counter = 0;

export const useToast = create<ToastState>((set, get) => ({
  toasts: [],
  push: (kind, message) => {
    const id = ++counter;
    set({ toasts: [...get().toasts, { id, kind, message }] });
    setTimeout(() => get().dismiss(id), 4000);
  },
  dismiss: (id) => set({ toasts: get().toasts.filter((t) => t.id !== id) }),
}));

/** Extract a human-readable message from an Axios/DRF error. */
export function apiError(err: any): string {
  const data = err?.response?.data;
  if (!data) return err?.message || "Something went wrong.";
  if (typeof data === "string") return data;
  if (data.detail) return data.detail;
  // DRF field errors: { field: ["msg"] }
  const first = Object.entries(data)[0];
  if (first) {
    const [field, msgs] = first;
    const msg = Array.isArray(msgs) ? msgs[0] : msgs;
    return field === "non_field_errors" ? String(msg) : `${field}: ${msg}`;
  }
  return "Request failed.";
}
