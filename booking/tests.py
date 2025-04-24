from unittest.mock import patch
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import date, time, datetime
from booking.models import BookingSlot
from my_app.models import Item, Service
from user_profile.models import UserProfile
from shop_profile.models import MyUser, ShopProfile, ShopWorker, ShopService, ShopSchedule, ShopNotification
import uuid

User = get_user_model()

class BookingTests(TestCase):
    def setUp(self):
        # Create customer user and profile
        self.customer_user = User.objects.create_user(
            email=f"customer_{uuid.uuid4()}@example.com",
            password="test"# NOSONAR
        )
        self.user_profile = UserProfile.objects.create(
            user=self.customer_user,
            first_name="Customer",
            last_name="Test",
            phone_number="1234567890"
        )
        # Create shop user and profile
        self.shop_user = User.objects.create_user(
            email=f"shop_{uuid.uuid4()}@example.com",
            password="test",# NOSONAR
            user_type="shop"
        )
        self.shop_profile = ShopProfile.objects.create(
            user=self.shop_user,
            shop_name="Test Shop",
            shop_rating=4.5,
            status=True
        )
        # Create worker and item
        self.shop_worker = ShopWorker.objects.create(
            name="John Doe",
            shop=self.shop_profile,
            email=f"worker_{uuid.uuid4()}@example.com",
            phone="1234567890",
            experience=5
        )
        self.service = Service.objects.create(name="Haircare")
        self.item = Item.objects.create(
            name="Haircut",
            service=self.service,
            gender="Both"
        )
        self.shop_service = ShopService.objects.create(
            shop=self.shop_profile,
            item=self.item,
            price=15.0
        )
        self.shop_worker.expertise.add(self.item)
        # Create schedule
        self.schedule = ShopSchedule.objects.create(
            shop=self.shop_profile,
            day_of_week=date.today().strftime("%A"),
            start=time(9, 0),
            end=time(17, 0)
        )
        self.client = Client()

    # Model Tests
    def test_booking_slot_creation(self):
        """Test BookingSlot creation with defaults."""
        booking = BookingSlot.objects.create(
            user=self.user_profile,
            shop=self.shop_profile,
            worker=self.shop_worker,
            item=self.item,
            date=date.today(),
            time=time(10, 0),
            notes="Test booking"
        )
        self.assertEqual(booking.status, "pending")
        self.assertEqual(booking.payment_status, "unpaid")
        # self.assertFalse(booking.user_end)
        self.assertFalse(booking.shop_end)
        self.assertIsNotNone(booking.created_at)

    def test_booking_slot_auto_complete(self):
        """Test BookingSlot status updates to completed."""
        booking = BookingSlot.objects.create(
            user=self.user_profile,
            shop=self.shop_profile,
            worker=self.shop_worker,
            item=self.item,
            date=date.today(),
            time=time(10, 0)
        )
        booking.user_end = True
        booking.shop_end = True
        booking.save()
        self.assertEqual(booking.status, "completed")

    def test_booking_slot_str(self):
        """Test BookingSlot string representation."""
        booking = BookingSlot.objects.create(
            user=self.user_profile,
            shop=self.shop_profile,
            worker=self.shop_worker,
            item=self.item,
            date=date.today(),
            time=time(10, 0)
        )
        self.assertEqual(
            str(booking),
            f"Booking by {self.user_profile} at {self.shop_profile} on {date.today()} 10:00:00"
        )

    def test_booking_slot_status_transitions(self):
        """Test BookingSlot status transitions."""
        booking = BookingSlot.objects.create(
            user=self.user_profile,
            shop=self.shop_profile,
            worker=self.shop_worker,
            item=self.item,
            date=date.today(),
            time=time(10, 0)
        )
        booking.status = "confirmed"
        booking.save()
        self.assertEqual(booking.status, "confirmed")
        booking.status = "canceled"
        booking.save()
        self.assertEqual(booking.status, "canceled")

    # View Tests
    def test_booking_step_1_get(self):
        """Test GET request to booking_step_1."""
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/booking/book-step-1.html")
        self.assertIsNone(response.context["shop"])
        self.assertIsNone(response.context["service"])
        self.assertIsNone(response.context["workers"])

    def test_booking_step_1_post_valid(self):
        """Test POST request to booking_step_1 with valid data."""
        data = {
            "item_id": self.item.id,
            "shop_id": self.shop_profile.id
        }
        response = self.client.post(reverse("index"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/booking/book-step-1.html")
        self.assertEqual(response.context["shop"].id, self.shop_profile.id)
        self.assertEqual(response.context["service"].id, self.item.id)
        self.assertEqual(
            list(response.context["workers"])[0].id,
            self.shop_worker.id
        )

    def test_booking_step_1_post_invalid(self):
        """Test POST request to booking_step_1 with invalid data."""
        data = {
            "item_id": 999,
            "shop_id": 999
        }
        response = self.client.post(reverse("index"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/booking/book-step-1.html")
        self.assertIsNone(response.context["shop"])
        self.assertIsNone(response.context["service"])
        self.assertIsNone(response.context["workers"])

    def test_booking_step_2_get(self):
        """Test GET request to booking_step_2."""
        response = self.client.get(reverse("step-2"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/booking/book-step-2.html")
        self.assertIsNone(response.context["shop"])
        self.assertIsNone(response.context["service"])
        self.assertIsNone(response.context["worker"])

    def test_booking_step_2_post_valid(self):
        """Test POST request to booking_step_2 with valid data."""
        data = {
            "item_id": self.item.id,
            "shop_id": self.shop_profile.id,
            "worker_id": self.shop_worker.id
        }
        response = self.client.post(reverse("step-2"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/booking/book-step-2.html")
        self.assertEqual(response.context["shop"].id, self.shop_profile.id)
        self.assertEqual(response.context["service"].id, self.item.id)
        self.assertEqual(response.context["worker"].id, self.shop_worker.id)

    def test_booking_step_2_post_invalid(self):
        """Test POST request to booking_step_2 with invalid data."""
        data = {
            "item_id": "",
            "shop_id": "",
            "worker_id": ""
        }
        response = self.client.post(reverse("step-2"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/booking/book-step-2.html")
        self.assertIsNone(response.context["shop"])
        self.assertIsNone(response.context["service"])
        self.assertIsNone(response.context["worker"])

    def test_available_slots_missing_params(self):
        """Test available_slots with missing parameters."""
        response = self.client.get(reverse("available_slots"))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content.decode(), {"error": "Missing parameters"})

    def test_available_slots_invalid_date(self):
        """Test available_slots with invalid date."""
        params = {
            "shop_id": self.shop_profile.id,
            "worker_id": self.shop_worker.id,
            "item_id": self.item.id,
            "date": "2025-13-01"
        }
        response = self.client.get(reverse("available_slots"), params)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content.decode(), {"error": "Invalid date format. Use YYYY-MM-DD."})

    def test_success_get_unauthenticated(self):
        """Test success GET requires login."""
        response = self.client.get(reverse("success"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_success_post_valid(self):
        """Test POST to success creates booking and notification."""
        self.client.force_login(self.customer_user)
        data = {
            "item_id": self.item.id,
            "shop_id": self.shop_profile.id,
            "worker_id": self.shop_worker.id,
            "selected_date_id": date.today().strftime("%Y-%m-%d"),
            "selected_time_id": "10:00"
        }
        response = self.client.post(reverse("success"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/booking/success.html")
        self.assertEqual(BookingSlot.objects.count(), 1)
        booking = BookingSlot.objects.first()
        self.assertEqual(booking.user, self.user_profile)
        self.assertEqual(booking.shop, self.shop_profile)
        self.assertEqual(booking.worker, self.shop_worker)
        self.assertEqual(booking.item, self.item)
        self.assertEqual(booking.date.strftime("%Y-%m-%d"), date.today().strftime("%Y-%m-%d"))
        self.assertEqual(booking.time.strftime("%H:%M"), "10:00")
        self.assertEqual(booking.status, "pending")
        self.assertEqual(ShopNotification.objects.count(), 1)
        notification = ShopNotification.objects.first()
        self.assertEqual(notification.title, "New Booking Alert")

    def test_success_post_invalid(self):
        """Test POST to success with invalid data."""
        self.client.force_login(self.customer_user)
        data = {
            "item_id": 999,
            "shop_id": 999,
            "worker_id": 999,
            "selected_date_id": "",
            "selected_time_id": ""
        }
        response = self.client.post(reverse("success"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/booking/success.html")
        self.assertEqual(BookingSlot.objects.count(), 0)
        self.assertEqual(ShopNotification.objects.count(), 0)
class BookingViewsTest(TestCase):
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
        self.worker = ShopWorker.objects.create(
            name="Test Worker",
            email="worker@example.com",
            phone="1234567890",
            experience=5.0,
            shop=self.shop,
            rating=0.0
        )
        # Create a shop schedule for Monday
        self.schedule = ShopSchedule.objects.create(
            shop=self.shop,
            day_of_week="Monday",
            start=time(9, 0),  # 9:00 AM
            end=time(17, 0)    # 5:00 PM
        )
        self.client.login(email="shop@example.com", password="password123")

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, time, datetime, timedelta
from my_app.models import Division, District, Upazilla, Area, Service, Item
from shop_profile.models import ShopProfile, ShopService, ShopWorker, ShopSchedule
from user_profile.models import UserProfile
from booking.models import BookingSlot
import json

UserModel = get_user_model()

class BookingUncoveredTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create test user and profile
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

        # Create shop schedule for Monday
        self.schedule = ShopSchedule.objects.create(
            shop=self.shop_profile,
            day_of_week='Monday',
            start=time(9, 0),  # 9:00 AM
            end=time(12, 0)    # 12:00 PM
        )

    def test_get_available_time_slots(self):
        # Cover: return [slot.strftime("%H:%M") for slot in time_slots if slot not in booked]
        date_obj = date(2025, 5, 5)  # A Monday in the future
        # Create a booked slot
        BookingSlot.objects.create(
            user=self.user_profile,
            shop=self.shop_profile,
            worker=self.shop_worker,
            item=self.item,
            status='pending',
            date=date_obj,
            time=time(10, 0),  # Book 10:00 AM
            payment_status='unpaid',
            user_end=True,
            shop_end=False,
            notes='',
            rated=False
        )
        # Expected slots: 09:00, 11:00 (10:00 is booked)
        from booking.views import get_available_time_slots
        slots = get_available_time_slots(self.shop_profile.id, self.shop_worker.id, date_obj)
        self.assertEqual(slots, ['09:00', '11:00'])

    def test_available_slots_view(self):
        # Cover: slots = get_available_time_slots(...) and return JsonResponse(slots, safe=False)
        date_obj = date(2025, 5, 5)  # A Monday in the future
        # Create a booked slot
        BookingSlot.objects.create(
            user=self.user_profile,
            shop=self.shop_profile,
            worker=self.shop_worker,
            item=self.item,
            status='pending',
            date=date_obj,
            time=time(10, 0),  # Book 10:00 AM
            payment_status='unpaid',
            user_end=True,
            shop_end=False,
            notes='',
            rated=False
        )
        # Send GET request to available_slots
        response = self.client.get(reverse('available_slots'), {
            'shop_id': str(self.shop_profile.id),
            'worker_id': str(self.shop_worker.id),
            'item_id': str(self.item.id),
            'date': date_obj.strftime('%Y-%m-%d')
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, ['09:00', '11:00'])