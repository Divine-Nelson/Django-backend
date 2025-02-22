#import os
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')  # Replace 'myproject' with your project name

from django.test import TestCase
from rest_framework.test import APIClient, force_authenticate
from rest_framework.test import APIClient
from myapp.models import CustomUser

class CustomUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = "/api/signup/"
        self.login_url = "/api/login/"
        self.reset_password_url = "/api/reset_password/"
        self.user_data_url = "/api/userDetails/"  # Ensure the leading slash is present

        self.create_user_url="api/create-payment/"
        self.call_back_url ="api/callback-payment/"
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
        self.reset_test = {
            "email": "",
        }

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

    def test_reset_success(self):
        response = self.client.post(
            self.reset_password_url,
            {"email": self.existing_user.email},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "If this email exists, a reset link has been sent.")

    def test_reset_invalid_email(self):
        response = self.client.post(
            self.reset_password_url,
            {"email": ""},
        )
        self.assertEqual(response.status_code, 400)

    def test_reset_nonexisting(self):
        response = self.client.post(
            self.reset_password_url,
            {"email": "nonexistent@example.com"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "If this email exists, a reset link has been sent.")

    def test_user_details_view(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.existing_user)
        
        # Send a GET request to the user details endpoint
        response = self.client.get(self.user_data_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["initials"], "EU")  # Based on 'Existing User'
        self.assertEqual(response.data["full_name"], "Existing User")
        self.assertEqual(response.data["email"], "existing@example.com")


    