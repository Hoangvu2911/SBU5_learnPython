from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class RegisterTestCase(APITestCase):
    def test_register_success(self):
        res = self.client.post(
            "/api/auth/register/",
            {
                "username": "testuser",
                "password": "testpassword",
                "password_confirm": "testpassword",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn("token", res.data)
        self.assertEqual(res.data["user"]["username"], "testuser")
    
    def test_register_failure_password_mismatch(self):
        res = self.client.post(
            "/api/auth/register/",
            {
                "username": "testuser",
                "password": "testpassword",
                "password_confirm": "mismatchpassword",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("non_field_errors", res.data)
        self.assertEqual(res.data["non_field_errors"][0], "Passwords do not match")

    def test_register_failure_short_password(self):
        res = self.client.post(
            "/api/auth/register/",
            {
                "username": "testuser",
                "password": "short",
                "password_confirm": "short",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("non_field_errors", res.data)
    
    def test_register_failure_existing_username(self):
        self.client.post(
            "/api/auth/register/",
            {
                "username": "testuser",
                "password": "testpassword",
                "password_confirm": "testpassword",
            },
            format="json",
        )
        res = self.client.post(
            "/api/auth/register/",
            {
                "username": "testuser",
                "password": "testpassword",
                "password_confirm": "testpassword",
            }
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("username", res.data)
        self.assertEqual(res.data["username"][0], "Username already exists")

class LoginTestCase(APITestCase):
    def test_login_success(self):
        self.client.post(
            "/api/auth/register/",
            {
                "username": "testuser",
                "password": "testpassword",
                "password_confirm": "testpassword",
            },
            format="json",
        )
        res = self.client.post(
            "/api/auth/login/",
            {
                "username": "testuser",
                "password": "testpassword",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.data)
        self.assertEqual(res.data["user"]["username"], "testuser")

    def test_login_failure_invalid_credentials(self):
        res = self.client.post(
            "/api/auth/register/",
            {
                "username": "testuser",
                "password": "testpassword",
                "password_confirm": "testpassword",
            },
            format="json",
        )
        res = self.client.post(
            "/api/auth/login/",
            {
                "username": "testuser",
                "password": "invalidpassword",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 401)
        self.assertIn("detail", res.data)
        self.assertEqual(res.data["detail"], "Invalid credentials")

class LogoutTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            password="123123",
        )
        self.token = Token.objects.create(user=self.user)

    def test_logout_success(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token.key}",
        )
        res = self.client.post("/api/auth/logout/", format="json")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["detail"], "Logged out.")
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())

    def test_logout_failure_unauthenticated(self):
        res = self.client.post("/api/auth/logout/", format="json")
        self.assertEqual(res.status_code, 401)
        self.assertIn("detail", res.data)
        self.assertEqual(res.data["detail"], "Authentication credentials were not provided.")