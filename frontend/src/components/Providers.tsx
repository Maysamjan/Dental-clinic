"use client";
import { useState, useEffect } from "react";
import { QueryClient, QueryClientProvider, QueryCache } from "@tanstack/react-query";
import { useUI, isRTL } from "@/stores/ui";
import { useToast, apiError } from "@/stores/toast";
import Toaster from "@/components/Toaster";

export default function Providers({ children }: { children: React.ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { staleTime: 15000, retry: 1 } },
        // Surface background data-fetch failures (other than auth) as toasts.
        queryCache: new QueryCache({
          onError: (error: any) => {
            if (error?.response?.status === 401) return;
            useToast.getState().push("error", apiError(error));
          },
        }),
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

  return (
    <QueryClientProvider client={client}>
      {children}
      <Toaster />
    </QueryClientProvider>
  );
}
