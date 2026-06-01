"use client";
import { useState, useEffect } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useUI, isRTL } from "@/stores/ui";

export default function Providers({ children }: { children: React.ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { staleTime: 15000, retry: 1 } },
      })
  );
  const { theme, locale } = useUI();

  // Apply theme + direction to <html> reactively.
  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle("dark", theme === "dark");
    root.dir = isRTL(locale) ? "rtl" : "ltr";
    root.lang = locale;
  }, [theme, locale]);

  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
