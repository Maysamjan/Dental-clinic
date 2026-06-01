"use client";
import { create } from "zustand";
import { persist } from "zustand/middleware";
import axios from "axios";
import { API_URL } from "@/lib/api";
import type { User } from "@/lib/types";

interface AuthState {
  access: string | null;
  refresh: string | null;
  user: User | null;
  hasHydrated: boolean;
  setHasHydrated: (v: boolean) => void;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<string | null>;
}

export const useAuth = create<AuthState>()(
  persist(
    (set, get) => ({
      access: null,
      refresh: null,
      user: null,
      hasHydrated: false,
      setHasHydrated: (v) => set({ hasHydrated: v }),

      login: async (username, password) => {
        const { data } = await axios.post(`${API_URL}/auth/login/`, {
          username,
          password,
        });
        set({ access: data.access, refresh: data.refresh, user: data.user });
      },

      logout: () => {
        const token = get().access;
        if (token) {
          axios
            .post(`${API_URL}/auth/me/logout/`, {}, {
              headers: { Authorization: `Bearer ${token}` },
            })
            .catch(() => {});
        }
        set({ access: null, refresh: null, user: null });
      },

      refreshToken: async () => {
        const refresh = get().refresh;
        if (!refresh) return null;
        try {
          const { data } = await axios.post(`${API_URL}/auth/refresh/`, {
            refresh,
          });
          set({ access: data.access, refresh: data.refresh ?? refresh });
          return data.access as string;
        } catch {
          set({ access: null, refresh: null, user: null });
          return null;
        }
      },
    }),
    {
      name: "dental-auth",
      onRehydrateStorage: () => (state) => state?.setHasHydrated(true),
    }
  )
);
