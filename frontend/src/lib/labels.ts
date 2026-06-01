// Persian labels for backend enum/code values, shown across the UI.

export const ROLE_FA: Record<string, string> = {
  ADMIN: "مدیر سیستم",
  MANAGER: "مدیر کلینیک",
  DOCTOR: "داکتر",
  RECEPTIONIST: "پذیرش",
  ACCOUNTANT: "محاسب",
  INVENTORY_OFFICER: "مسئول انبار",
};

export const APPT_STATUS_FA: Record<string, string> = {
  SCHEDULED: "تعیین‌شده",
  CONFIRMED: "تأییدشده",
  ARRIVED: "حاضر شد",
  COMPLETED: "تکمیل‌شده",
  CANCELLED: "لغوشده",
  NO_SHOW: "غایب",
};

export const WORKFLOW_FA: Record<string, string> = {
  WAITING: "در انتظار",
  IN_CONSULTATION: "در حال معاینه",
  TREATMENT_IN_PROGRESS: "در حال تداوی",
  COMPLETED: "تکمیل‌شده",
};

export const INVOICE_STATUS_FA: Record<string, string> = {
  PAID: "پرداخت‌شده",
  PARTIAL: "قسمی",
  UNPAID: "پرداخت‌نشده",
};

export const TREATMENT_STATUS_FA: Record<string, string> = {
  PLANNED: "برنامه‌ریزی‌شده",
  IN_PROGRESS: "در حال انجام",
  COMPLETED: "تکمیل‌شده",
  CANCELLED: "لغوشده",
  DRAFT: "پیش‌نویس",
  ACTIVE: "فعال",
};

export const PAYMENT_METHOD_FA: Record<string, string> = {
  CASH: "نقد",
  BANK_TRANSFER: "انتقال بانکی",
};

export const GENDER_FA: Record<string, string> = {
  M: "مرد",
  F: "زن",
  O: "سایر",
};

export const DOC_TYPE_FA: Record<string, string> = {
  PHOTO: "عکس بیمار",
  XRAY: "رادیوگرافی",
  OPG: "OPG",
  PDF: "سند PDF",
  LAB: "فایل لابراتوار",
};

export const FOLLOWUP_TYPE_FA: Record<string, string> = {
  VISIT: "ویزیت بعدی",
  PAYMENT: "پیگیری پرداخت",
};

export const ACTION_FA: Record<string, string> = {
  LOGIN: "ورود",
  LOGOUT: "خروج",
  CREATE: "ایجاد",
  UPDATE: "ویرایش",
  DELETE: "حذف",
  PAYMENT: "پرداخت",
  INVOICE: "صورتحساب",
};

export const fa = (map: Record<string, string>, key: string) => map[key] ?? key;

