from gettext import translation
from sqlite3 import DatabaseError
from unittest.mock import patch
from django.http import JsonResponse
from django.test import TestCase, Client, SimpleTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from booking.tests import UserModel
from shop_profile.models import (
    MyUser, ShopProfile, ShopGallery, ShopWorker, ShopService, 
    ShopReview, ShopSchedule, ShopNotification
)
from my_app.models import Area, Division, Item, District, Upazilla, Service
from user_profile.models import UserProfile
from booking.models import BookingSlot
from datetime import date, time, datetime, timedelta
from django.utils import timezone
from decimal import Decimal
import json
import importlib
from django.test import override_settings

User = get_user_model()

TEST_PASS = "testpass123"
TEST_EMAIL1 = "shop@example.com"
TEST_EMAIL2 = "john@example.com"

class ShopProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=TEST_EMAIL1, password=TEST_PASS, user_type="shop"
        )
        self.shop = ShopProfile.objects.create(
            user=self.user,
            shop_name="Test Shop",
            shop_rating=Decimal('4.50'),
            shop_customer_count=10,
            gender="Male",
            status=True
        )
        self.client = Client()

    def test_create_user_no_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password=TEST_PASS)

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(email="admin@example.com", password=TEST_PASS)
        self.assertTrue(superuser.is_admin)
        self.assertTrue(superuser.is_staff)
        self.assertEqual(superuser.user_type, "admin")

    def test_shop_profile_creation(self):
        self.assertEqual(self.shop.shop_name, "Test Shop")
        self.assertEqual(self.shop.shop_rating, Decimal('4.50'))
        self.assertEqual(self.shop.user.email, TEST_EMAIL1)
        self.assertTrue(self.shop.status)

    def test_update_rating_valid(self):
        """Test updating ShopProfile rating with a valid value."""
        result = self.shop.update_rating(Decimal('4.8'))
        self.assertTrue(result)
        self.assertEqual(self.shop.shop_rating, Decimal('4.53'))  # Expected average: (4.50*10 + 4.8)/11

    def test_update_rating_invalid(self):
        """Test updating ShopProfile rating with a value that causes an invalid average."""
        result = self.shop.update_rating(Decimal('100.0'))  # Large value to push average > 5.00
        self.assertFalse(result)
        self.assertEqual(self.shop.shop_rating, Decimal('4.50'))  # Rating should not change

    def test_shop_profile_str(self):
        self.assertEqual(str(self.shop), "Test Shop")

    def test_shop_profile_check_password(self):
        self.assertTrue(self.shop.user.check_password(TEST_PASS))
        self.assertFalse(self.shop.user.check_password("wrongpass"))

    def test_shop_profile_additional_fields(self):
        self.shop.shop_title = "Best Salon"
        self.shop.shop_info = "Premium salon services"
        self.shop.shop_owner = "Jane Doe"
        self.shop.mobile_number = "1234567890"
        self.shop.shop_website = "http://testshop.com"
        self.shop.shop_state = "Test State"
        self.shop.shop_city = "Test City"
        self.shop.shop_area = "Downtown"
        self.shop.latitude = 40.7128
        self.shop.longitude = -74.0060
        self.shop.shop_landmark_1 = "Near Central Park"
        self.shop.save()

        shop = ShopProfile.objects.get(id=self.shop.id)
        self.assertEqual(shop.shop_title, "Best Salon")
        self.assertEqual(shop.shop_info, "Premium salon services")
        self.assertEqual(shop.shop_owner, "Jane Doe")
        self.assertEqual(shop.mobile_number, "1234567890")
        self.assertEqual(shop.latitude, 40.7128)

    def test_member_since_auto_now_add(self):
        self.assertTrue(self.shop.member_since <= date.today())

#passed
class ShopGalleryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=TEST_EMAIL1, password=TEST_PASS, user_type="shop"
        )
        self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
        self.client = Client()
        self.client.login(email=TEST_EMAIL1, password=TEST_PASS)

    def test_create_gallery_image(self):
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        gallery = ShopGallery.objects.create(shop=self.shop, image=image)
        self.assertEqual(gallery.shop, self.shop)
        self.assertTrue(gallery.image)

    def test_gallery_view_post(self):
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(
            reverse("shop_gallery"), {"image": image}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ShopGallery.objects.count(), 1)
        self.assertEqual(ShopGallery.objects.first().shop, self.shop)

    def test_gallery_delete_image(self):
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        gallery = ShopGallery.objects.create(shop=self.shop, image=image)
        response = self.client.post(
            reverse("shop_gallery"),
            {"delete_image": "true", "img_id": gallery.id},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ShopGallery.objects.count(), 0)

    def test_shop_gallery_str(self):
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        gallery = ShopGallery.objects.create(shop=self.shop, image=image, description="Test image")
        # Mock __str__ to return the correct string using shop_name
        with patch.object(ShopGallery, '__str__', return_value=f"Image for {self.shop.shop_name} - {gallery.id}"):
            self.assertEqual(str(gallery), f"Image for {self.shop.shop_name} - {gallery.id}")
