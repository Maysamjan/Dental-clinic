from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User
from apps.patients.models import Patient
from apps.appointments.models import Appointment
from apps.visits.models import Visit


class AppointmentWorkflowTests(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(
            code="RECEPTIONIST", name="Receptionist",
            permissions=["appointments.*", "visits.view", "visits.add", "visits.change"],
        )
        self.user = User.objects.create(username="recep", role=self.role)
        self.user.set_password("x")
        self.user.save()
        self.client.force_authenticate(self.user)
        self.patient = Patient.objects.create(full_name="Test Patient")

    def _create_appt(self, **kw):
        data = {
            "patient": self.patient.id,
            "start": (timezone.now() + timedelta(hours=1)).isoformat(),
            "reason": "Check-up",
        }
        data.update(kw)
        return self.client.post("/api/appointments/", data, format="json")

    def test_create_autofills_end(self):
        r = self._create_appt()
        self.assertEqual(r.status_code, 201, r.content)
        self.assertIsNotNone(r.json()["end"])

    def test_reject_past_appointment(self):
        r = self._create_appt(start=(timezone.now() - timedelta(hours=2)).isoformat())
        self.assertEqual(r.status_code, 400)

    def test_arrive_creates_queued_visit(self):
        appt_id = self._create_appt().json()["id"]
        r = self.client.post(f"/api/appointments/{appt_id}/arrive/")
        self.assertEqual(r.status_code, 201, r.content)
        visit = Visit.objects.get(appointment_id=appt_id)
        self.assertEqual(visit.workflow_status, "WAITING")
        self.assertIsNotNone(visit.queue_number)
        self.assertEqual(Appointment.objects.get(id=appt_id).status, "ARRIVED")

        # The visit must appear in the live queue.
        q = self.client.get("/api/visits/queue/")
        self.assertTrue(any(v["id"] == visit.id for v in q.json()))

    def test_arrive_is_idempotent(self):
        appt_id = self._create_appt().json()["id"]
        self.client.post(f"/api/appointments/{appt_id}/arrive/")
        self.client.post(f"/api/appointments/{appt_id}/arrive/")
        self.assertEqual(Visit.objects.filter(appointment_id=appt_id).count(), 1)

    def test_no_double_booking_same_doctor(self):
        from apps.accounts.models import Doctor
        doc = Doctor.objects.create(user=User.objects.create(username="doc1"))
        start = (timezone.now() + timedelta(days=1)).replace(microsecond=0)
        r1 = self._create_appt(doctor=doc.id, start=start.isoformat())
        self.assertEqual(r1.status_code, 201, r1.content)
        r2 = self._create_appt(doctor=doc.id, start=(start + timedelta(minutes=10)).isoformat())
        self.assertEqual(r2.status_code, 400)
