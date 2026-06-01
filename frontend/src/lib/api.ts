"use client";
import axios from "axios";
import { useAuth } from "@/stores/auth";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost/api";
export const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL || "ws://localhost/ws";

export const api = axios.create({ baseURL: API_URL });

// Attach the access token to every request.
api.interceptors.request.use((config) => {
  const token = useAuth.getState().access;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Transparently refresh the access token on 401, once.
let refreshing: Promise<string | null> | null = null;

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      if (!refreshing) refreshing = useAuth.getState().refreshToken();
      const newToken = await refreshing;
      refreshing = null;
      if (newToken) {
        original.headers.Authorization = `Bearer ${newToken}`;
        return api(original);
      }
      useAuth.getState().logout();
    }
    return Promise.reject(error);
  }
);
