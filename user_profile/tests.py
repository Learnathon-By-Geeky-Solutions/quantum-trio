from django.test import TestCase

# Create your tests here.
import pytest
from django.urls import reverse
from shop_profile.models import MyUser
from user_profile.models import UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages

@pytest.fixture
def user_with_profile(db):
    user = MyUser.objects.create_user(email="test@example.com", password="strongpassword123")
    profile = UserProfile.objects.create(user=user, first_name="Test", last_name="User")
    return user, profile

@pytest.fixture
def client_logged_in(client, user_with_profile):
    user, _ = user_with_profile
    client.force_login(user)
    return client, user

@pytest.mark.django_db
def test_get_profile_page(client_logged_in):
    client, _ = client_logged_in
    url = reverse("user")
    response = client.get(url)
    assert response.status_code == 200
    assert b"My Profile" in response.content  # or a string you know appears in the template


# ✅ Test email already exists
@pytest.mark.django_db
def test_update_profile_email_conflict(client_logged_in):
    MyUser.objects.create_user(email="existing@example.com", password="anotherpass")

    client, user = client_logged_in
    url = reverse("user")
    data = {
        "email": "existing@example.com",  # this email already taken
        "first_name": "X",
        "last_name": "Y",
    }
    response = client.post(url, data)

    # Check if the flash message was added
    messages = list(get_messages(response.wsgi_request))
    assert any("email is already in use" in str(message) for message in messages)

# ✅ Test password mismatch
def test_update_profile_password_mismatch(client_logged_in):
    client, user = client_logged_in
    url = reverse("user")
    data = {
        "password": "pass123",
        "retype_password": "wrongpass123",
    }
    response = client.post(url, data)
    assert b"Passwords do not match" in response.content


