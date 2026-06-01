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

    def _invoice(self, **kw):
        payload = {
            "patient": self.patient.id,
            "items": [{"description": "Scaling", "quantity": 2, "unit_price": "1500"}],
        }
        payload.update(kw)
        return self.client.post("/api/invoices/", payload, format="json").json()

    def test_create_invoice_computes_totals(self):
        body = self._invoice(discount="200")
        self.assertEqual(Decimal(body["subtotal"]), Decimal("3000.00"))
        self.assertEqual(Decimal(body["total"]), Decimal("2800.00"))
        self.assertEqual(body["status"], "UNPAID")
        self.assertTrue(body["number"].startswith("INV-"))

    def test_edit_invoice_replaces_items_and_recomputes(self):
        inv = self._invoice()
        r = self.client.patch(f"/api/invoices/{inv['id']}/", {
            "items": [{"description": "B", "quantity": 3, "unit_price": "1000"}],
        }, format="json")
        self.assertEqual(Decimal(r.json()["total"]), Decimal("3000.00"))


class PaymentTests(APITestCase):
    def setUp(self):
        role = Role.objects.create(code="ADMIN", name="Admin", permissions=["*"])
        self.user = User.objects.create(username="admin", role=role, is_superuser=True)
        self.client.force_authenticate(self.user)
        self.patient = Patient.objects.create(full_name="Pay P")
        self.inv = self.client.post("/api/invoices/", {
            "patient": self.patient.id,
            "items": [{"description": "Crown", "quantity": 1, "unit_price": "5000"}],
        }, format="json").json()

    def test_partial_then_full_payment_updates_status(self):
        r = self.client.post("/api/payments/", {"invoice": self.inv["id"], "amount": "2000", "method": "CASH"}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        inv = self.client.get(f"/api/invoices/{self.inv['id']}/").json()
        self.assertEqual(inv["status"], "PARTIAL")
        self.assertEqual(Decimal(inv["balance"]), Decimal("3000.00"))

        self.client.post("/api/payments/", {"invoice": self.inv["id"], "amount": "3000", "method": "CASH"}, format="json")
        inv = self.client.get(f"/api/invoices/{self.inv['id']}/").json()
        self.assertEqual(inv["status"], "PAID")

    def test_overpayment_rejected(self):
        r = self.client.post("/api/payments/", {"invoice": self.inv["id"], "amount": "6000", "method": "CASH"}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_zero_payment_rejected(self):
        r = self.client.post("/api/payments/", {"invoice": self.inv["id"], "amount": "0", "method": "CASH"}, format="json")
        self.assertEqual(r.status_code, 400)
