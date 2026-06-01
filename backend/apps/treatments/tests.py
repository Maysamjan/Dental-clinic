from decimal import Decimal

from rest_framework.test import APITestCase

from apps.accounts.models import Role, User
from apps.patients.models import Patient
from apps.treatments.models import TreatmentPlan, TreatmentStage, Treatment


class TreatmentPlanTests(APITestCase):
    def setUp(self):
        role = Role.objects.create(code="ADMIN", name="Admin", permissions=["*"])
        self.user = User.objects.create(username="admin", role=role, is_superuser=True)
        self.client.force_authenticate(self.user)
        self.patient = Patient.objects.create(full_name="Plan P")
        self.plan = TreatmentPlan.objects.create(patient=self.patient, title="Rehab", status="ACTIVE")
        self.stage = TreatmentStage.objects.create(plan=self.plan, name="Stage 1", order=1)

    def test_progress_recomputes_on_status_change(self):
        t1 = Treatment.objects.create(stage=self.stage, description="A", unit_price=Decimal("100"))
        Treatment.objects.create(stage=self.stage, description="B", unit_price=Decimal("100"))
        r = self.client.patch(f"/api/treatments/{t1.id}/", {"status": "COMPLETED"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.plan.refresh_from_db()
        self.assertEqual(self.plan.progress_percent, 50)

    def test_generate_invoice_from_completed(self):
        Treatment.objects.create(stage=self.stage, description="Crown", quantity=1,
                                 unit_price=Decimal("8000"), status="COMPLETED")
        Treatment.objects.create(stage=self.stage, description="Pending", unit_price=Decimal("500"))
        r = self.client.post(f"/api/treatment-plans/{self.plan.id}/generate-invoice/")
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(Decimal(r.json()["total"]), Decimal("8000.00"))

        # Re-generating must not double-bill the same treatment.
        r2 = self.client.post(f"/api/treatment-plans/{self.plan.id}/generate-invoice/")
        self.assertEqual(r2.status_code, 400)
