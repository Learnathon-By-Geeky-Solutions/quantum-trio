from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from shop_profile.models import (
    ShopProfile, ShopGallery, ShopWorker, ShopService, 
    ShopReview, ShopSchedule, ShopNotification
)
from my_app.models import Item
from booking.models import BookingSlot
from datetime import date, time, datetime
from django.utils import timezone
import json

User = get_user_model()

class ShopProfileTests(TestCase):
    def setUp(self):
        # Create a test user and shop profile
        self.user = User.objects.create_user(
            email="shop@example.com", password="testpass123", user_type="shop"
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

    def test_shop_profile_creation(self):
        """Test that a ShopProfile is created correctly."""
        self.assertEqual(self.shop.shop_name, "Test Shop")
        self.assertEqual(self.shop.shop_rating, 4.5)
        self.assertEqual(self.shop.user.email, "shop@example.com")
        self.assertTrue(self.shop.status)

    def test_update_rating_valid(self):
        """Test updating shop rating with a valid value."""
        result = self.shop.update_rating(4.8)
        self.assertTrue(result)
        self.assertEqual(self.shop.shop_rating, 4.8)

    def test_update_rating_invalid(self):
        """Test updating shop rating with an invalid value."""
        result = self.shop.update_rating(6.0)
        self.assertFalse(result)
        self.assertEqual(self.shop.shop_rating, 4.5)

    def test_shop_profile_str(self):
        """Test the string representation of ShopProfile."""
        self.assertEqual(str(self.shop), "Test Shop")


class ShopGalleryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="shop@example.com", password="testpass123", user_type="shop"
        )
        self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
        self.client = Client()
        self.client.login(email="shop@example.com", password="testpass123")

    def test_create_gallery_image(self):
        """Test creating a gallery image."""
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        gallery = ShopGallery.objects.create(shop=self.shop, image=image)
        self.assertEqual(gallery.shop, self.shop)
        self.assertTrue(gallery.image)

    def test_gallery_view_post(self):
        """Test the gallery view POST request to upload an image."""
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(
            reverse("shop_gallery"), {"image": image}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ShopGallery.objects.count(), 1)
        self.assertEqual(ShopGallery.objects.first().shop, self.shop)


class ShopWorkerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="shop@example.com", password="testpass123", user_type="shop"
        )
        self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
        self.item = Item.objects.create(name="Haircut", description="Basic haircut")
        self.worker = ShopWorker.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="1234567890",
            experience=5,
            shop=self.shop
        )
        self.worker.expertise.add(self.item)

    # def test_worker_creation(self):
    #     """Test that a ShopWorker is created correctly."""
    #     self.assertEqual(self.worker.name, "John Doe")
    #     self.assertEqual(self.worker.experience, 5)
    #     self.assertEqual(self.worker.shop, self.shop)
    #     self.assertIn(self.item, self.worker.expertise.all())

    # def test_worker_str(self):
    #     """Test the string representation of ShopWorker."""
    #     self.assertEqual(str(self.worker), "John Doe (5 years experience)")


class ShopServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="shop@example.com", password="testpass123", user_type="shop"
        )
        self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
        self.item = Item.objects.create(name="Haircut", description="Basic haircut")
        self.service = ShopService.objects.create(
            shop=self.shop, item=self.item, price=25.00
        )

    # def test_service_creation(self):
    #     """Test that a ShopService is created correctly."""
    #     self.assertEqual(self.service.shop, self.shop)
    #     self.assertEqual(self.service.item, self.item)
    #     self.assertEqual(self.service.price, 25.00)

    # def test_service_str(self):
    #     """Test the string representation of ShopService."""
    #     self.assertEqual(str(self.service), "Test Shop - Haircut")


class ShopReviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="shop@example.com", password="testpass123", user_type="shop"
        )
        self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
        self.review = ShopReview.objects.create(
            shop=self.shop, rating=4, review="Great service!"
        )

    def test_review_creation(self):
        """Test that a ShopReview is created correctly."""
        self.assertEqual(self.review.shop, self.shop)
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.review, "Great service!")


class ShopScheduleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="shop@example.com", password="testpass123", user_type="shop"
        )
        self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
        self.schedule = ShopSchedule.objects.create(
            shop=self.shop,
            day_of_week="Monday",
            start=time(9, 0),
            end=time(17, 0)
        )

    def test_schedule_creation(self):
        """Test that a ShopSchedule is created correctly."""
        self.assertEqual(self.schedule.shop, self.shop)
        self.assertEqual(self.schedule.day_of_week, "Monday")
        self.assertEqual(self.schedule.start, time(9, 0))
        self.assertEqual(self.schedule.end, time(17, 0))

    def test_schedule_str(self):
        """Test the string representation of ShopSchedule."""
        self.assertEqual(str(self.schedule), "Test Shop for Monday")


class ShopNotificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="shop@example.com", password="testpass123", user_type="shop"
        )
        self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
        self.notification = ShopNotification.objects.create(
            shop=self.shop,
            title="New Booking",
            message="You have a new booking!",
            notification_type="booking"
        )

    def test_notification_creation(self):
        """Test that a ShopNotification is created correctly."""
        self.assertEqual(self.notification.shop, self.shop)
        self.assertEqual(self.notification.title, "New Booking")
        self.assertEqual(self.notification.notification_type, "booking")
        self.assertFalse(self.notification.is_read)

    def test_notification_str(self):
        """Test the string representation of ShopNotification."""
        self.assertEqual(str(self.notification), "New Booking - Test Shop (Unread)")


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="shop@example.com", password="testpass123", user_type="shop"
        )
        self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
        self.item = Item.objects.create(name="Haircut", description="Basic haircut")
        self.worker = ShopWorker.objects.create(
            name="John Doe", email="john@example.com", phone="1234567890", shop=self.shop
        )
        self.client.login(email="shop@example.com", password="testpass123")

    # def test_profile_view(self):
    #     """Test the profile view."""
    #     response = self.client.get(reverse("shop_profile"))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "app/salon_dashboard/index.html")

    # def test_appointments_view(self):
    #     """Test the appointments view."""
    #     response = self.client.get(reverse("appointments"))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "app/salon_dashboard/appointments.html")

    # def test_slots_view(self):
    #     """Test the slots view."""
    #     response = self.client.get(reverse("shop_booking_slots"))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "app/salon_dashboard/booking-slots.html")

    # def test_accept_booking(self):
    #     """Test accepting a booking."""
    #     booking = BookingSlot.objects.create(
    #         user=self.user,
    #         shop=self.shop,
    #         worker=self.worker,
    #         item=self.item,
    #         date=date.today(),
    #         time=time(10, 0),
    #         status="pending"
    #     )
    #     response = self.client.post(
    #         reverse("accept_booking"),
    #         json.dumps({"booking_id": booking.id}),
    #         content_type="application/json"
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     booking.refresh_from_db()
    #     self.assertEqual(booking.status, "confirmed")

    # def test_reject_booking(self):
    #     """Test rejecting a booking."""
    #     booking = BookingSlot.objects.create(
    #         user=self.user,
    #         shop=self.shop,
    #         worker=self.worker,
    #         item=self.item,
    #         date=date.today(),
    #         time=time(10, 0),
    #         status="pending"
    #     )
    #     response = self.client.post(
    #         reverse("reject_booking"),
    #         json.dumps({"booking_id": booking.id}),
    #         content_type="application/json"
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     booking.refresh_from_db()
    #     self.assertEqual(booking.status, "rejected")

    # def test_booking_details(self):
    #     """Test retrieving booking details."""
    #     booking = BookingSlot.objects.create(
    #         user=self.user,
    #         shop=self.shop,
    #         worker=self.worker,
    #         item=self.item,
    #         date=date.today(),
    #         time=time(10, 0),
    #         status="pending"
    #     )
    #     ShopService.objects.create(shop=self.shop, item=self.item, price=25.00)
    #     response = self.client.post(
    #         reverse("booking_details"),
    #         json.dumps({"booking_id": booking.id}),
    #         content_type="application/json"
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertJSONEqual(
    #         response.content,
    #         {
    #             "success": True,
    #             "details": {
    #                 "full_name": "",
    #                 "item_name": "Haircut",
    #                 "item_price": "25.0",
    #                 "booked_time": booking.time.strftime("%I:%M %p"),
    #                 "booked_date": booking.date.strftime("%d-%m-%Y"),
    #                 "status": "pending",
    #                 "booking_time": booking.time.strftime("%I:%M %p")
    #             }
    #         }
    #     )

    # def test_add_worker_post(self):
    #     """Test adding a worker via POST request."""
    #     data = {
    #         "name": "Jane Doe",
    #         "email": "jane@example.com",
    #         "phone": "0987654321",
    #         "experience": "3",
    #         "expertise": [str(self.item.id)]
    #     }
    #     response = self.client.post(reverse("add_worker"), data)
    #     self.assertEqual(response.status_code, 302)  # Redirects to shop_staffs
    #     self.assertEqual(ShopWorker.objects.count(), 1)
    #     worker = ShopWorker.objects.first()
    #     self.assertEqual(worker.name, "Jane Doe")
    #     self.assertEqual(worker.expertise.count(), 1)