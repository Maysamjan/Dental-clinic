from datetime import date

from django.db import models

from apps.core.models import ArchivableModel


class Patient(ArchivableModel):
    GENDER = [("M", "Male"), ("F", "Female"), ("O", "Other")]

    code = models.CharField(max_length=20, unique=True, editable=False)
    full_name = models.CharField(max_length=150)
    gender = models.CharField(max_length=1, choices=GENDER, default="M")
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    registration_date = models.DateField(default=date.today)

    emergency_contact_name = models.CharField(max_length=120, blank=True)
    emergency_contact_phone = models.CharField(max_length=30, blank=True)

    medical_history = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to="patients/photos/", null=True, blank=True)

    class Meta(ArchivableModel.Meta):
        indexes = [models.Index(fields=["full_name"]), models.Index(fields=["phone"])]

    def __str__(self):
        return f"{self.code} - {self.full_name}"

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def save(self, *args, **kwargs):
        if not self.code:
            # Generate a clinic ID like P-000123 based on the next id.
            last = Patient.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.code = f"P-{next_id:06d}"
        super().save(*args, **kwargs)
