import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')  # Replace 'myproject' with your project name

from django.test import TestCase
from rest_framework.test import APIClient
from myapp.models import CustomUser

class CustomUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = "/api/signup/"
        self.login_url = "/api/login/"
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password1": "TestPassword123",
            "password2": "TestPassword123",
        }
        self.existing_user = CustomUser.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            first_name="Existing",
            last_name="User",
            password="ExistingPassword123",
        )

    def test_signup_success(self):
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(CustomUser.objects.count(), 2)  # Including the existing user
        self.assertEqual(CustomUser.objects.last().username, "testuser")

    def test_signup_password_mismatch(self):
        data = self.user_data.copy()
        data["password2"] = "MismatchPassword123"
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Passwords do not match", response.data["non_field_errors"])

    def test_signup_existing_email(self):
        data = self.user_data.copy()
        data["email"] = self.existing_user.email
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_login_success_with_email(self):
        response = self.client.post(
            self.login_url,
            {"identifier": self.existing_user.email, "password": "ExistingPassword123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Login Successful!")

    def test_login_success_with_username(self):
        response = self.client.post(
            self.login_url,
            {"identifier": self.existing_user.username, "password": "ExistingPassword123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Login Successful!")

    def test_login_invalid_password(self):
        response = self.client.post(
            self.login_url,
            {"identifier": self.existing_user.username, "password": "WrongPassword123"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid password.", response.data["non_field_errors"])

    def test_login_non_existent_user(self):
        response = self.client.post(
            self.login_url,
            {"identifier": "nonexistent@example.com", "password": "AnyPassword123"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid username or email.", response.data["non_field_errors"])



