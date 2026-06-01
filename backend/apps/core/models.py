"""Shared abstract base models."""
from django.db import models


class TimeStampedModel(models.Model):
    """Adds self-managed created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SoftDeleteQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_archived=False)


class ArchivableModel(TimeStampedModel):
    """Base for records that are archived rather than hard-deleted."""

    is_archived = models.BooleanField(default=False)

    objects = SoftDeleteQuerySet.as_manager()

    class Meta(TimeStampedModel.Meta):
        abstract = True
