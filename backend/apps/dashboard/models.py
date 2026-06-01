from django.db import models


class ClinicInfo(models.Model):
    """Singleton-style clinic information & system settings."""

    name = models.CharField(max_length=150, default="Dental Clinic")
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=60, blank=True)
    email = models.EmailField(blank=True)
    website = models.CharField(max_length=120, blank=True)
    logo = models.ImageField(upload_to="clinic/", null=True, blank=True)

    default_language = models.CharField(max_length=5, default="fa")
    default_calendar = models.CharField(
        max_length=12,
        choices=[("gregorian", "Gregorian"), ("solar_hijri", "Solar Hijri")],
        default="solar_hijri",
    )
    currency = models.CharField(max_length=10, default="AFN")

    # Financial
    tax_enabled = models.BooleanField(default=False)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    invoice_footer = models.CharField(max_length=300, blank=True)

    # Prescriptions
    prescription_header = models.CharField(max_length=300, blank=True)
    prescription_footer = models.CharField(max_length=300, blank=True)

    # Scheduling
    appointment_duration_minutes = models.PositiveSmallIntegerField(default=30)
    working_hours = models.JSONField(default=dict, blank=True)

    # Free-form / future settings (e.g. backup schedule)
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
