"""Report data builders. Each returns (title, header, rows, summary_lines)."""
from datetime import datetime
from decimal import Decimal

from django.db.models import Sum, Count, F
from django.utils.dateparse import parse_date

from apps.billing.models import Invoice, Payment
from apps.expenses.models import Expense
from apps.inventory.models import InventoryItem, InventoryTransaction
from apps.visits.models import Visit
from apps.treatments.models import Treatment

ZERO = Decimal("0.00")


def _range(params):
    start = parse_date(params.get("from")) if params.get("from") else None
    end = parse_date(params.get("to")) if params.get("to") else None
    return start, end


def revenue_report(params):
    start, end = _range(params)
    qs = Payment.objects.all()
    if start:
        qs = qs.filter(paid_at__date__gte=start)
    if end:
        qs = qs.filter(paid_at__date__lte=end)
    rows = [
        [p.paid_at.strftime("%Y-%m-%d"), p.invoice.number,
         p.invoice.patient.full_name, p.get_method_display(), str(p.amount)]
        for p in qs.select_related("invoice", "invoice__patient")
    ]
    total = qs.aggregate(s=Sum("amount"))["s"] or ZERO
    return (
        "Revenue Report",
        ["Date", "Invoice", "Patient", "Method", "Amount"],
        rows,
        [f"Total revenue: {total}", f"Payments: {qs.count()}"],
    )


def payments_report(params):
    return revenue_report(params)  # alias; same dataset


def outstanding_report(params):
    qs = Invoice.objects.exclude(status="PAID").select_related("patient")
    rows = [
        [i.number, i.patient.full_name, str(i.total), str(i.paid_amount), str(i.balance)]
        for i in qs
    ]
    total = qs.aggregate(s=Sum("balance"))["s"] or ZERO
    return (
        "Outstanding Balances",
        ["Invoice", "Patient", "Total", "Paid", "Balance"],
        rows,
        [f"Total outstanding: {total}", f"Invoices: {qs.count()}"],
    )


def expense_report(params):
    start, end = _range(params)
    qs = Expense.objects.select_related("category")
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    rows = [
        [e.date.strftime("%Y-%m-%d"), e.category.name, e.description, str(e.amount)]
        for e in qs
    ]
    total = qs.aggregate(s=Sum("amount"))["s"] or ZERO
    return (
        "Expense Report",
        ["Date", "Category", "Description", "Amount"],
        rows,
        [f"Total expenses: {total}"],
    )


def profit_loss_report(params):
    start, end = _range(params)
    pay = Payment.objects.all()
    exp = Expense.objects.all()
    if start:
        pay = pay.filter(paid_at__date__gte=start)
        exp = exp.filter(date__gte=start)
    if end:
        pay = pay.filter(paid_at__date__lte=end)
        exp = exp.filter(date__lte=end)
    revenue = pay.aggregate(s=Sum("amount"))["s"] or ZERO
    expenses = exp.aggregate(s=Sum("amount"))["s"] or ZERO
    profit = revenue - expenses
    rows = [
        ["Revenue", str(revenue)],
        ["Expenses", str(expenses)],
        ["Net Profit / Loss", str(profit)],
    ]
    return "Profit and Loss", ["Item", "Amount"], rows, []


def doctor_performance_report(params):
    qs = (
        Visit.objects.values("doctor__user__full_name")
        .annotate(visits=Count("id"))
        .order_by("-visits")
    )
    rows = [[r["doctor__user__full_name"] or "Unassigned", str(r["visits"])] for r in qs]
    return "Doctor Performance", ["Doctor", "Visits"], rows, []


def treatment_report(params):
    qs = (
        Treatment.objects.values("catalog_item__name", "status")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    rows = [
        [r["catalog_item__name"] or "-", r["status"], str(r["count"])] for r in qs
    ]
    return "Treatment Report", ["Treatment", "Status", "Count"], rows, []


def current_stock_report(params):
    qs = InventoryItem.objects.all()
    rows = [
        [i.name, i.category, i.unit, str(i.quantity), str(i.minimum_stock)]
        for i in qs
    ]
    return (
        "Current Stock",
        ["Item", "Category", "Unit", "Quantity", "Min Stock"],
        rows, [],
    )


def low_stock_report(params):
    qs = InventoryItem.objects.filter(quantity__lte=F("minimum_stock"))
    rows = [[i.name, str(i.quantity), str(i.minimum_stock)] for i in qs]
    return "Low Stock", ["Item", "Quantity", "Min Stock"], rows, []


def inventory_movement_report(params):
    start, end = _range(params)
    qs = InventoryTransaction.objects.select_related("item")
    if start:
        qs = qs.filter(created_at__date__gte=start)
    if end:
        qs = qs.filter(created_at__date__lte=end)
    rows = [
        [t.created_at.strftime("%Y-%m-%d"), t.item.name, t.type, str(t.quantity), t.reason]
        for t in qs
    ]
    return (
        "Inventory Movement",
        ["Date", "Item", "Type", "Quantity", "Reason"],
        rows, [],
    )


REPORTS = {
    "revenue": revenue_report,
    "payments": payments_report,
    "outstanding": outstanding_report,
    "expenses": expense_report,
    "profit-loss": profit_loss_report,
    "doctor-performance": doctor_performance_report,
    "treatments": treatment_report,
    "current-stock": current_stock_report,
    "low-stock": low_stock_report,
    "inventory-movement": inventory_movement_report,
}