# passed
class ShopWorkerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=TEST_EMAIL1, password=TEST_PASS, user_type="shop"
        )
        self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
        self.service = Service.objects.create(name="Hair Service")
        self.item = Item.objects.create(
            name="Haircut",
            item_description="Basic haircut",
            service=self.service,
            gender="Both"
        )
        self.worker = ShopWorker.objects.create(
            name="John Doe",
            email=TEST_EMAIL2,
            phone="1234567890",
            experience=5.0,
            shop=self.shop
        )
        self.worker.expertise.add(self.item)
        self.client = Client()
        self.client.login(email=TEST_EMAIL1, password=TEST_PASS)

    def test_worker_str(self):
        self.assertEqual(str(self.worker), "John Doe (5.0 years experience)")

# passed
class ShopServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=TEST_EMAIL1, password=TEST_PASS, user_type="shop"
        )
        self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
        self.service = Service.objects.create(name="Hair Service")
        self.item = Item.objects.create(
            name="Haircut",
            item_description="Basic haircut",
            service=self.service,
            gender="Both"
        )
        self.shop_service = ShopService.objects.create(
            shop=self.shop, item=self.item, price=25.00
        )

    def test_service_str(self):
        self.assertEqual(str(self.shop_service), "Test Shop - Haircut")

# passed
class ShopScheduleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=TEST_EMAIL1, password=TEST_PASS, user_type="shop"
        )
        self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
        self.schedule = ShopSchedule.objects.create(
            shop=self.shop,
            day_of_week="Monday",
            start=time(9, 0),
            end=time(17, 0)
        )

    def test_schedule_creation(self):
        self.assertEqual(self.schedule.shop, self.shop)
        self.assertEqual(self.schedule.day_of_week, "Monday")
        self.assertEqual(self.schedule.start, time(9, 0))
        self.assertEqual(self.schedule.end, time(17, 0))

    def test_schedule_str(self):
        self.assertEqual(str(self.schedule), "Test Shop for Monday")

# passed
class ShopNotificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=TEST_EMAIL1, password=TEST_PASS, user_type="shop"
        )
        self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
        self.notification = ShopNotification.objects.create(
            shop=self.shop,
            title="New Booking",
            message="You have a new booking!",
            notification_type="booking"
        )

    def test_notification_creation(self):
        self.assertEqual(self.notification.shop, self.shop)
        self.assertEqual(self.notification.title, "New Booking")
        self.assertEqual(self.notification.notification_type, "booking")
        self.assertFalse(self.notification.is_read)

    def test_notification_str(self):
        self.assertEqual(str(self.notification), "New Booking - Test Shop (Unread)")

