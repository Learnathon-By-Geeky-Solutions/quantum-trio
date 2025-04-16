# from django.test import TestCase, Client
# from django.urls import reverse
# from django.contrib.auth import get_user_model
# from django.core.files.uploadedfile import SimpleUploadedFile
# from shop_profile.models import (
#     ShopProfile, ShopGallery, ShopWorker, ShopService, 
#     ShopReview, ShopSchedule, ShopNotification
# )
# from my_app.models import Item
# from booking.models import BookingSlot
# from datetime import date, time, datetime
# from django.utils import timezone
# import json

# User = get_user_model()

# TEST_PASS = "testpass123"
# TEST_EMAIL1 = "shop@example.com"   # TEST_EMAIL1
# TEST_EMAIL2 = "john@example.com"   # TEST_EMAIL2
# class ShopProfileTests(TestCase):
#     def setUp(self):
#         # Create a test user and shop profile
#         self.user = User.objects.create_user(
#             email=TEST_EMAIL1, password=TEST_PASS, user_type="shop"
#         )
#         self.shop = ShopProfile.objects.create(
#             user=self.user,
#             shop_name="Test Shop",
#             shop_rating=4.5,
#             shop_customer_count=10,
#             gender="Male",
#             status=True
#         )
#         self.client = Client()

#     def test_shop_profile_creation(self):
#         """Test that a ShopProfile is created correctly."""
#         self.assertEqual(self.shop.shop_name, "Test Shop")
#         self.assertEqual(self.shop.shop_rating, 4.5)
#         self.assertEqual(self.shop.user.email, TEST_EMAIL1)
#         self.assertTrue(self.shop.status)

#     def test_update_rating_valid(self):
#         """Test updating shop rating with a valid value."""
#         result = self.shop.update_rating(4.8)
#         self.assertTrue(result)
#         self.assertEqual(self.shop.shop_rating, 4.8)

#     def test_update_rating_invalid(self):
#         """Test updating shop rating with an invalid value."""
#         result = self.shop.update_rating(6.0)
#         self.assertFalse(result)
#         self.assertEqual(self.shop.shop_rating, 4.5)

#     def test_shop_profile_str(self):
#         """Test the string representation of ShopProfile."""
#         self.assertEqual(str(self.shop), "Test Shop")


# class ShopGalleryTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             email=TEST_EMAIL1, password=TEST_PASS, user_type="shop"
#         )
#         self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
#         self.client = Client()
#         self.client.login(email=TEST_EMAIL1, password=TEST_PASS)

#     def test_create_gallery_image(self):
#         """Test creating a gallery image."""
#         image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
#         gallery = ShopGallery.objects.create(shop=self.shop, image=image)
#         self.assertEqual(gallery.shop, self.shop)
#         self.assertTrue(gallery.image)

#     def test_gallery_view_post(self):
#         """Test the gallery view POST request to upload an image."""
#         image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
#         response = self.client.post(
#             reverse("shop_gallery"), {"image": image}, follow=True
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(ShopGallery.objects.count(), 1)
#         self.assertEqual(ShopGallery.objects.first().shop, self.shop)


# class ShopWorkerTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             email=TEST_EMAIL1, password=TEST_PASS, user_type="shop"
#         )
#         self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
#         self.item = Item.objects.create(name="Haircut", description="Basic haircut")
#         self.worker = ShopWorker.objects.create(
#             name="John Doe",
#             email=TEST_EMAIL2,
#             phone="1234567890",
#             experience=5,
#             shop=self.shop
#         )
#         self.worker.expertise.add(self.item)

# class ShopServiceTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             email=TEST_EMAIL1, password=TEST_PASS, user_type="shop"
#         )
#         self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
#         self.item = Item.objects.create(name="Haircut", description="Basic haircut")
#         self.service = ShopService.objects.create(
#             shop=self.shop, item=self.item, price=25.00
#         )

# class ShopReviewTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             email=TEST_EMAIL1, password=TEST_PASS, user_type="shop"
#         )
#         self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
#         self.review = ShopReview.objects.create(
#             shop=self.shop, rating=4, review="Great service!"
#         )

#     def test_review_creation(self):
#         """Test that a ShopReview is created correctly."""
#         self.assertEqual(self.review.shop, self.shop)
#         self.assertEqual(self.review.rating, 4)
#         self.assertEqual(self.review.review, "Great service!")


# class ShopScheduleTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             email=TEST_EMAIL1, password=TEST_PASS, user_type="shop"
#         )
#         self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
#         self.schedule = ShopSchedule.objects.create(
#             shop=self.shop,
#             day_of_week="Monday",
#             start=time(9, 0),
#             end=time(17, 0)
#         )

#     def test_schedule_creation(self):
#         """Test that a ShopSchedule is created correctly."""
#         self.assertEqual(self.schedule.shop, self.shop)
#         self.assertEqual(self.schedule.day_of_week, "Monday")
#         self.assertEqual(self.schedule.start, time(9, 0))
#         self.assertEqual(self.schedule.end, time(17, 0))

#     def test_schedule_str(self):
#         """Test the string representation of ShopSchedule."""
#         self.assertEqual(str(self.schedule), "Test Shop for Monday")


# class ShopNotificationTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             email=TEST_EMAIL1, password=TEST_PASS, user_type="shop"
#         )
#         self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
#         self.notification = ShopNotification.objects.create(
#             shop=self.shop,
#             title="New Booking",
#             message="You have a new booking!",
#             notification_type="booking"
#         )

#     def test_notification_creation(self):
#         """Test that a ShopNotification is created correctly."""
#         self.assertEqual(self.notification.shop, self.shop)
#         self.assertEqual(self.notification.title, "New Booking")
#         self.assertEqual(self.notification.notification_type, "booking")
#         self.assertFalse(self.notification.is_read)

#     def test_notification_str(self):
#         """Test the string representation of ShopNotification."""
#         self.assertEqual(str(self.notification), "New Booking - Test Shop (Unread)")


# class ViewTests(TestCase):
#     TEST_PASS = TEST_PASS
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(
#             email=TEST_EMAIL1, password=self.TEST_PASS, user_type="shop"
#         )
#         self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
#         self.item = Item.objects.create(name="Haircut", description="Basic haircut")
#         self.worker = ShopWorker.objects.create(
#             name="John Doe", email=TEST_EMAIL2, phone="1234567890", shop=self.shop
#         )
#         self.client.login(email=TEST_EMAIL1, password=self.TEST_PASS)

# class ViewTests1(TestCase):
#     TEST_PASS = TEST_PASS
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(
#             email=TEST_EMAIL1, password=self.TEST_PASS, user_type="shop"
#         )
#         self.shop = ShopProfile.objects.create(user=self.user, shop_name="Test Shop")
#         self.item = Item.objects.create(name="Haircut", description="Basic haircut")
#         self.worker = ShopWorker.objects.create(
#             name="John Doe", email=TEST_EMAIL2, phone="1234567890", shop=self.shop
#         )
#         self.client.login(email=TEST_EMAIL1, password=self.TEST_PASS)