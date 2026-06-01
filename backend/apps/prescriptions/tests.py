from rest_framework.test import APITestCase

from apps.accounts.models import Role, User, Doctor
from apps.patients.models import Patient


class PrescriptionTests(APITestCase):
    def setUp(self):
        role = Role.objects.create(code="DOCTOR", name="Doctor", permissions=["prescriptions.*"])
        self.user = User.objects.create(username="doc", full_name="Jane Doe", role=role)
        self.doctor = Doctor.objects.create(user=self.user, license_number="DEN-123")
        self.client.force_authenticate(self.user)
        self.patient = Patient.objects.create(full_name="Rx P")

    def test_create_with_items_and_pdf(self):
        payload = {
            "patient": self.patient.id,
            "doctor": self.doctor.id,
            "notes": "After meals",
            "items": [
                {"medication": "Amoxicillin 500mg", "dosage": "1 cap", "frequency": "TID", "duration": "5 days", "notes": ""},
                {"medication": "Ibuprofen 400mg", "dosage": "1 tab", "frequency": "BID", "duration": "3 days", "notes": "PRN"},
            ],
        }
        r = self.client.post("/api/prescriptions/", payload, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        rx_id = r.json()["id"]
        self.assertEqual(len(r.json()["items"]), 2)

        pdf = self.client.get(f"/api/prescriptions/{rx_id}/pdf/")
        self.assertEqual(pdf.status_code, 200)
        self.assertEqual(pdf["Content-Type"], "application/pdf")
        self.assertTrue(pdf.content[:4] == b"%PDF")
