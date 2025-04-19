from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from user_profile.models import UserProfile
from shop_profile.models import MyUser
from my_app.models import District, Upazilla, Area, Division
import uuid

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

    def test_user_profile_set_password1(self):
        """Test UserProfile set_password method."""
        self.profile.set_password("NewPassword124!")
        self.assertTrue(self.profile.check_password("NewPassword124!"))
        self.assertFalse(self.profile.check_password("WrongPassword"))

    def test_user_profile_set_password2(self):
        """Test UserProfile set_password method."""
        self.profile.set_password("NewPassword1!")
        self.assertTrue(self.profile.check_password("NewPassword1!"))
        self.assertFalse(self.profile.check_password("WrongPassword"))

    def test_user_profile_set_password3(self):
        """Test UserProfile set_password method."""
        self.profile.set_password("NewPassord124!")
        self.assertTrue(self.profile.check_password("NewPassord124!"))
        self.assertFalse(self.profile.check_password("WrongPassword"))

    def test_user_profile_set_password4(self):
        """Test UserProfile set_password method."""
        self.profile.set_password("NewPassord1244!")
        self.assertTrue(self.profile.check_password("NewPassord1244!"))
        self.assertFalse(self.profile.check_password("WrongPassword"))

    def test_user_profile_set_password5(self):
        """Test UserProfile set_password method."""
        self.profile.set_password("NewPassord1245!")
        self.assertTrue(self.profile.check_password("NewPassord1245!"))
        self.assertFalse(self.profile.check_password("WrongPassword"))

    def test_user_profile_set_password6(self):
        """Test UserProfile set_password method."""
        self.profile.set_password("NewPassord11245!")
        self.assertTrue(self.profile.check_password("NewPassord11245!"))
        self.assertFalse(self.profile.check_password("WrongPassword"))

    def test_user_profile_set_password8(self):
        """Test UserProfile set_password method."""
        self.profile.set_password("NewPassord1124533!")
        self.assertTrue(self.profile.check_password("NewPassord1124533!"))
        self.assertFalse(self.profile.check_password("WrongPassword"))

    def test_user_profile_set_password9(self):
        """Test UserProfile set_password method."""
        self.profile.set_password("NewPassord1124544!")
        self.assertTrue(self.profile.check_password("NewPassord1124544!"))
        self.assertFalse(self.profile.check_password("WrongPassword"))

    def test_user_profile_generate_random_password(self):
        """Test UserProfile generate_random_password method."""
        password = self.profile.generate_random_password(length=8)
        self.assertEqual(len(password), 8)
    
    def test_user_profile_generate_random_password1(self):
        """Test UserProfile generate_random_password method."""
        password = self.profile.generate_random_password(length=9)
        self.assertEqual(len(password), 9)

    def test_mynotifications_get(self):
        """Test GET request to mynotifications."""
        self.client.login(email=self.user.email, password="Password123!")
        response = self.client.get(reverse("mynotifications"))
        self.assertEqual(response.status_code, 200)

    def test_myreviews_get(self):
        """Test GET request to myreviews."""
        self.client.login(email=self.user.email, password="Password123!")
        response = self.client.get(reverse("myreviews"))
        self.assertEqual(response.status_code, 200)
