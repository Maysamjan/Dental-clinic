from decimal import Decimal

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.audit.utils import log_activity
from apps.core.realtime import broadcast, DASHBOARD_GROUP
from .models import Payment, Invoice, Installment

ZERO = Decimal("0.00")


@receiver(post_save, sender=Payment)
def on_payment_saved(sender, instance, created, **kwargs):
    invoice = instance.invoice
    invoice.recompute()

    # Update the linked installment's paid amount/status.
    inst = instance.installment
    if inst:
        inst.paid_amount = sum((p.amount for p in inst.payments.all()), ZERO)
        if inst.paid_amount <= ZERO:
            inst.status = "PENDING"
        elif inst.paid_amount < inst.amount:
            inst.status = "PARTIAL"
        else:
            inst.status = "PAID"
        inst.save(update_fields=["paid_amount", "status"])

    if created:
        log_activity(
            action="PAYMENT", entity="Payment", entity_id=instance.id,
            summary=f"Payment {instance.amount} ({instance.method}) on "
                    f"{invoice.number}",
        )
    broadcast(DASHBOARD_GROUP, "refresh", {"reason": "payment"})


@receiver(post_delete, sender=Payment)
def on_payment_deleted(sender, instance, **kwargs):
    try:
        instance.invoice.recompute()
    except Invoice.DoesNotExist:
        pass


@receiver(post_save, sender=Invoice)
def on_invoice_saved(sender, instance, created, **kwargs):
    if created:
        log_activity(
            action="INVOICE", entity="Invoice", entity_id=instance.id,
            summary=f"Created invoice {instance.number} (total {instance.total})",
        )
