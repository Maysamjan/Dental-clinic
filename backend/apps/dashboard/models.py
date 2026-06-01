from django.db import models


class ClinicInfo(models.Model):
    """Singleton-style clinic information & system settings."""

    name = models.CharField(max_length=150, default="Dental Clinic")
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=60, blank=True)
    email = models.EmailField(blank=True)
    logo = models.ImageField(upload_to="clinic/", null=True, blank=True)

    default_language = models.CharField(max_length=5, default="en")
    default_calendar = models.CharField(
        max_length=12,
        choices=[("gregorian", "Gregorian"), ("solar_hijri", "Solar Hijri")],
        default="gregorian",
    )
    currency = models.CharField(max_length=10, default="AFN")
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Clinic information"
        verbose_name_plural = "Clinic information"

    def __str__(self):
        return self.name

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
