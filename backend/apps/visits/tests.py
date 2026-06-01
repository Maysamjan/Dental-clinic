from rest_framework.test import APITestCase

from apps.accounts.models import Role, User, Doctor
from apps.patients.models import Patient
from apps.visits.models import Visit


class ConsultationTests(APITestCase):
    def setUp(self):
        role = Role.objects.create(code="DOCTOR", name="Doctor", permissions=["visits.*"])
        self.user = User.objects.create(username="doc", role=role)
        Doctor.objects.create(user=self.user)
        self.client.force_authenticate(self.user)
        self.patient = Patient.objects.create(full_name="P")
        self.visit = Visit.objects.create(patient=self.patient, workflow_status="WAITING", queue_number=1)

    def test_update_clinical_fields(self):
        r = self.client.patch(f"/api/visits/{self.visit.id}/", {"diagnosis": "Caries 16"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.visit.refresh_from_db()
        self.assertEqual(self.visit.diagnosis, "Caries 16")

    def test_valid_status_advance(self):
        r = self.client.post(f"/api/visits/{self.visit.id}/advance/", {"status": "IN_CONSULTATION"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.visit.refresh_from_db()
        self.assertEqual(self.visit.workflow_status, "IN_CONSULTATION")

    def test_invalid_status_advance_rejected(self):
        # Cannot jump straight from WAITING to COMPLETED.
        r = self.client.post(f"/api/visits/{self.visit.id}/advance/", {"status": "COMPLETED"}, format="json")
        self.assertEqual(r.status_code, 400)
