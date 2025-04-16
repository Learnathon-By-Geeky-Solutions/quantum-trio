from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from my_app.models import District, Upazilla, Area, Service, Item, Division
from shop_profile.models import MyUser, ShopProfile, ShopWorker, ShopService, ShopSchedule
from user_profile.models import UserProfile
from unittest.mock import patch

import uuid

User = get_user_model()

class RegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create location data
        self.division = Division.objects.create(name="Dhaka Division")
        self.district = District.objects.create(name="Dhaka", division=self.division)
        self.upazilla = Upazilla.objects.create(name="Mirpur", district=self.district)
        self.area = Area.objects.create(name="Mirpur-10", upazilla=self.upazilla)
        # Create service and item
        self.service = Service.objects.create(name="Haircare")
        self.item = Item.objects.create(
            name="Haircut",
            service=self.service,
            gender="Both",
            item_description="Standard haircut"
        )

    def test_select_user_type(self):
        """Test GET request to select_user_type."""
        response = self.client.get(reverse("select_user_type"))
        self.assertEqual(response.status_code, 200)

    def test_customer_register_step1_get(self):
        """Test GET request to customer_register_step1."""
        response = self.client.get(reverse("customer_register_step1"))
        self.assertEqual(response.status_code, 200)

    def test_customer_register_step2_post_existing_email(self):
        """Test POST to customer_register_step2 with existing email."""
        User.objects.create_user(
            email="existing@example.com",
            password="test",
            user_type="user"
        )
        data = {
            "first-name": "Jane",
            "last-name": "Doe",
            "email": "existing@example.com",
            "password": "Password123!",
            "mobile-number": "1234567890",
            "gender": "Female"
        }
        response = self.client.post(reverse("step2"), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get("message", ""), "The email exist.")

    def test_business_register_step1_get(self):
        """Test GET request to business_register_step1."""
        response = self.client.get(reverse("business_register_step1"))
        self.assertEqual(response.status_code, 200)

    def test_business_register_step2_post_valid(self):
        """Test POST to business_register_step2 with valid data."""
        data = {
            "first-name": "Jane",
            "last-name": "Smith",
            "email": f"jane_{uuid.uuid4()}@example.com",
            "password": "Password123!",
            "mobile-number": "9876543210"
        }
        response = self.client.post(reverse("business_register_step2"), data)
        self.assertEqual(response.status_code, 200)
        session_user = self.client.session.get("user", {})
        self.assertEqual(session_user.get("first-name"), "Jane")
        self.assertEqual(session_user.get("email"), data["email"])

    @patch('registration.views.Upazilla.objects.values')
    def test_customer_register_step2_get(self, mock_upazilla_values):
        """Test GET request to customer_register_step2."""
        mock_upazilla_values.return_value.annotate.return_value = [
            {'district__name': 'Dhaka', 'upazilla_names': ['Mirpur', 'Dhanmondi']}
        ]
        response = self.client.get(reverse("step2"))
        self.assertEqual(response.status_code, 200)

    @patch('registration.views.Upazilla.objects.values')
    def test_customer_register_step2_post_valid(self, mock_upazilla_values):
        """Test POST to customer_register_step2 with valid data."""
        mock_upazilla_values.return_value.annotate.return_value = [
            {'district__name': 'Dhaka', 'upazilla_names': ['Mirpur', 'Dhanmondi']}
        ]
        data = {
            "first-name": "John",
            "last-name": "Doe",
            "email": f"john_{uuid.uuid4()}@example.com",
            "password": "Password123!",
            "mobile-number": "1234567890",
            "gender": "Male"
        }
        response = self.client.post(reverse("step2"), data)
        self.assertEqual(response.status_code, 200)
        session_user = self.client.session.get("user", {})
        self.assertEqual(session_user.get("first-name"), "John")
        self.assertEqual(session_user.get("email"), data["email"])

    @patch('registration.views.Item.objects.values')
    def test_business_register_step5_post(self, mock_item_values):
        """Test POST to business_register_step5."""
        email = f"jane_{uuid.uuid4()}@example.com"
        self.client.session["user"] = {
            "email": email
        }
        self.client.session.modified = True
        mock_item_values.return_value.annotate.return_value = [
            {'service__id': 1, 'service__name': 'Haircare', 'service_names': ['Haircut']}
        ]
        data = {
            "services[]": ["1"]
        }
        response = self.client.post(reverse("business_register_step5"), data)
        self.assertEqual(response.status_code, 200)
        session_user = self.client.session.get("user", {})
        self.assertEqual(session_user.get("services", []), ["1"])

