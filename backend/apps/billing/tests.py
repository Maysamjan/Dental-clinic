from decimal import Decimal

from rest_framework.test import APITestCase

from apps.accounts.models import Role, User
from apps.patients.models import Patient


class InvoiceBuilderTests(APITestCase):
    def setUp(self):
        role = Role.objects.create(code="ADMIN", name="Admin", permissions=["*"])
        self.user = User.objects.create(username="admin", role=role, is_superuser=True)
        self.client.force_authenticate(self.user)
        self.patient = Patient.objects.create(full_name="Bill P")

    def test_create_invoice_computes_totals(self):
        payload = {
            "patient": self.patient.id,
            "discount": "200",
            "tax": "0",
            "items": [
                {"description": "Scaling", "quantity": 2, "unit_price": "1500"},
                {"description": "Filling", "quantity": 1, "unit_price": "2000"},
            ],
        }
        r = self.client.post("/api/invoices/", payload, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        body = r.json()
        self.assertEqual(Decimal(body["subtotal"]), Decimal("5000.00"))
        self.assertEqual(Decimal(body["total"]), Decimal("4800.00"))
        self.assertEqual(Decimal(body["balance"]), Decimal("4800.00"))
        self.assertEqual(body["status"], "UNPAID")
        self.assertTrue(body["number"].startswith("INV-"))

    def test_edit_invoice_replaces_items_and_recomputes(self):
        inv = self.client.post("/api/invoices/", {
            "patient": self.patient.id,
            "items": [{"description": "A", "quantity": 1, "unit_price": "1000"}],
        }, format="json").json()
        r = self.client.patch(f"/api/invoices/{inv['id']}/", {
            "items": [{"description": "B", "quantity": 3, "unit_price": "1000"}],
        }, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(Decimal(r.json()["total"]), Decimal("3000.00"))