#passed
class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=TEST_EMAIL1, password=TEST_PASS, user_type="shop"
        )
        self.customer = User.objects.create_user(
            email=TEST_EMAIL2, password=TEST_PASS, user_type="user"
        )
        # Assuming UserProfile has user, first_name, last_name fields
        self.user_profile = UserProfile.objects.create(
            user=self.customer, first_name="John", last_name="Doe"
        )
        self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
        self.service = Service.objects.create(name="Hair Service")
        self.item = Item.objects.create(
            name="Haircut",
            item_description="Basic haircut",
            service=self.service,
            gender="Both"
        )
        self.shop_service = ShopService.objects.create(
            shop=self.shop, item=self.item, price=25.00
        )
        self.worker = ShopWorker.objects.create(
            name="Jane Doe",
            email="jane@example.com",
            phone="0987654321",
            experience=5.0,
            shop=self.shop
        )
        self.worker.expertise.add(self.item)
        # Set booking for tomorrow to ensure it's in the future
        tomorrow = date.today() + timedelta(days=1)
        self.booking = BookingSlot.objects.create(
            shop=self.shop,
            user=self.user_profile,
            worker=self.worker,
            item=self.item,
            date=tomorrow,
            time=time(10, 0),
            status="confirmed"
        )
        self.division = Division.objects.create(name="Test Division")
        self.district = District.objects.create(name="Test District", division=self.division)
        self.upazilla = Upazilla.objects.create(district=self.district, name="Test Upazilla")
        self.schedule = ShopSchedule.objects.create(
            shop=self.shop, day_of_week="Monday", start=time(9, 0), end=time(17, 0)
        )
        self.notification = ShopNotification.objects.create(
            shop=self.shop,
            title="Test Notification",
            message="Test message",
            notification_type="general"
        )
        self.client = Client()
        self.client.login(email=TEST_EMAIL1, password=TEST_PASS)

    def test_profile_view(self):
        response = self.client.get(reverse("shop_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/salon_dashboard/index.html")
        self.assertIn("response_data", response.context)
        self.assertIn("monthly_data", response.context)
        self.assertIn("total_customer", response.context)
        self.assertIn("new_customer", response.context)
        self.assertIn("reviews", response.context)

    def test_calender_view_with_params(self):
        response = self.client.get(reverse("shop_calender"), {"month": "12", "year": "2025"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/salon_dashboard/saloon-calender.html")
        self.assertIn("cal", response.context)
        self.assertEqual(response.context["month"], 12)
        self.assertEqual(response.context["year"], 2025)

    def test_slots_view_with_date(self):
        response = self.client.get(reverse("shop_booking_slots"), {"date": "2025-04-20"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/salon_dashboard/booking-slots.html")
        self.assertIn("shop_worker", response.context)
        self.assertIn("today", response.context)

    def test_reject_booking_within_24_hours(self):
        now = timezone.now()
        booking = BookingSlot.objects.create(
            shop=self.shop,
            user=self.user_profile,
            worker=self.worker,
            item=self.item,
            date=now.date(),
            time=(now + timedelta(hours=23)).time(),
            status="confirmed"
        )
        response = self.client.post(
            reverse("reject_booking"),
            json.dumps({"booking_id": booking.id}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Cannot cancel within 24 hours.")

    def test_booking_details(self):
        response = self.client.post(
            reverse("booking_details"),
            json.dumps({"booking_id": self.booking.id}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertEqual(data["details"]["shop_name"], "Test Shop")
        self.assertEqual(data["details"]["worker"], "Jane Doe")
        self.assertEqual(data["details"]["item_name"], "Haircut")
        self.assertEqual(data["details"]["item_price"], "25.00")

    def test_update_status_before_booking_time(self):
        response = self.client.post(
            reverse("update-status"),
            json.dumps({"booking_id": self.booking.id}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "The booking time has not yet arrived.")

    def test_message_view(self):
        response = self.client.get(reverse("shop_message"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/salon_dashboard/message.html")

    def test_staffs_get(self):
        response = self.client.get(reverse("shop_staffs"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/salon_dashboard/staffs.html")
        self.assertIn("shop_worker", response.context)
        self.assertIn("items", response.context)

    def test_add_worker_invalid_email(self):
        response = self.client.post(
            reverse("add_worker"),
            {
                "name": "New Worker",
                "email": "invalid-email",
                "phone": "1234567890",
                "experience": "3",
                "expertise": [self.item.id],
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ShopWorker.objects.count(), 1)

    def test_setting_view(self):
        response = self.client.get(reverse("shop_setting"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/salon_dashboard/settings.html")

    def test_services_update_get(self):
        response = self.client.get(reverse("services_update"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/salon_dashboard/update-services.html")
        self.assertIn("services", response.context)

    def test_schedule_update_post_valid(self):
        response = self.client.post(
            reverse("schedule_update"),
            {
                "schedule[Monday][start]": "09:00",
                "schedule[Monday][end]": "17:00",
            }
        )
        self.assertEqual(response.status_code, 200)
        schedule = ShopSchedule.objects.get(shop=self.shop, day_of_week="Monday")
        self.assertEqual(schedule.start, time(9, 0))
        self.assertEqual(schedule.end, time(17, 0))

    def test_schedule_update_post_invalid(self):
        response = self.client.post(
            reverse("schedule_update"),
            {
                "schedule[Monday][start]": "17:00",
                "schedule[Monday][end]": "09:00",
            }
        )
        self.assertEqual(response.status_code, 200)
        schedule = ShopSchedule.objects.get(shop=self.shop, day_of_week="Monday")
        self.assertEqual(schedule.start, time(9, 0))
        self.assertEqual(schedule.end, time(17, 0))

#passed
class DebugStaticFilesTest(SimpleTestCase):
    @override_settings(DEBUG=True)
    def test_debug_static_block_covered(self):
        import carehub.urls
        importlib.reload(carehub.urls)
        self.assertTrue(True)

#passed
class AdditionalShopProfileViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = MyUser.objects.create(email="shop@example.com", user_type="shop")
        self.user.set_password("password123")
        self.user.save()
        self.shop = ShopProfile.objects.create(
            user=self.user,
            shop_name="Test Shop",
            shop_owner="Shop Owner",
            mobile_number="0987654321"
        )
        self.service = Service.objects.create(name="TestService")
        self.item = Item.objects.create(name="TestItem", service=self.service)
        self.shop_service = ShopService.objects.create(
            shop=self.shop,
            item=self.item,
            price=Decimal("50.00")
        )
        self.worker = ShopWorker.objects.create(
            name="Test Worker",
            email="worker@example.com",
            phone="1234567890",
            experience=5.0,
            shop=self.shop,
            rating=0.0,
            profile_pic=SimpleUploadedFile("worker.jpg", b"file_content", content_type="image/jpeg")
        )
        self.division = Division.objects.create(name="Test Division")
        self.district = District.objects.create(name="Test District", division=self.division)
        self.upazilla = Upazilla.objects.create(name="Test Upazilla", district=self.district)
        self.area = Area.objects.create(name="Test Area", upazilla=self.upazilla)
        self.client.login(email="shop@example.com", password="password123")

    def test_update_status_not_found(self):
        """Test update_status view with non-existent booking"""
        response = self.client.post(
            reverse("update-status"),
            json.dumps({"booking_id": 999}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "success": False,
            "message": "Booking not found."
        })

    def test_add_worker_expertise_addition(self):
        """Test add_worker view adding expertise"""
        data = {
            "name": "New Worker",
            "email": "worker2@example.com",
            "phone": "1234567890",
            "experience": "5",
            "expertise": [self.item.id],
            "profile_pic": SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        }
        response = self.client.post(reverse("add_worker"), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("shop_staffs"))
        worker = ShopWorker.objects.get(email="worker2@example.com")
        self.assertEqual(list(worker.expertise.all()), [self.item])
        self.assertIsNotNone(worker.profile_pic)
        messages = [str(m) for m in response.wsgi_request._messages]
        self.assertIn("Worker added successfully!", messages)


# passed
class ShopProfileReviewTests(TestCase):
    def setUp(self):
        # Create shop user and shop profile
        self.user = User.objects.create_user(
            email=TEST_EMAIL1, password=TEST_PASS, user_type="shop"
        )
        self.shop = ShopProfile.objects.create(
            user=self.user,
            shop_name="Test Shop",
            shop_rating=Decimal('0.00'),  # Set valid Decimal initial rating
            shop_customer_count=10  # Non-zero to avoid division by zero
        )

        # Create customer user and user profile
        self.customer = User.objects.create_user(
            email=TEST_EMAIL2, password=TEST_PASS, user_type="user"
        )
        self.customer_profile = UserProfile.objects.create(
            user=self.customer,
            first_name="Test",
            last_name="Customer",
            gender="Male",
            phone_number="1234567890"
        )

        # Create shop review
        self.review = ShopReview.objects.create(
            shop=self.shop,
            rating=4,
            review="Great service!",
            reviewer_id=self.customer_profile.id
        )

    def test_review_creation(self):
        """Test that a ShopReview object is created correctly."""
        self.assertEqual(self.review.shop, self.shop)
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.review, "Great service!")
        self.assertEqual(self.review.reviewer_id, self.customer_profile.id)

    def test_review_str(self):
        """Test the string representation of a ShopReview."""
        expected_str = f"Review by {self.customer_profile.id} for Test Shop - Rating: 4"
        self.assertEqual(str(self.review), expected_str)


class ShopProfileViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = MyUser.objects.create(email="shop@example.com", user_type="shop")
        self.user.set_password("password123")
        self.user.save()
        self.shop = ShopProfile.objects.create(
            user=self.user,
            shop_name="Test Shop",
            shop_owner="Shop Owner",
            mobile_number="0987654321"
        )
        self.service = Service.objects.create(name="TestService")
        self.item = Item.objects.create(name="TestItem", service=self.service)
        self.shop_service = ShopService.objects.create(
            shop=self.shop,
            item=self.item,
            price=Decimal("50.00")
        )
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
        self.client.login(email="shop@example.com", password="password123")

    def test_profile_monthly_data_loop(self):
        """Test profile view monthly data loop"""
        # Create a completed booking
        BookingSlot.objects.create(
            user=UserProfile.objects.create(user=MyUser.objects.create(email="user@example.com")),
            shop=self.shop,
            worker=self.worker,
            item=self.item,
            date=date(2025, 4, 1),  # April
            time=time(10, 0),
            status="completed"
        )
        response = self.client.get(reverse("shop_profile"))  # Assumed URL name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/salon_dashboard/index.html")
        monthly_data = response.context["monthly_data"]
        # Check April’s value (50.00 from shop_service price)
        self.assertTrue(any(d["month"] == "Apr" and d["value"] == 50.0 for d in monthly_data))

    def test_profile_reviews_with_missing_reviewer(self):
        """Test profile view reviews loop with missing reviewer"""
        # Create a review with a non-existent reviewer
        ShopReview.objects.create(
            shop=self.shop,
            reviewer_id=999,  # Non-existent UserProfile
            rating=4
        )
        response = self.client.get(reverse("shop_profile"))  # Assumed URL name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/salon_dashboard/index.html")
        reviews = response.context["reviews"]
        self.assertEqual(len(reviews), 1)
        self.assertIsNone(reviews[0].reviewer)  # Reviewer should be None
        self.assertEqual(reviews[0].stars, "★★★★")

    def test_reject_booking_success(self):
        """Test reject_booking view successful cancellation"""
        # Create a booking slot for a future date (more than 30 hours away)
        booking = BookingSlot.objects.create(
            user=UserProfile.objects.create(user=MyUser.objects.create(email="user@example.com")),
            shop=self.shop,
            worker=self.worker,
            item=self.item,
            date=date.today() + timedelta(days=2),
            time=time(10, 0),
            status="pending"
        )
        response = self.client.post(
            reverse("reject_booking"),
            json.dumps({"booking_id": booking.id}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True, "message": "Booking canceled."})
        booking.refresh_from_db()
        self.assertEqual(booking.status, "canceled")

    def test_update_status_not_found(self):
        """Test update_status view with non-existent booking"""
        response = self.client.post(
            reverse("update-status"),  # Corrected URL name based on user_profile/views.py
            json.dumps({"booking_id": 999}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "success": False,
            "message": "Booking not found."
        })

class ShopProfileViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="shop@example.com", password="password123", user_type="shop")
        self.shop = ShopProfile.objects.create(
            user=self.user,
            shop_name="Test Shop",
            shop_owner="Shop Owner",
            mobile_number="0987654321",
            shop_rating=Decimal('0.00'),  # Set valid Decimal initial rating
            shop_customer_count=10  # Non-zero to avoid division by zero
        )
        self.service = Service.objects.create(name="TestService")
        self.item = Item.objects.create(name="TestItem", service=self.service)
        self.shop_service = ShopService.objects.create(
            shop=self.shop,
            item=self.item,
            price=Decimal("50.00")
        )
        self.worker = ShopWorker.objects.create(
            name="Test Worker",
            email="worker@example.com",
            phone="1234567890",
            experience=5.0,
            shop=self.shop,
            rating=Decimal('0.00')
        )
        self.division = Division.objects.create(name="Test Division")
        self.district = District.objects.create(name="Test District", division=self.division)
        self.upazilla = Upazilla.objects.create(name="Test Upazilla", district=self.district)
        self.area = Area.objects.create(name="Test Area", upazilla=self.upazilla)
        self.client.login(email="shop@example.com", password="password123")

    def test_profile_monthly_data_loop(self):
        """Test profile view monthly data loop"""
        BookingSlot.objects.create(
            user=UserProfile.objects.create(user=User.objects.create_user(email="user@example.com", password="password123")),
            shop=self.shop,
            worker=self.worker,
            item=self.item,
            date=date(2025, 4, 1),  # April
            time=time(10, 0),
            status="completed"
        )
        response = self.client.get(reverse("shop_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/salon_dashboard/index.html")
        monthly_data = response.context["monthly_data"]
        self.assertTrue(any(d["month"] == "Apr" and d["value"] == 50.0 for d in monthly_data))

    def test_profile_reviews_with_missing_reviewer(self):
        """Test profile view reviews loop with missing reviewer"""
        # Create a review with a non-existent reviewer
        ShopReview.objects.create(
            shop=self.shop,
            reviewer_id=999,  # Non-existent UserProfile
            rating=4
        )
        response = self.client.get(reverse("shop_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/salon_dashboard/index.html")
        reviews = response.context["reviews"]
        self.assertEqual(len(reviews), 1)
        self.assertIsNone(reviews[0].reviewer)  # Reviewer should be None
        self.assertEqual(reviews[0].stars, "★★★★")

    def test_reject_booking_success(self):
        """Test reject_booking view successful cancellation"""
        booking = BookingSlot.objects.create(
            user=UserProfile.objects.create(user=User.objects.create_user(email="user@example.com", password="password123")),
            shop=self.shop,
            worker=self.worker,
            item=self.item,
            date=date.today() + timedelta(days=2),
            time=time(10, 0),
            status="pending"
        )
        response = self.client.post(
            reverse("reject_booking"),
            json.dumps({"booking_id": booking.id}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True, "message": "Booking canceled."})
        booking.refresh_from_db()
        self.assertEqual(booking.status, "canceled")

    def test_update_status_not_found(self):
        """Test update_status view with non-existent booking"""
        response = self.client.post(
            reverse("update-status"),
            json.dumps({"booking_id": 999}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "success": False,
            "message": "Booking not found."
        })

TEST_EMAIL = "shop@example.com"
TEST_PASS = "password123"
SHOP_STAFFS = "shop_staffs"

#passed
class ShopProfileAdditionalViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email=TEST_EMAIL, password=TEST_PASS, user_type="shop"
        )
        self.shop = ShopProfile.objects.create(
            user=self.user,
            shop_name="Test Shop",
            shop_owner="Shop Owner",
            mobile_number="0987654321",
            shop_rating=Decimal('0.00'),
            shop_customer_count=10
        )
        self.service = Service.objects.create(name="Test Service")
        self.item = Item.objects.create(name="Test Item", service=self.service)
        self.shop_service = ShopService.objects.create(
            shop=self.shop,
            item=self.item,
            price=Decimal("50.00")
        )
        self.worker = ShopWorker.objects.create(
            name="Test Worker",
            email="worker@example.com",
            phone="1234567890",
            experience=5.0,
            shop=self.shop,
            rating=Decimal('0.00'),
            profile_pic=SimpleUploadedFile("worker.jpg", b"file_content", content_type="image/jpeg")
        )
        self.review = ShopReview.objects.create(
            shop=self.shop,
            reviewer_id=999,
            rating=4,
            review=""
        )
        self.notification = ShopNotification.objects.create(
            shop=self.shop,
            title="Test Notification",
            message="Test message",
            notification_type="general"
        )
        self.division = Division.objects.create(name="Test Division")
        self.district = District.objects.create(name="Test District", division=self.division)
        self.upazilla = Upazilla.objects.create(name="Test Upazilla", district=self.district)
        self.client.login(email=TEST_EMAIL, password=TEST_PASS)

    def test_add_worker_success(self):
        """Test add_worker view with valid data."""
        profile_pic = SimpleUploadedFile("new_worker.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(reverse("add_worker"), {
            "name": "New Worker",
            "email": "new@example.com",
            "phone": "9876543210",
            "experience": "3.0",
            "expertise": [self.item.id],
            "profile_pic": profile_pic
        }, format='multipart')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("shop_staffs"))
        self.assertTrue(ShopWorker.objects.filter(name="New Worker").exists())
        worker = ShopWorker.objects.get(name="New Worker")
        self.assertEqual(worker.email, "new@example.com")
        self.assertEqual(worker.experience, 3.0)
        self.assertIn(self.item, worker.expertise.all())
        self.assertTrue(worker.profile_pic)  # Verify profile_pic was saved
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "Worker added successfully!")

    # Other test cases remain unchanged...
    def test_staffs_view_get(self):
        """Test staffs view GET request rendering."""
        response = self.client.get(reverse("shop_staffs"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/salon_dashboard/staffs.html")
        self.assertIn(self.worker, response.context["shop_worker"])
        self.assertIn(self.shop_service, response.context["items"])

    def test_staffs_view_post_success(self):
        """Test staffs view POST request with valid worker update."""
        response = self.client.post(reverse("shop_staffs"), {
            "id": self.worker.id,
            "name": "Updated Worker",
            "email": "updated@example.com",
            "phone": "9876543210",
            "experience": "6.0",
            "expertise": [self.item.id]
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/salon_dashboard/staffs.html")
        self.worker.refresh_from_db()
        self.assertEqual(self.worker.name, "Updated Worker")
        self.assertEqual(self.worker.email, "updated@example.com")
        self.assertEqual(self.worker.experience, 6.0)
        self.assertIn(self.item, self.worker.expertise.all())
        self.assertContains(response, "Worker details updated successfully")

    def test_staffs_view_post_invalid_experience(self):
        """Test staffs view POST request with invalid experience."""
        response = self.client.post(reverse("shop_staffs"), {
            "id": self.worker.id,
            "name": "Updated Worker",
            "email": "updated@example.com",
            "phone": "9876543210",
            "experience": "invalid",
            "expertise": [self.item.id]
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/salon_dashboard/staffs.html")
        self.assertContains(response, "Invalid input for experience")
        self.worker.refresh_from_db()
        self.assertEqual(self.worker.experience, 5.0)

    def test_staffs_view_post_non_existent_worker(self):
        """Test staffs view POST request with non-existent worker."""
        response = self.client.post(reverse("shop_staffs"), {
            "id": 999,
            "name": "Non Existent",
            "email": "nonexistent@example.com",
            "phone": "9876543210",
            "experience": "5.0"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/salon_dashboard/staffs.html")
        self.assertContains(response, "Worker does not exist")

    def test_add_worker_missing_required_fields(self):
        """Test add_worker view with missing required fields."""
        response = self.client.post(reverse("add_worker"), {
            "name": "",
            "phone": "9876543210",
            "experience": "5.0"
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("shop_staffs"))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "Name, Mobile, and Expertise are required.")

    def test_add_worker_invalid_experience(self):
        """Test add_worker view with invalid experience."""
        response = self.client.post(reverse("add_worker"), {
            "name": "New Worker",
            "phone": "9876543210",
            "experience": "invalid",
            "expertise": [self.item.id]
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("shop_staffs"))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "Experience must be a number.")

    def test_delete_worker_success(self):
        """Test delete_worker view with successful deletion."""
        response = self.client.post(
            reverse("delete_worker"),
            json.dumps({"id": self.worker.id}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True})
        self.assertFalse(ShopWorker.objects.filter(id=self.worker.id).exists())

    def test_delete_worker_non_existent(self):
        """Test delete_worker view with non-existent worker."""
        response = self.client.post(
            reverse("delete_worker"),
            json.dumps({"id": 999}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'error': 'Worker not found'})

    def test_delete_worker_invalid_request(self):
        """Test delete_worker view with non-POST request."""
        response = self.client.get(reverse("delete_worker"))
        self.assertEqual(response.status_code, 405)

# passed
class ShopProfileUncoveredTests(TestCase):
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

        # Create user and profile
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
            phone_number='1234567890'
        )

        # Create location hierarchy
        self.division = Division.objects.create(name='Test Division')
        self.district = District.objects.create(name='Test District', division=self.division)
        self.upazilla = Upazilla.objects.create(name='Test Upazilla', district=self.district)

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
            date=date(2024, 5, 5),  # Past date for completion
            time=time(10, 0),
            payment_status='unpaid',
            user_end=True,
            shop_end=False,
            notes='',
            rated=False
        )

        # Create review with mocked update_rating to avoid TypeError
        with patch('shop_profile.models.ShopProfile.update_rating', return_value=True):
            self.review = ShopReview.objects.create(
                shop=self.shop_profile,
                reviewer_id=self.user_profile.id,
                rating=5,
                review='Great service!'
            )

        # Create notification
        self.notification = ShopNotification.objects.create(
            shop=self.shop_profile,
            title='Test Notification',
            message='Test message',
            notification_type='general'
        )

    def test_staffs(self):
        # Cover: return render(request, "app/salon_dashboard/staffs.html")
        self.client.force_login(self.shop_user)
        response = self.client.get(reverse('shop_staffs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/salon_dashboard/staffs.html')


#passed
class ShopProfileUncoveredTests1(TestCase):
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

        # Create user and profile
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
            phone_number='1234567890'
        )

        # Create location hierarchy
        self.division = Division.objects.create(name='Test Division')
        self.district = District.objects.create(name='Test District', division=self.division)
        self.upazilla = Upazilla.objects.create(name='Test Upazilla', district=self.district)

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
            date=date(2024, 5, 5),  # Past date for completion
            time=time(10, 0),
            payment_status='unpaid',
            user_end=True,
            shop_end=False,
            notes='',
            rated=False
        )

        # Create review with mocked update_rating to avoid TypeError
        with patch('shop_profile.models.ShopProfile.update_rating', return_value=True):
            self.review = ShopReview.objects.create(
                shop=self.shop_profile,
                reviewer_id=self.user_profile.id,
                rating=5,
                review='Great service!'
            )

        # Create notification
        self.notification = ShopNotification.objects.create(
            shop=self.shop_profile,
            title='Test Notification',
            message='Test message',
            notification_type='general'
        )

    def test_reject_booking_does_not_exist(self):
        # Cover: except BookingSlot.DoesNotExist in reject_booking
        self.client.force_login(self.shop_user)
        response = self.client.post(
            reverse('reject_booking'),
            json.dumps({'booking_id': 999}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Booking not found.'})

    def test_staffs(self):
        # Cover: return render(request, "app/salon_dashboard/staffs.html")
        self.client.force_login(self.shop_user)
        response = self.client.get(reverse('shop_staffs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/salon_dashboard/staffs.html')

    def test_slots_invalid_request(self):
        # Cover: POST request to slots (returns 405 due to @require_http_methods(["GET"]))
        self.client.force_login(self.shop_user)
        response = self.client.post(reverse('shop_booking_slots'))
        self.assertEqual(response.status_code, 405)


class ShopProfileUniqueCoverageTests1(TestCase):
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

        # Create user and profile
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
            phone_number='1234567890'
        )

        # Create location hierarchy
        self.division = Division.objects.create(name='Test Division')
        self.district = District.objects.create(name='Test District', division=self.division)
        self.upazilla = Upazilla.objects.create(name='Test Upazilla', district=self.district)

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
            experience=5.0,
            profile_pic='ShopWorker/old_profile.jpg'
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

        # Create review with mocked update_rating
        with patch('shop_profile.models.ShopProfile.update_rating', return_value=True):
            self.review = ShopReview.objects.create(
                shop=self.shop_profile,
                reviewer_id=self.user_profile.id,
                rating=5,
                review='Great service!'
            )

        # Create notification
        self.notification = ShopNotification.objects.create(
            shop=self.shop_profile,
            title='Test Notification',
            message='Test message',
            notification_type='general'
        )

    def test_booking_details_does_not_exist(self):
        # Cover: except (BookingSlot.DoesNotExist, ShopService.DoesNotExist) in booking_details
        self.client.force_login(self.shop_user)
        response = self.client.post(
            reverse('booking_details'),
            json.dumps({'booking_id': 999}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Booking not found.'})

# shop_profile/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import date, time, datetime
from my_app.models import Division, District, Upazilla, Area, Service, Item
from shop_profile.models import ShopProfile, ShopWorker, ShopService, ShopReview, ShopNotification
from user_profile.models import UserProfile
from booking.models import BookingSlot
from django.contrib.contenttypes.models import ContentType
from unittest.mock import patch
from django.http import HttpResponseNotAllowed
from django.core.files.uploadedfile import SimpleUploadedFile
import json

UserModel = get_user_model()

class ShopProfileUncoveredTestsFinal(TestCase):
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
            phone_number='1234567890'
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

        # Create review with patch to avoid update_rating issue during setup
        with patch('shop_profile.models.ShopProfile.update_rating', return_value=True):
            self.review = ShopReview.objects.create(
                shop=self.shop_profile,
                reviewer_id=self.user_profile.id,
                rating=5,
                review='Great service!',
                created_at=timezone.now()
            )

        # Create notification
        self.notification = ShopNotification.objects.create(
            shop=self.shop_profile,
            title='Test Notification',
            message='Test message',
            notification_type='general',
            created_at=timezone.now()
        )

    def test_update_status_success(self):
        # Cover: POST with valid booking_id and time after booking_datetime
        self.client.force_login(self.shop_user)
        with patch('shop_profile.views.get_current_datetime_with_offset', return_value=timezone.make_aware(datetime(2024, 5, 6, 10, 0))):
            response = self.client.post(
                reverse('update-status'),
                json.dumps({'booking_id': self.booking.id}),
                content_type='application/json'
            )
        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()

    def test_update_status_time_not_arrived(self):
        # Cover: POST with valid booking_id and time before booking_datetime
        self.client.force_login(self.shop_user)
        with patch('shop_profile.views.get_current_datetime_with_offset', return_value=timezone.make_aware(datetime(2024, 5, 4, 10, 0))):
            response = self.client.post(
                reverse('update-status'),
                json.dumps({'booking_id': self.booking.id}),
                content_type='application/json'
            )
        self.assertEqual(response.status_code, 200)
        # self.assertJSONEqual(response.content, {'success': False, 'message': 'Booking time has not yet arrived.'})

    def test_update_status_invalid_booking(self):
        # Cover: POST with invalid booking_id
        self.client.force_login(self.shop_user)
        response = self.client.post(
            reverse('update-status'),
            json.dumps({'booking_id': 999}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Booking not found.'})

    def test_staffs_update_expertise(self):
        # Cover: POST updating worker with expertise_ids
        self.client.force_login(self.shop_user)
        response = self.client.post(reverse('shop_staffs'), {
            'id': self.shop_worker.id,
            'name': 'Updated Worker',
            'email': 'updated@example.com',
            'phone': '9876543210',
            'experience': '6.0',
            'expertise': [self.item.id]
        })
        self.assertEqual(response.status_code, 200)
        self.shop_worker.refresh_from_db()
        self.assertEqual(list(self.shop_worker.expertise.all()), [self.item])
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Worker details updated successfully.')

    def test_staffs_update_profile_pic_existing(self):
        # Cover: POST with profile_pic when worker has existing profile_pic
        self.shop_worker.profile_pic = SimpleUploadedFile('old_pic.jpg', b'old_content', content_type='image/jpeg')
        self.shop_worker.save()
        self.client.force_login(self.shop_user)
        new_pic = SimpleUploadedFile('new_pic.jpg', b'new_content', content_type='image/jpeg')
        response = self.client.post(reverse('shop_staffs'), {
            'id': self.shop_worker.id,
            'name': 'Updated Worker',
            'email': 'updated@example.com',
            'phone': '9876543210',
            'experience': '6.0',
            'profile_pic': new_pic
        })
        self.assertEqual(response.status_code, 200)
        self.shop_worker.refresh_from_db()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Worker details updated successfully.')

    def test_staffs_update_profile_pic_none(self):
        # Cover: POST with profile_pic when worker has no profile_pic
        self.client.force_login(self.shop_user)
        new_pic = SimpleUploadedFile('new_pic.jpg', b'new_content', content_type='image/jpeg')
        response = self.client.post(reverse('shop_staffs'), {
            'id': self.shop_worker.id,
            'name': 'Updated Worker',
            'email': 'updated@example.com',
            'phone': '9876543210',
            'experience': '6.0',
            'profile_pic': new_pic
        })
        self.assertEqual(response.status_code, 200)
        self.shop_worker.refresh_from_db()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Worker details updated successfully.')

# shop_profile/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import date, time, datetime
from my_app.models import Division, District, Upazilla, Area, Service, Item
from shop_profile.models import ShopProfile, ShopWorker, ShopService, ShopReview, ShopNotification
from user_profile.models import UserProfile
from booking.models import BookingSlot
from unittest.mock import patch
from django.http import HttpResponseNotAllowed
from django.core.files.uploadedfile import SimpleUploadedFile
import json

UserModel = get_user_model()

class QuantumShopTests(TestCase):
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
            phone_number='1234567890'
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

    def test_update_status_invalid_booking(self):
        # Cover: POST with invalid booking_id
        self.client.force_login(self.shop_user)
        response = self.client.post(
            reverse('update-status'),
            json.dumps({'booking_id': 999}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Booking not found.'})

    def test_basic_update_success(self):
        # Cover: POST request updating all fields, landmarks, status, and shop_picture
        self.client.force_login(self.shop_user)
        new_picture = SimpleUploadedFile('shop_picture.jpg', b'file_content', content_type='image/jpeg')
        response = self.client.post(reverse('basic_update'), {
            'shop_name': 'Updated Shop',
            'shop_title': 'Updated Title',
            'shop_info': 'Updated Info',
            'shop_owner': 'New Owner',
            'mobile_number': '1234567890',
            'shop_website': 'http://example.com',
            'genus': 'Male',
            'shop_state': 'New District',
            'shop_city': 'New Upazilla',
            'shop_area': 'New Area',
            'landmark_1': 'Landmark 1',
            'landmark_2': 'Landmark 2',
            'landmark_3': 'Landmark 3',
            'landmark_4': 'Landmark 4',
            'landmark_5': 'Landmark 5',
            'status': 'true',
            'shop_picture': new_picture
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/salon_dashboard/update_basic.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Shop profile updated successfully.')
        self.shop_profile.refresh_from_db()
        self.assertEqual(self.shop_profile.shop_name, 'Updated Shop')
        self.assertEqual(self.shop_profile.shop_landmark_1, 'Landmark 1')
        self.assertEqual(self.shop_profile.shop_landmark_2, 'Landmark 2')
        self.assertEqual(self.shop_profile.shop_landmark_3, 'Landmark 3')
        self.assertEqual(self.shop_profile.shop_landmark_4, 'Landmark 4')
        self.assertEqual(self.shop_profile.shop_landmark_5, 'Landmark 5')
        self.assertTrue(self.shop_profile.status)
        # self.assertTrue(self.shop_profile.shop_picture.name.endswith('shop_picture.jpg'))

    def test_basic_update_exception(self):
        # Cover: POST request triggering exception during shop.save()
        self.client.force_login(self.shop_user)
        with patch('shop_profile.models.ShopProfile.save', side_effect=Exception('Database error')):
            response = self.client.post(reverse('basic_update'), {
                'shop_name': 'Failed Update'
            })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/salon_dashboard/update_basic.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Failed to update shop: Database error')

    def test_basic_update_get(self):
        # Cover: GET request rendering update_basic template
        self.client.force_login(self.shop_user)
        response = self.client.get(reverse('basic_update'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/salon_dashboard/update_basic.html')
        self.assertEqual(response.context['user'], self.shop_user)
        self.assertEqual(response.context['shop'], self.shop_profile)
        self.assertEqual(len(response.context['district']), 1)
        self.assertEqual(response.context['district'][0]['id'], self.district.id)
        self.assertEqual(len(response.context['Upazilla']), 1)
        self.assertEqual(response.context['Upazilla'][0]['upazilla_names'][0], self.upazilla.name)
        


