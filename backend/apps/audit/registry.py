"""Centralised audit logging for models that don't have bespoke signals.

Patient / Visit / Invoice / Payment / Appointment are audited in their own
apps (with richer summaries); this registry covers the rest so that every
clinically- or security-significant change is traceable.
"""
from django.apps import apps as django_apps
from django.db.models.signals import post_save, post_delete

from .utils import log_activity

# model label -> (friendly entity name, log_updates)
AUDITED = {
    "prescriptions.Prescription": ("Prescription", True),
    "treatments.TreatmentPlan": ("Treatment Plan", True),
    "treatments.Treatment": ("Treatment", True),
    "documents.Document": ("Document", True),
    "accounts.Role": ("Role", True),
    "accounts.User": ("User", False),       # avoid noise on each login update
    "accounts.Doctor": ("Doctor", True),
    "dental_charts.ToothCondition": ("Tooth Condition", False),
}


def _make_save_handler(entity, log_updates):
    def handler(sender, instance, created, **kwargs):
        if not created and not log_updates:
            return
        action = "CREATE" if created else "UPDATE"
        log_activity(
            action=action, entity=entity, entity_id=getattr(instance, "id", ""),
            summary=f"{action.title()} {entity}: {str(instance)[:120]}",
        )
    return handler


def _make_delete_handler(entity):
    def handler(sender, instance, **kwargs):
        log_activity(
            action="DELETE", entity=entity, entity_id=getattr(instance, "id", ""),
            summary=f"Deleted {entity}: {str(instance)[:120]}",
        )
    return handler


def connect():
    for label, (entity, log_updates) in AUDITED.items():
        model = django_apps.get_model(label)
        post_save.connect(
            _make_save_handler(entity, log_updates), sender=model, weak=False,
            dispatch_uid=f"audit_save_{label}",
        )
        post_delete.connect(
            _make_delete_handler(entity), sender=model, weak=False,
            dispatch_uid=f"audit_delete_{label}",
        )
