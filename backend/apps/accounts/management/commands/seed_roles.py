from django.core.management.base import BaseCommand

from apps.accounts.models import Role
from apps.accounts.permissions_matrix import ROLE_DEFINITIONS


class Command(BaseCommand):
    help = "Create or update the system roles and their permission matrices."

    def handle(self, *args, **options):
        for code, spec in ROLE_DEFINITIONS.items():
            role, created = Role.objects.update_or_create(
                code=code,
                defaults={
                    "name": spec["name"],
                    "permissions": spec["permissions"],
                    "is_system": spec.get("is_system", True),
                },
            )
            verb = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{verb} role {code} ({role.name})"))
        self.stdout.write(self.style.SUCCESS("Roles seeded."))
