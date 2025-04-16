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
    # def test_customer_register_step2_get(self):
    #     """Test GET request to customer_register_step2."""
    #     response = self.client.get(reverse("step2"))
    #     self.assertEqual(response.status_code, 200)
