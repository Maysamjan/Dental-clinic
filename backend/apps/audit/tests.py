from rest_framework.test import APITestCase

from apps.accounts.models import Role, User, Doctor
from apps.patients.models import Patient
from apps.audit.models import ActivityLog


class AuditCoverageTests(APITestCase):
    def setUp(self):
        role = Role.objects.create(code="ADMIN", name="Admin", permissions=["*"])
        self.user = User.objects.create(username="admin", role=role, is_superuser=True)
        self.doctor = Doctor.objects.create(user=self.user)
        self.client.force_authenticate(self.user)
        self.patient = Patient.objects.create(full_name="Audit P")

    def test_prescription_create_is_audited(self):
        self.client.post("/api/prescriptions/", {
            "patient": self.patient.id, "doctor": self.doctor.id,
            "items": [{"medication": "Amox", "dosage": "1", "frequency": "TID", "duration": "5d"}],
        }, format="json")
        self.assertTrue(
            ActivityLog.objects.filter(entity="Prescription", action="CREATE", user=self.user).exists()
        )

    def test_treatment_plan_create_is_audited(self):
        self.client.post("/api/treatment-plans/", {"patient": self.patient.id, "title": "Plan"}, format="json")
        self.assertTrue(ActivityLog.objects.filter(entity="Treatment Plan", action="CREATE").exists())
