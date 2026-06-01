"use client";
import PageHeader from "@/components/PageHeader";
import InvoiceBuilder from "@/components/InvoiceBuilder";

export default function NewInvoicePage() {
  return (
    <div>
      <PageHeader title="New Invoice" subtitle="Build an invoice from line items" />
      <InvoiceBuilder />
    </div>
  );
}
