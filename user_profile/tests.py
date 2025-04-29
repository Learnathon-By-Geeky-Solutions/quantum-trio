from django.http import JsonResponse
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from user_profile.models import UserProfile
from shop_profile.models import MyUser, ShopProfile, ShopWorker
from my_app.models import Division, District, Upazilla, Area, Item, Service
from booking.models import BookingSlot
from decimal import Decimal
from datetime import datetime, date, time, timedelta
import json
from unittest.mock import patch, MagicMock

UserModel = get_user_model()

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create(email="test@example.com")
        self.profile = UserProfile.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            gender="Male",
            phone_number="1234567890",
            user_state="State",
            user_city="City",
            user_area="Area",
            latitude=12.34,
            longitude=56.78,
            date_of_birth=date(1990, 1, 1),
            is_active=True,
            is_staff=False,
            is_superuser=False
        )

    def test_str_method(self):
        self.assertEqual(str(self.profile), "test@example.com")

    def test_set_password(self):
        raw_password = "mypassword"
        self.profile.set_password(raw_password)
        self.assertTrue(self.profile.check_password(raw_password))

    def test_check_password_invalid(self):
        self.profile.set_password("mypassword")
        self.assertFalse(self.profile.check_password("wrongpassword"))

    def test_generate_random_password(self):
        password = self.profile.generate_random_password(length=12)
        self.assertEqual(len(password), 12)
        self.assertIsInstance(password, str)

    def test_field_validations(self):
        self.assertEqual(self.profile.first_name, "John")
        self.assertEqual(self.profile.gender, "Male")
        self.assertEqual(self.profile.latitude, 12.34)
        self.assertTrue(self.profile.is_active)
        self.assertFalse(self.profile.is_superuser)

    def test_profile_picture_upload(self):
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        self.profile.profile_picture = image
        self.profile.save()
        self.assertTrue(self.profile.profile_picture.name.startswith("profile_pictures/test"))

class UserProfileViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = MyUser.objects.create(email="test@example.com")
        self.user.set_password("password123")
        self.user.save()
        self.profile = UserProfile.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            phone_number="1234567890"
        )
        self.shop_user = MyUser.objects.create(email="shop@example.com", user_type="shop")
        self.shop = ShopProfile.objects.create(
            user=self.shop_user,
            shop_name="Test Shop",
            shop_owner="Shop Owner",
            mobile_number="0987654321"
        )
        self.client.login(email="test@example.com", password="password123")

    def test_profile_view_get(self):
        response = self.client.get(reverse("user"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/customer_profile/my-profile.html")
        self.assertIn("user", response.context)
        self.assertIn("profile", response.context)

    def test_profile_view_post_valid(self):
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "test@example.com",
            "mobile_number": "0987654321",
            "password": "",
            "retype_password": ""
        }
        response = self.client.post(reverse("user"), data)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.first_name, "Jane")
        self.assertEqual(self.profile.phone_number, "0987654321")
        self.assertContains(response, "Profile updated successfully")

    def test_profile_view_post_invalid_email(self):
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "invalid-email",
            "mobile_number": "0987654321"
        }
        response = self.client.post(reverse("user"), data)
        self.assertContains(response, "Please enter a valid email address")
        self.assertTemplateUsed(response, "app/customer_profile/my-profile.html")

    def test_profile_view_post_email_in_use(self):
        MyUser.objects.create(email="other@example.com")
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "other@example.com",
            "mobile_number": "0987654321"
        }
        response = self.client.post(reverse("user"), data)
        self.assertContains(response, "This email is already in use")

    def test_profile_view_post_password_mismatch(self):
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "test@example.com",
            "password": "newpassword",
            "retype_password": "differentpassword",
            "mobile_number": "0987654321"
        }
        response = self.client.post(reverse("user"), data)
        self.assertContains(response, "Passwords do not match")

    def test_profile_view_post_with_image(self):
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "test@example.com",
            "mobile_number": "0987654321",
            "image": image
        }
        response = self.client.post(reverse("user"), data)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.profile_picture.name.startswith("profile_pictures/test"))

    # def test_profile_view_unauthenticated(self):
    #     self.client.logout()
    #     response = self.client.get(reverse("user"))
    #     self.assertEqual(response.status_code, 302)
    #     self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_myreviews_view(self):
        response = self.client.get(reverse("myreviews"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/customer_profile/myreviews.html")

    @patch("user_profile.views.imported_booking_details")
    def test_booking_details_view(self, mock_booking_details):
        mock_booking_details.return_value = JsonResponse({"success": True})
        data = {"booking_id": 1}
        response = self.client.post(reverse("booking_details"), json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

    @patch("user_profile.views.imported_reject_booking")
    def test_reject_booking_view(self, mock_reject_booking):
        mock_reject_booking.return_value = JsonResponse({"success": True})
        data = {"booking_id": 1}
        response = self.client.post(reverse("reject_booking"), json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

    def test_update_status_view_past_booking(self):
        service = Service.objects.create(name="TestService")
        item = Item.objects.create(name="TestItem", service=service)
        worker = ShopWorker.objects.create(
            name="Test Worker",
            email="worker@example.com",
            phone="1234567890",
            experience=5.0,
            shop=self.shop,
            rating=0.0
        )
        booking = BookingSlot.objects.create(
            user=self.profile,
            shop=self.shop,
            worker=worker,
            item=item,
            date=date.today() - timedelta(days=1),
            time=(timezone.now() - timedelta(hours=1)).time(),
            status="confirmed"
        )
        data = {"booking_id": booking.id}
        response = self.client.post(reverse("update-status"), json.dumps(data), content_type="application/json")
        booking.refresh_from_db()
        self.assertTrue(booking.user_end)
        self.assertJSONEqual(response.content, {
            "success": True,
            "details": {"message": "You have successfully marked as completed!"}
        })

    def test_update_status_view_future_booking(self):
        service = Service.objects.create(name="TestService")
        item = Item.objects.create(name="TestItem", service=service)
        worker = ShopWorker.objects.create(
            name="Test Worker",
            email="worker@example.com",
            phone="1234567890",
            experience=5.0,
            shop=self.shop,
            rating=0.0
        )
        booking = BookingSlot.objects.create(
            user=self.profile,
            shop=self.shop,
            worker=worker,
            item=item,
            date=date.today() + timedelta(days=1),
            time=timezone.now().time(),
            status="confirmed"
        )
        data = {"booking_id": booking.id}
        response = self.client.post(reverse("update-status"), json.dumps(data), content_type="application/json")
        self.assertJSONEqual(response.content, {
            "success": False,
            "message": "The booking time has not yet arrived."
        })

    def test_update_status_view_invalid_booking(self):
        data = {"booking_id": 999}
        response = self.client.post(reverse("update-status"), json.dumps(data), content_type="application/json")
        self.assertJSONEqual(response.content, {
            "success": False,
            "message": "Booking not found."
        })

    def test_mycancellations_view(self):
        service = Service.objects.create(name="TestService")
        item = Item.objects.create(name="TestItem", service=service)
        worker = ShopWorker.objects.create(
            name="Test Worker",
            email="worker@example.com",
            phone="1234567890",
            experience=5.0,
            shop=self.shop,
            rating=0.0
        )
        BookingSlot.objects.create(
            user=self.profile,
            shop=self.shop,
            worker=worker,
            item=item,
            date=date.today(),
            time=timezone.now().time(),
            status="canceled"
        )
        response = self.client.get(reverse("mycancellations"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/customer_profile/mycancellations.html")
        self.assertIn("booking", response.context)

    def test_mynotifications_view(self):
        response = self.client.get(reverse("mynotifications"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/customer_profile/mynotifications.html")

    def test_mymessage_view(self):
        response = self.client.get(reverse("mymessage"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/customer_profile/mymessage.html")

    # def test_views_require_login(self):
    #     self.client.logout()
    #     urls = [
    #         "user", "addressofbooking", "myreviews", "mybooking",
    #         "booking_details", "reject_booking", "update-status",
    #         "mycancellations", "mynotifications", "mymessage"
    #     ]
    #     for url_name in urls:
    #         response = self.client.get(reverse(url_name))
    #         self.assertEqual(response.status_code, 302)
    #         self.assertTrue(response.url.startswith("/accounts/login/"))


class TargetedUserProfileViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = MyUser.objects.create(email="test@example.com")
        self.user.set_password("password123")
        self.user.save()
        self.profile = UserProfile.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            phone_number="1234567890"
        )
        self.shop_user = MyUser.objects.create(email="shop@example.com", user_type="shop")
        self.shop = ShopProfile.objects.create(
            user=self.shop_user,
            shop_name="Test Shop",
            shop_owner="Shop Owner",
            mobile_number="0987654321"
        )
        self.service = Service.objects.create(name="TestService")
        self.item = Item.objects.create(name="TestItem", service=self.service)
        self.worker = ShopWorker.objects.create(
            name="Test Worker",
            email="worker@example.com",
            phone="1234567890",
            experience=5.0,
            shop=self.shop,
            rating=0.0
        )
        self.division = Division.objects.create(name="Test Division")
        self.district = District.objects.create(name="Test District", division=self.division)
        self.upazilla = Upazilla.objects.create(name="Test Upazilla", district=self.district)
        self.area = Area.objects.create(name="Test Area", upazilla=self.upazilla)
        self.client.login(email="test@example.com", password="password123")

    def test_profile_post_password_update(self):
        """Test profile POST with matching passwords to cover password update and logout redirect"""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "test@example.com",
            "password": "newpassword123",
            "retype_password": "newpassword123",
            "mobile_number": "1234567890"
        }
        response = self.client.post(reverse("user"), data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("logout"))
        messages = [m.message for m in response.wsgi_request._messages]
        self.assertIn("Please log in again since you changed your password or email.", messages)

    @patch("user_profile.views.District")
    @patch("user_profile.views.Upazilla")
    @patch("user_profile.views.Area")
    def test_addressofbooking_get_render(self, mock_area, mock_upazilla, mock_district):
        """Test addressofbooking GET to cover template rendering"""
        mock_district.objects.all.return_value.values.return_value = [
            {"id": 1, "name": "Test District"}
        ]
        mock_upazilla.objects.values.return_value.annotate.return_value = [
            {"district__name": "Test District", "upazilla_names": ["Test Upazilla"]}
        ]
        mock_area.objects.values.return_value.annotate.return_value = [
            {"upazilla__name": "Test Upazilla", "area_names": ["Test Area"]}
        ]
        response = self.client.get(reverse("addressofbooking"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/customer_profile/addressofbooking.html")
        self.assertEqual(response.context["district"], [{"id": 1, "name": "Test District"}])

    def test_mybooking_post_worker_rating(self):
        """Test mybooking POST to cover worker rating update"""
        # Use timezone-aware datetime for time field
        aware_time = timezone.now()
        booking = BookingSlot.objects.create(
            user=self.profile,
            shop=self.shop,
            worker=self.worker,
            item=self.item,
            date=date.today(),
            time=aware_time,
            status="confirmed"
        )
        data = {
            "rating": "4.5",
            "to": str(booking.id)
        }
        response = self.client.post(reverse("mybooking"), data)
        booking.refresh_from_db()
        self.worker.refresh_from_db()
        self.assertTrue(booking.rated)
        self.assertEqual(self.worker.rating, Decimal("4.5"))
        self.assertContains(response, "Rating submitted successfully.")

class AdditionalUserProfileViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = MyUser.objects.create(email="test@example.com")
        self.user.set_password("password123")
        self.user.save()
        self.profile = UserProfile.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            phone_number="1234567890",
            user_state="Initial State",
            user_city="Initial City",
            user_area="Initial Area",
            latitude=12.34,
            longitude=56.78
        )
        self.shop_user = MyUser.objects.create(email="shop@example.com", user_type="shop")
        self.shop = ShopProfile.objects.create(
            user=self.shop_user,
            shop_name="Test Shop",
            shop_owner="Shop Owner",
            mobile_number="0987654321"
        )
        self.service = Service.objects.create(name="TestService")
        self.item = Item.objects.create(name="TestItem", service=self.service)
        self.worker = ShopWorker.objects.create(
            name="Test Worker",
            email="worker@example.com",
            phone="1234567890",
            experience=5.0,
            shop=self.shop,
            rating=0.0
        )
        self.division = Division.objects.create(name="Test Division")
        self.district = District.objects.create(name="Test District", division=self.division)
        self.upazilla = Upazilla.objects.create(name="Test Upazilla", district=self.district)
        self.area = Area.objects.create(name="Test Area", upazilla=self.upazilla)
        self.client.login(email="test@example.com", password="password123")

    def test_mybooking_post_invalid_booking_id(self):
        """Test mybooking POST with invalid booking ID to cover BookingSlot.DoesNotExist"""
        data = {
            "rating": "4.5",
            "to": "999"  # Non-existent booking ID
        }
        response = self.client.post(reverse("mybooking"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/customer_profile/mybooking.html")
        # Note: The view prints "Booking slot not found" to console, which we can't directly test
        # But we verify the view doesn't crash and renders the template


# user_profile/tests.py
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import date, time, datetime
from decimal import Decimal
from my_app.models import Division, District, Upazilla, Area, Service, Item
from shop_profile.models import ShopProfile, ShopWorker, ShopService
from user_profile.models import UserProfile
from booking.models import BookingSlot
from unittest.mock import patch
from django.http import HttpResponse
from django.core.files.uploadedfile import SimpleUploadedFile
import json

class UserProfileCoverageTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create shop user and profile
        self.shop_user = UserModel.objects.create_user(
            email='shopuser@example.com',
            password='shoppass123',
            user_type='shop'
        )
        self.shop_profile = ShopProfile.objects.create(
            user=self.shop_user,
            shop_name='Test Shop',
            shop_title='Test Title',
            shop_info='Test Info',
            shop_state='Test District',
            shop_city='Test Upazilla',
            shop_area='Test Area',
            shop_rating=4.5,
            shop_customer_count=100,
            gender='Both',
            mobile_number='0987654321'
        )

        # Create regular user and profile
        self.user = UserModel.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            user_type='user'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            gender='Male',
            phone_number='1234567890',
            user_state='Old District',
            user_city='Old Upazilla',
            user_area='Old Area',
            latitude=0.0,
            longitude=0.0
        )

        # Create location hierarchy
        self.division = Division.objects.create(name='Test Division')
        self.district = District.objects.create(name='Test District', division=self.division)
        self.upazilla = Upazilla.objects.create(name='Test Upazilla', district=self.district)
        self.area = Area.objects.create(name='Test Area', upazilla=self.upazilla)

        # Create service and item
        self.service = Service.objects.create(name='Test Service')
        self.item = Item.objects.create(
            name='Test Item',
            item_description='Test Description',
            service=self.service,
            gender='Both'
        )

        # Create shop service
        self.shop_service = ShopService.objects.create(
            shop=self.shop_profile,
            item=self.item,
            price=50.00
        )

        # Create shop worker
        self.shop_worker = ShopWorker.objects.create(
            shop=self.shop_profile,
            name='Test Worker',
            email='worker@example.com',
            phone='1234567890',
            experience=5.0
        )

        # Create booking slot
        self.booking = BookingSlot.objects.create(
            user=self.user_profile,
            shop=self.shop_profile,
            worker=self.shop_worker,
            item=self.item,
            status='pending',
            date=date(2024, 5, 5),
            time=time(10, 0),
            payment_status='unpaid',
            user_end=True,
            shop_end=False,
            notes='',
            rated=False
        )

    def test_addressofbooking_with_upazilla(self):
        # Cover: POST request with upazilla updating all fields
        self.client.force_login(self.user)
        with patch('my_app.models.Upazilla.objects', return_value=[{'district__name': 'Test District', 'upazilla_names': ['Test Upazilla']}]):
            with patch('my_app.models.Area.objects', return_value=[{'upazilla__name': 'Test Upazilla', 'area_names': ['Test Area']}]):
                response = self.client.post(reverse('addressofbooking'), {
                    'district': 'New District',
                    'upazilla': 'New Upazilla',
                    'area': 'New Area',
                    'latitude': '12.34',
                    'longitude': '56.78'
                })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/customer_profile/addressofbooking.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Successfully changed your address.')
        self.user_profile.refresh_from_db()
        self.assertEqual(self.user_profile.user_state, 'New District')
        self.assertEqual(self.user_profile.user_city, 'New Upazilla')
        self.assertEqual(self.user_profile.user_area, 'New Area')
        self.assertEqual(self.user_profile.latitude, 12.34)
        self.assertEqual(self.user_profile.longitude, 56.78)

    def test_addressofbooking_without_upazilla(self):
        # Cover: POST request without upazilla updating area, latitude, longitude
        self.client.force_login(self.user)
        with patch('my_app.models.Upazilla.objects', return_value=[{'district__name': 'Test District', 'upazilla_names': ['Test Upazilla']}]):
            with patch('my_app.models.Area.objects', return_value=[{'upazilla__name': 'Test Upazilla', 'area_names': ['Test Area']}]):
                response = self.client.post(reverse('addressofbooking'), {
                    'area': 'New Area',
                    'latitude': '12.34',
                    'longitude': '56.78'
                })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/customer_profile/addressofbooking.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Successfully changed your address.')
        self.user_profile.refresh_from_db()
        self.assertEqual(self.user_profile.user_area, 'New Area')
        self.assertEqual(self.user_profile.latitude, 12.34)
        self.assertEqual(self.user_profile.longitude, 56.78)

    def test_addressofbooking_get(self):
        # Cover: GET request rendering addressofbooking template
        self.client.force_login(self.user)
        with patch('my_app.models.Upazilla.objects', return_value=[{'district__name': 'Test District', 'upazilla_names': ['Test Upazilla']}]):
            with patch('my_app.models.Area.objects', return_value=[{'upazilla__name': 'Test Upazilla', 'area_names': ['Test Area']}]):
                response = self.client.get(reverse('addressofbooking'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/customer_profile/addressofbooking.html')
        self.assertEqual(response.context['user'], self.user_profile)
        self.assertEqual(len(response.context['district']), 1)
        self.assertEqual(response.context['district'][0]['id'], self.district.id)

    def test_myreviews_view(self):
        # Cover: GET request rendering myreviews template
        self.client.force_login(self.user)
        response = self.client.get(reverse('myreviews'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/customer_profile/myreviews.html')

    def test_mybooking_worker_does_not_exist(self):
        # Cover: ShopWorker.DoesNotExist exception with print statement
        self.client.force_login(self.user)
        # Delete the worker to trigger DoesNotExist
        self.shop_worker.delete()
        with patch('builtins.print') as mocked_print:
            response = self.client.post(reverse('mybooking'), {
                'rating': '5',
                'to': self.booking.id
            })
        mocked_print.assert_called_with("Booking slot not found")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/customer_profile/mybooking.html')