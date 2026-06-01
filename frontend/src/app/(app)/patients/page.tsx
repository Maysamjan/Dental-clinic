"use client";
import { useState } from "react";
import Link from "next/link";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useT } from "@/i18n/useT";
import { useAuth } from "@/stores/auth";
import { hasPerm } from "@/lib/permissions";
import { GENDER_FA } from "@/lib/labels";
import PageHeader from "@/components/PageHeader";
import ResourceTable from "@/components/ResourceTable";
import Modal from "@/components/Modal";

export default function PatientsPage() {
  const t = useT();
  const qc = useQueryClient();
  const permissions = useAuth((s) => s.user?.permissions);
  const canAdd = hasPerm(permissions, "patients.add");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    full_name: "",
    gender: "M",
    phone: "",
    date_of_birth: "",
    allergies: "",
    medical_history: "",
  });

  const create = useMutation({
    mutationFn: () =>
      api.post("/patients/", {
        ...form,
        date_of_birth: form.date_of_birth || null,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["patients"] });
      setOpen(false);
      setForm({ full_name: "", gender: "M", phone: "", date_of_birth: "", allergies: "", medical_history: "" });
    },
  });

  return (
    <div>
      <PageHeader
        title={t("patients")}
        action={
          canAdd ? (
            <button className="btn-primary" onClick={() => setOpen(true)}>
              + {t("add")}
            </button>
          ) : null
        }
      />

      <ResourceTable
        resource="patients"
        columns={[
          { key: "code", label: "شناسه" },
          {
            key: "full_name",
            label: t("name"),
            render: (r) => (
              <Link className="text-brand-600 hover:underline" href={`/patients/${r.id}`}>
                {r.full_name}
              </Link>
            ),
          },
          { key: "gender", label: t("gender"), render: (r) => GENDER_FA[r.gender] ?? r.gender },
          { key: "age", label: t("age") },
          { key: "phone", label: t("phone") },
        ]}
      />

      <Modal open={open} title="بیمار جدید" onClose={() => setOpen(false)}>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            create.mutate();
          }}
          className="grid grid-cols-2 gap-3"
        >
          <div className="col-span-2">
            <label className="label">نام کامل</label>
            <input
              className="input"
              required
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
            />
          </div>
          <div>
            <label className="label">{t("gender")}</label>
            <select
              className="input"
              value={form.gender}
              onChange={(e) => setForm({ ...form, gender: e.target.value })}
            >
              <option value="M">مرد</option>
              <option value="F">زن</option>
              <option value="O">سایر</option>
            </select>
          </div>
          <div>
            <label className="label">تاریخ تولد</label>
            <input
              type="date"
              className="input"
              value={form.date_of_birth}
              onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })}
            />
          </div>
          <div className="col-span-2">
            <label className="label">{t("phone")}</label>
            <input
              className="input"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
            />
          </div>
          <div className="col-span-2">
            <label className="label">حساسیت‌ها (الرژی)</label>
            <input
              className="input"
              value={form.allergies}
              onChange={(e) => setForm({ ...form, allergies: e.target.value })}
            />
          </div>
          <div className="col-span-2 mt-2 flex justify-end gap-2">
            <button type="button" className="btn-ghost" onClick={() => setOpen(false)}>
              {t("cancel")}
            </button>
            <button className="btn-primary" disabled={create.isPending}>
              {t("save")}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
