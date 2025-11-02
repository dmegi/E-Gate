from django.test import TestCase, override_settings
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_simplejwt.authentication.JWTAuthentication',
        ),
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 20,
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {'user': '10000/min', 'anon': '10000/min'},
    }
)
class EventsFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        cache.clear()
        User = get_user_model()
        # Create admin via endpoint to match serializers/permissions
        self.client.post(
            "/api/accounts/register/admin/",
            {"username": "admin_flow", "password": "pass1234"},
            format="json",
        )
        login = self.client.post(
            "/api/accounts/login/admin/",
            {"username": "admin_flow", "password": "pass1234"},
            format="json",
        )
        if login.status_code != status.HTTP_200_OK:
            self.fail(f"Admin login failed: {login.status_code} {getattr(login, 'data', None)}")
        self.admin_token = login.data["tokens"]["access"]

        # Create a resident
        self.client.post(
            "/api/accounts/register/resident/",
            {
                "username": "res_flow",
                "password": "pass1234",
                "address": "Blk 1",
                "birthdate": "2000-01-01",
            },
            format="json",
        )
        rlogin = self.client.post(
            "/api/accounts/login/resident/",
            {"username": "res_flow", "password": "pass1234"},
            format="json",
        )
        if rlogin.status_code != status.HTTP_200_OK:
            self.fail(f"Resident login failed: {rlogin.status_code} {getattr(rlogin, 'data', None)}")
        self.res_token = rlogin.data["tokens"]["access"]

    def auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_event_create_register_attendance_unreg(self):
        # Admin creates an event
        self.auth(self.admin_token)
        payload = {
            "title": "Clinic Day",
            "event_type": "community",
            "date": (timezone.now() + timedelta(days=2)).isoformat(),
            "venue": "Hall",
            "capacity": 10,
            "registration_open": (timezone.now() + timedelta(days=1)).isoformat(),
            "registration_close": (timezone.now() + timedelta(days=2)).isoformat(),
        }
        res = self.client.post("/api/events/create/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        event_id = res.data["id"]

        # Move open window to now for registration
        patch = {"registration_open": (timezone.now() - timedelta(minutes=1)).isoformat()}
        res = self.client.put(f"/api/events/update/{event_id}/", patch, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Resident registers
        self.auth(self.res_token)
        res = self.client.post(f"/api/events/{event_id}/register/")
        self.assertIn(res.status_code, (status.HTTP_201_CREATED, status.HTTP_200_OK))

        # Get resident barangay_id for attendance mark
        p = self.client.get("/api/residents/profile/")
        self.assertEqual(p.status_code, status.HTTP_200_OK)
        barangay_id = p.data["barangay_id"]

        # Admin marks attendance
        self.auth(self.admin_token)
        res = self.client.post(
            "/api/events/attendance/mark/",
            {"barangay_id": barangay_id, "event_id": event_id},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Resident cannot unregister after check-in
        self.auth(self.res_token)
        res = self.client.post(f"/api/events/{event_id}/unregister/")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
