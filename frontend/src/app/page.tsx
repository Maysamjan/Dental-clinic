"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/stores/auth";

export default function Home() {
  const router = useRouter();
  const access = useAuth((s) => s.access);
  useEffect(() => {
    router.replace(access ? "/dashboard" : "/login");
  }, [access, router]);
  return null;
}
