"use client";
import PageHeader from "@/components/PageHeader";
import InvoiceBuilder from "@/components/InvoiceBuilder";

export default function NewInvoicePage() {
  return (
    <div>
      <PageHeader title="صورتحساب جدید" subtitle="ساخت صورتحساب از اقلام" />
      <InvoiceBuilder />
    </div>
  );
}
