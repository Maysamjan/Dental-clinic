"use client";
import { useUI } from "@/stores/ui";
import { getDict, DictKey } from "./dictionaries";

export function useT() {
  const locale = useUI((s) => s.locale);
  const dict = getDict(locale);
  return (key: DictKey) => dict[key] ?? key;
}
