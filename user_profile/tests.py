from django.test import TestCase, Client
from django.urls import reverse
from shop_profile.models import MyUser
from user_profile.models import UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
import uuid

TEST_PASS = "pass"

class UserProfileTests(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create_user(
            email=f"test_{uuid.uuid4()}@example.com",
            password=TEST_PASS  
        )
        self.profile = UserProfile.objects.create(
            user=self.user, first_name="Test", last_name="User"
        )
        self.client = Client()
        self.client.force_login(self.user)

    def test_get_profile_page(self):
        url = reverse("user")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Profile")

    def test_update_profile_email_conflict(self):
        conflict_email = f"conflict_{uuid.uuid4()}@example.com"
        MyUser.objects.create_user(
            email= conflict_email,
            password=TEST_PASS  
        )
        url = reverse("user")
        data = {
            "email": conflict_email,
            "first_name": "X",
            "last_name": "Y",
        }
        response = self.client.post(url, data)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("email is already in use" in str(message) for message in messages)
        )

    def test_update_profile_password_mismatch(self):
        url = reverse("user")
        data = {
            "password": "pass1",
            "retype_password": "pass2",
        }
        response = self.client.post(url, data)
        self.assertContains(response, "Passwords do not match")