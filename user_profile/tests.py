from django.test import TestCase, Client
from django.urls import reverse
from shop_profile.models import MyUser
from user_profile.models import UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
import uuid

TEST_PASS = "pass"
RETYPE_TEST_PASS ="pass1"
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


    

        