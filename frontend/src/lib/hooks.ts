"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Paginated } from "@/lib/types";

/** Fetch a paginated list endpoint. */
export function useList<T = any>(
  resource: string,
  params: Record<string, any> = {}
) {
  return useQuery({
    queryKey: [resource, params],
    queryFn: async () => {
      const { data } = await api.get<Paginated<T> | T[]>(`/${resource}/`, {
        params,
      });
      return data;
    },
  });
}

export function rowsOf<T>(data: Paginated<T> | T[] | undefined): T[] {
  if (!data) return [];
  return Array.isArray(data) ? data : data.results;
}
