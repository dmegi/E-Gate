from django.test import TestCase, override_settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status


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
class AccountsFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        cache.clear()

    def test_admin_register_and_login(self):
        # Register admin
        res = self.client.post(
            "/api/accounts/register/admin/",
            {"username": "admin_test", "password": "pass1234", "email": "a@b.com"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Login admin
        res = self.client.post(
            "/api/accounts/login/admin/",
            {"username": "admin_test", "password": "pass1234"},
            format="json",
        )
        if res.status_code != status.HTTP_200_OK:
            self.fail(f"Admin login failed: {res.status_code} {getattr(res, 'data', None)}")
        tokens = res.data.get("tokens", {})
        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)

    def test_resident_register_and_login(self):
        # Register resident
        res = self.client.post(
            "/api/accounts/register/resident/",
            {
                "username": "res_test",
                "password": "pass1234",
                "address": "Blk 1",
                "birthdate": "2000-01-01",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Login resident
        res = self.client.post(
            "/api/accounts/login/resident/",
            {"username": "res_test", "password": "pass1234"},
            format="json",
        )
        if res.status_code != status.HTTP_200_OK:
            self.fail(f"Resident login failed: {res.status_code} {getattr(res, 'data', None)}")
        tokens = res.data.get("tokens", {})
        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)
