from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimeStampedModel


class Role(TimeStampedModel):
    """A named set of permission codes (see permissions_matrix)."""

    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    permissions = models.JSONField(default=list, blank=True)
    is_system = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Custom user. Each user has at most one Role."""

    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    role = models.ForeignKey(
        Role, null=True, blank=True, on_delete=models.SET_NULL, related_name="users"
    )
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.get_full_name() or self.username
        super().save(*args, **kwargs)

    @property
    def role_code(self):
        return self.role.code if self.role else None


class Doctor(TimeStampedModel):
    """Clinical profile attached to a User with the DOCTOR role."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="doctor_profile"
    )
    specialization = models.CharField(max_length=120, blank=True)
    license_number = models.CharField(max_length=60, blank=True)
    working_hours = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.full_name or self.user.username}"


class UserSession(models.Model):
    """Tracks login sessions for security auditing."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    login_at = models.DateTimeField(auto_now_add=True)
    logout_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-login_at"]
