"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/stores/auth";
import { useT } from "@/i18n/useT";

export default function LoginPage() {
  const router = useRouter();
  const login = useAuth((s) => s.login);
  const t = useT();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(username, password);
      router.replace("/dashboard");
    } catch {
      setError("Invalid username or password");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-brand-700 to-brand-500 p-4">
      <form
        onSubmit={submit}
        className="w-full max-w-sm rounded-2xl bg-white p-8 shadow-xl dark:bg-slate-800"
      >
        <div className="mb-6 text-center">
          <div className="text-4xl">🦷</div>
          <h1 className="mt-2 text-xl font-bold text-brand-700 dark:text-brand-100">
            {t("app_name")}
          </h1>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
            {error}
          </div>
        )}

        <div className="mb-3">
          <label className="label">{t("username")}</label>
          <input
            className="input"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoFocus
          />
        </div>
        <div className="mb-5">
          <label className="label">{t("password")}</label>
          <input
            className="input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button className="btn-primary w-full" disabled={loading}>
          {loading ? "…" : t("login")}
        </button>
        <p className="mt-4 text-center text-xs text-slate-400">
          Demo: admin / Passw0rd!
        </p>
      </form>
    </div>
  );
}
