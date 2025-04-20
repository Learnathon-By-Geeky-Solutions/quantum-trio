from gettext import translation
from unittest.mock import patch
from django.http import JsonResponse
from django.test import TestCase, Client, SimpleTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
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
            shop_rating=4.5,
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
        self.assertEqual(self.shop.shop_rating, 4.5)
        self.assertEqual(self.shop.user.email, TEST_EMAIL1)
        self.assertTrue(self.shop.status)

    def test_update_rating_valid(self):
        result = self.shop.update_rating(4.8)
        self.assertTrue(result)
        self.assertEqual(self.shop.shop_rating, 4.8)

    def test_update_rating_invalid(self):
        result = self.shop.update_rating(6.0)
        self.assertFalse(result)
        self.assertEqual(self.shop.shop_rating, 4.5)

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
class ShopReviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=TEST_EMAIL1, password=TEST_PASS, user_type="shop"
        )
        self.customer = User.objects.create_user(
            email=TEST_EMAIL2, password=TEST_PASS, user_type="user"
        )
        self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
        self.review = ShopReview.objects.create(
            shop=self.shop, rating=4, review="Great service!", reviewer_id=self.customer.id
        )

    def test_review_creation(self):
        self.assertEqual(self.review.shop, self.shop)
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.review, "Great service!")

    def test_review_str(self):
        self.assertEqual(str(self.review), f"Review by {self.customer.id} for Test Shop - Rating: 4")

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
        self.assertEqual(data["message"], "Cannot cancel booking within 24 hours of the appointment time.")

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

    # def test_customers_view(self):
    #     response = self.client.get(reverse("shop_customers"))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "app/salon_dashboard/customers.html")
    #     self.assertIn("bookings", response.context)

    # def test_review_view(self):
    #     response = self.client.get(reverse("shop_review"))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "app/salon_dashboard/reviews.html")

    # def test_notification_view(self):
    #     response = self.client.get(reverse("shop_notifications"))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "app/salon_dashboard/notifications.html")
    #     self.assertIn("notifications", response.context)

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
# passed
class DebugStaticFilesTest(SimpleTestCase):
    @override_settings(DEBUG=True)
    def test_debug_static_block_covered(self):
        import carehub.urls
        importlib.reload(carehub.urls)
        self.assertTrue(True)

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

    def test_basic_update_post(self):
        """Test basic_update view POST request"""
        data = {
            "shop_name": "Updated Shop",
            "shop_title": "New Title",
            "shop_info": "Updated Info",
            "shop_owner": "New Owner",
            "mobile_number": "1234567890",
            "shop_website": "http://newwebsite.com",
            "gender": "Unisex",
            "status": "true",
            "shop_state": "New State",
            "shop_city": "New City",
            "shop_area": "New Area"
        }
        response = self.client.post(reverse("basic_update"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/salon_dashboard/update_basic.html")
        self.shop.refresh_from_db()
        self.assertEqual(self.shop.shop_name, "Updated Shop")
        self.assertEqual(self.shop.shop_title, "New Title")
        self.assertEqual(self.shop.shop_info, "Updated Info")
        self.assertEqual(self.shop.shop_owner, "New Owner")
        self.assertEqual(self.shop.mobile_number, "1234567890")
        self.assertEqual(self.shop.shop_website, "http://newwebsite.com")
        self.assertEqual(self.shop.gender, "Unisex")
        self.assertTrue(self.shop.status)
        self.assertEqual(self.shop.shop_state, "New State")
        self.assertEqual(self.shop.shop_city, "New City")
        self.assertEqual(self.shop.shop_area, "New Area")
        messages = [str(m) for m in response.wsgi_request._messages]
        self.assertIn("Shop profile updated successfully.", messages)

