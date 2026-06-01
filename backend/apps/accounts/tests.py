from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User
from apps.patients.models import Patient
from apps.audit.models import ActivityLog


class SecurityTests(APITestCase):
    def setUp(self):
        cache.clear()  # reset throttle counters between tests
        self.role = Role.objects.create(code="ADMIN", name="Admin", permissions=["*"])
        self.user = User.objects.create(username="admin", role=self.role, is_superuser=True)
        self.user.set_password("Secret123!")
        self.user.save()

    def test_successful_login_records_session_and_audit(self):
        r = self.client.post("/api/auth/login/", {"username": "admin", "password": "Secret123!"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertTrue(self.user.sessions.filter(is_active=True).exists())
        self.assertTrue(ActivityLog.objects.filter(action="LOGIN", user=self.user).exists())

    def test_failed_login_is_audited(self):
        r = self.client.post("/api/auth/login/", {"username": "admin", "password": "wrong"}, format="json")
        self.assertEqual(r.status_code, 401)
        self.assertTrue(ActivityLog.objects.filter(action="LOGIN", summary__icontains="Failed").exists())

    def test_login_is_rate_limited(self):
        codes = [
            self.client.post("/api/auth/login/", {"username": "admin", "password": "x"}, format="json").status_code
            for _ in range(12)
        ]
        self.assertIn(429, codes)

    def test_logout_closes_session(self):
        self.client.force_authenticate(self.user)
        self.user.sessions.create(is_active=True)
        self.client.post("/api/auth/me/logout/")
        self.assertFalse(self.user.sessions.filter(is_active=True).exists())
        self.assertIsNotNone(self.user.sessions.first().logout_at)

    def test_upload_rejects_disallowed_extension(self):
        self.client.force_authenticate(self.user)
        bad = SimpleUploadedFile("malware.exe", b"x", content_type="application/octet-stream")
        r = self.client.post("/api/patients/", {"full_name": "Up P", "photo": bad}, format="multipart")
        self.assertEqual(r.status_code, 400)
        self.assertIn("photo", r.json())
