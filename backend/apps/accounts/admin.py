from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Role, Doctor, UserSession


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "full_name", "email", "role", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Clinic profile", {"fields": ("full_name", "phone", "role", "last_login_ip")}),
    )


admin.site.register(Role)
admin.site.register(Doctor)
admin.site.register(UserSession)
