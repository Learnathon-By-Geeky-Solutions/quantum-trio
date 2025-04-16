from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from user_profile.models import UserProfile
from shop_profile.models import MyUser
from my_app.models import District, Upazilla, Area, Division
from unittest.mock import patch
import uuid
from io import BytesIO
from PIL import Image

User = get_user_model()

class UserProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create location data
        self.division = Division.objects.create(name="Dhaka Division")
        self.district = District.objects.create(name="Dhaka", division=self.division)
        self.upazilla = Upazilla.objects.create(name="Mirpur", district=self.district)
        self.area = Area.objects.create(name="Mirpur-10", upazilla=self.upazilla)
        # Create user and profile
        self.user = User.objects.create_user(
            email=f"user_{uuid.uuid4()}@example.com",
            password="Password123!",
            user_type="user"
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            phone_number="1234567890",
            gender="Male",
            user_state=self.district.name,
            user_city=self.upazilla.name,
            user_area=self.area.name
        )

    def test_user_profile_set_password(self):
        """Test UserProfile set_password method."""
        self.profile.set_password("NewPassword123!")
        self.assertTrue(self.profile.check_password("NewPassword123!"))
        self.assertFalse(self.profile.check_password("WrongPassword"))

    def test_user_profile_generate_random_password(self):
        """Test UserProfile generate_random_password method."""
        password = self.profile.generate_random_password(length=8)
        self.assertEqual(len(password), 8)

    @patch('user_profile.views.Upazilla.objects.values')
    @patch('user_profile.views.Area.objects.values')
    def test_addressofbooking_get(self, mock_area_values, mock_upazilla_values):
        """Test GET request to addressofbooking."""
        mock_upazilla_values.return_value.annotate.return_value = [
            {'district__name': 'Dhaka', 'upazilla_names': ['Mirpur', 'Dhanmondi']}
        ]
        mock_area_values.return_value.annotate.return_value = [
            {'upazilla__name': 'Mirpur', 'area_names': ['Mirpur-10']}
        ]
        response = self.client.get(reverse("addressofbooking"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("district" in response.context)
        self.assertTrue("Upazilla" in response.context)
        self.assertTrue("Area" in response.context)

    def test_addressofbooking_post_not_allowed(self):
        """Test POST to addressofbooking returns 302."""
        response = self.client.post(reverse("addressofbooking"))
        self.assertEqual(response.status_code, 302)

    def test_reviews_get(self):
        """Test GET request to reviews."""
        response = self.client.get(reverse("myreviews"))
        self.assertEqual(response.status_code, 302)

    def test_myreviews_get(self):
        """Test GET request to myreviews."""
        response = self.client.get(reverse("myreviews"))
        self.assertEqual(response.status_code, 302)

    def test_mybooking_get(self):
        """Test GET request to mybooking."""
        response = self.client.get(reverse("mybooking"))
        self.assertEqual(response.status_code, 302)

    def test_mycancellations_get(self):
        """Test GET request to mycancellations."""
        response = self.client.get(reverse("mycancellations"))
        self.assertEqual(response.status_code, 302)

    def test_mynotifications_get(self):
        """Test GET request to mynotifications."""
        response = self.client.get(reverse("mynotifications"))
        self.assertEqual(response.status_code, 302)

    def test_mymessage_get(self):
        """Test GET request to mymessage."""
        response = self.client.get(reverse("mymessage"))
        self.assertEqual(response.status_code, 302)
 