from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.audit.utils import log_activity
from .models import Patient


@receiver(post_save, sender=Patient)
def log_patient_save(sender, instance, created, **kwargs):
    action = "CREATE" if created else "UPDATE"
    log_activity(
        action=action, entity="Patient", entity_id=instance.id,
        summary=f"{action.title()} patient {instance.code} ({instance.full_name})",
    )


@receiver(post_delete, sender=Patient)
def log_patient_delete(sender, instance, **kwargs):
    log_activity(
        action="DELETE", entity="Patient", entity_id=instance.id,
        summary=f"Deleted patient {instance.code}",
    )
