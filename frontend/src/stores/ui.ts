"use client";
import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Locale = "en" | "fa" | "ps";
export type Theme = "light" | "dark";

interface UIState {
  locale: Locale;
  theme: Theme;
  sidebarOpen: boolean;
  setLocale: (l: Locale) => void;
  toggleTheme: () => void;
  toggleSidebar: () => void;
}

export const isRTL = (locale: Locale) => locale === "fa" || locale === "ps";

export const useUI = create<UIState>()(
  persist(
    (set, get) => ({
      locale: "en",
      theme: "light",
      sidebarOpen: true,
      setLocale: (locale) => set({ locale }),
      toggleTheme: () => set({ theme: get().theme === "light" ? "dark" : "light" }),
      toggleSidebar: () => set({ sidebarOpen: !get().sidebarOpen }),
    }),
    { name: "dental-ui" }
  )
);
