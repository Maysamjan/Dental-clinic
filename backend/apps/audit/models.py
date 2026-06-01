from django.conf import settings
from django.db import models


class ActivityLog(models.Model):
    """Append-only audit trail of significant actions."""

    ACTIONS = [
        ("LOGIN", "Login"),
        ("LOGOUT", "Logout"),
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("PAYMENT", "Payment"),
        ("INVOICE", "Invoice"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="activity_logs",
    )
    action = models.CharField(max_length=20, choices=ACTIONS)
    entity = models.CharField(max_length=60, blank=True)
    entity_id = models.CharField(max_length=40, blank=True)
    summary = models.CharField(max_length=300, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["entity", "entity_id"]),
            models.Index(fields=["action"]),
        ]

    def __str__(self):
        return f"{self.action} {self.entity}#{self.entity_id} by {self.user_id}"
