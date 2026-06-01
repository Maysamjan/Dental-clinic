from decimal import Decimal

from django.db.models import F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.core.realtime import broadcast, DASHBOARD_GROUP
from .models import InventoryItem, InventoryTransaction


def _apply(item_id, delta):
    InventoryItem.objects.filter(pk=item_id).update(quantity=F("quantity") + delta)


@receiver(post_save, sender=InventoryTransaction)
def adjust_stock_on_create(sender, instance, created, **kwargs):
    if not created:
        return
    delta = instance.quantity if instance.type == "IN" else -instance.quantity
    _apply(instance.item_id, delta)

    item = InventoryItem.objects.get(pk=instance.item_id)
    if item.is_low_stock:
        broadcast(DASHBOARD_GROUP, "inventory.low_stock",
                  {"item": item.name, "quantity": str(item.quantity)})


@receiver(post_delete, sender=InventoryTransaction)
def revert_stock_on_delete(sender, instance, **kwargs):
    delta = -instance.quantity if instance.type == "IN" else instance.quantity
    _apply(instance.item_id, delta)
