from datetime import date, timedelta

from rest_framework.test import APITestCase

from apps.accounts.models import Role, User
from apps.patients.models import Patient
from apps.inventory.models import InventoryItem
from apps.expenses.models import ExpenseCategory


class ValidationTests(APITestCase):
    def setUp(self):
        role = Role.objects.create(code="ADMIN", name="Admin", permissions=["*"])
        self.user = User.objects.create(username="admin", role=role, is_superuser=True)
        self.client.force_authenticate(self.user)

    def test_future_dob_rejected(self):
        future = (date.today() + timedelta(days=1)).isoformat()
        r = self.client.post("/api/patients/", {"full_name": "X", "date_of_birth": future}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("date_of_birth", r.json())

    def test_expense_amount_must_be_positive(self):
        cat = ExpenseCategory.objects.create(name="Rent")
        r = self.client.post("/api/expenses/", {"category": cat.id, "amount": "0", "date": date.today().isoformat()}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_stock_out_cannot_exceed_quantity(self):
        item = InventoryItem.objects.create(name="Gloves", quantity=5, minimum_stock=2)
        r = self.client.post("/api/inventory-transactions/", {"item": item.id, "type": "OUT", "quantity": "10"}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("quantity", r.json())

    def test_404_returns_clean_detail(self):
        r = self.client.get("/api/patients/999999/")
        self.assertEqual(r.status_code, 404)
        self.assertIn("detail", r.json())
