from decimal import Decimal

from rest_framework.test import APITestCase

from apps.accounts.models import Role, User
from apps.patients.models import Patient
from apps.billing.models import Invoice, InvoiceItem, Payment


class PatientHistoryTests(APITestCase):
    def setUp(self):
        role = Role.objects.create(code="ADMIN", name="Admin", permissions=["*"])
        self.user = User.objects.create(username="admin", role=role, is_superuser=True)
        self.client.force_authenticate(self.user)
        self.patient = Patient.objects.create(full_name="History P", allergies="Penicillin")

    def test_history_aggregates_financials(self):
        inv = Invoice.objects.create(patient=self.patient)
        InvoiceItem.objects.create(invoice=inv, description="Scaling", quantity=1, unit_price=Decimal("1000"))
        inv.recompute()
        Payment.objects.create(invoice=inv, amount=Decimal("400"), method="CASH")

        r = self.client.get(f"/api/patients/{self.patient.id}/history/")
        self.assertEqual(r.status_code, 200, r.content)
        body = r.json()
        for key in ["financial_summary", "visits", "treatment_plans", "prescriptions",
                    "invoices", "payments", "documents", "follow_ups"]:
            self.assertIn(key, body)
        self.assertEqual(Decimal(body["financial_summary"]["total_billed"]), Decimal("1000.00"))
        self.assertEqual(Decimal(body["financial_summary"]["total_paid"]), Decimal("400.00"))
        self.assertEqual(Decimal(body["financial_summary"]["outstanding_balance"]), Decimal("600.00"))

    def test_archive_restore(self):
        r = self.client.post(f"/api/patients/{self.patient.id}/archive/")
        self.assertEqual(r.status_code, 200)
        self.patient.refresh_from_db()
        self.assertTrue(self.patient.is_archived)
        self.client.post(f"/api/patients/{self.patient.id}/restore/")
        self.patient.refresh_from_db()
        self.assertFalse(self.patient.is_archived)
