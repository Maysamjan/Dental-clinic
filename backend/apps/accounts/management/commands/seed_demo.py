from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import Role, User, Doctor
from apps.patients.models import Patient
from apps.appointments.models import Appointment
from apps.treatments.models import TreatmentCatalog
from apps.expenses.models import ExpenseCategory
from apps.inventory.models import InventoryItem, Supplier


class Command(BaseCommand):
    help = "Seed demonstration data (roles must be seeded first)."

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        # Users (one per role)
        accounts = {
            "admin": "ADMIN",
            "manager": "MANAGER",
            "doctor": "DOCTOR",
            "reception": "RECEPTIONIST",
            "accountant": "ACCOUNTANT",
            "inventory": "INVENTORY_OFFICER",
        }
        for username, role_code in accounts.items():
            role = Role.objects.filter(code=role_code).first()
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"full_name": username.title(), "role": role,
                          "is_staff": role_code == "ADMIN"},
            )
            if created:
                user.set_password("Passw0rd!")
                if role_code == "ADMIN":
                    user.is_superuser = True
                user.save()
            if role_code == "DOCTOR":
                Doctor.objects.get_or_create(
                    user=user, defaults={"specialization": "General Dentistry"}
                )

        # Expense categories
        for name in ExpenseCategory.DEFAULTS:
            ExpenseCategory.objects.get_or_create(name=name)

        # Treatment catalog
        catalog = [
            ("CONS", "Consultation", "Diagnostic", 500),
            ("SCAL", "Scaling & Polishing", "Hygiene", 1500),
            ("RCT", "Root Canal Treatment", "Endodontics", 6000),
            ("CRWN", "Crown", "Prosthodontics", 8000),
            ("EXT", "Extraction", "Surgery", 1200),
            ("FILL", "Composite Filling", "Restorative", 2000),
        ]
        for code, name, cat, price in catalog:
            TreatmentCatalog.objects.get_or_create(
                code=code,
                defaults={"name": name, "category": cat,
                          "default_price": Decimal(price)},
            )

        # Supplier + inventory
        supplier, _ = Supplier.objects.get_or_create(
            name="Kabul Dental Supplies", defaults={"phone": "0700000000"}
        )
        items = [
            ("Latex Gloves (box)", "Consumables", "box", 40, 10),
            ("Anaesthetic Cartridges", "Pharmacy", "pcs", 8, 20),
            ("Composite Resin", "Materials", "syringe", 25, 5),
        ]
        for name, cat, unit, qty, minimum in items:
            InventoryItem.objects.get_or_create(
                name=name,
                defaults={"category": cat, "unit": unit,
                          "quantity": qty, "minimum_stock": minimum,
                          "supplier": supplier},
            )

        # Patients + appointments
        doctor = Doctor.objects.first()
        names = ["Ahmad Khan", "Fatima Noori", "Zahra Ahmadi",
                 "Mohammad Yusuf", "Layla Karimi"]
        for i, name in enumerate(names):
            patient, _ = Patient.objects.get_or_create(
                full_name=name,
                defaults={
                    "gender": "M" if i % 2 == 0 else "F",
                    "date_of_birth": date(1990 + i, 1, 1),
                    "phone": f"070000000{i}",
                    "allergies": "Penicillin" if i == 1 else "",
                },
            )
            Appointment.objects.get_or_create(
                patient=patient,
                start=timezone.now() + timedelta(days=i, hours=1),
                defaults={"doctor": doctor, "reason": "Check-up"},
            )

        self.stdout.write(self.style.SUCCESS(
            "Demo data seeded. Login with admin / Passw0rd! (and others)."
        ))
