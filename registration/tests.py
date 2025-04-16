from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from my_app.models import District, Upazilla, Area, Service, Item, Division
from shop_profile.models import MyUser, ShopProfile, ShopWorker, ShopService, ShopSchedule
from user_profile.models import UserProfile
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

    def test_customer_register_step2_post_existing_email(self):
        """Test POST to customer_register_step2 with existing email."""
        User.objects.create_user(
            email="existing@example.com",
            password="test",
            user_type="user"  # Fixed typo: was user_type-rel
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
   