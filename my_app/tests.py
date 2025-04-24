from datetime import date, time
from decimal import Decimal
import decimal
from unittest.mock import patch
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

from booking.tests import User
from my_app.views import area_database
from .models import Division, District, Upazilla, Area, Landmark, Service, Item, ReviewCarehub, Contact
from user_profile.models import UserProfile
from shop_profile.models import ShopProfile, ShopService, ShopWorker, ShopReview
from booking.models import BookingSlot
from django.contrib.auth import get_user_model
import json

UserModel = get_user_model()

class MyAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        # Create test user with UserProfile
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

        # Create test shop user with ShopProfile
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
            gender='Male',
            mobile_number='0987654321'
        )

        # Create location hierarchy
        self.division = Division.objects.create(name='Test Division')
        self.district = District.objects.create(name='Test District', division=self.division)
        self.upazilla = Upazilla.objects.create(name='Test Upazilla', district=self.district)
        self.area = Area.objects.create(name='Test Area', upazilla=self.upazilla)
        self.landmark = Landmark.objects.create(name='Test Landmark', area=self.area)

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

    # Model Tests
    def test_division_str(self):
        self.assertEqual(str(self.division), 'Test Division')

    def test_district_str(self):
        self.assertEqual(str(self.district), 'Test District')

    def test_upazilla_str(self):
        self.assertEqual(str(self.upazilla), 'Test Upazilla, Test District')

    def test_area_str(self):
        self.assertEqual(str(self.area), 'Test Area, Test Upazilla')

    def test_landmark_str(self):
        self.assertEqual(str(self.landmark), 'Test Landmark, Test Area')

    def test_service_str(self):
        self.assertEqual(str(self.service), 'Test Service')

    def test_item_str(self):
        self.assertEqual(str(self.item), 'Test Item,   Test Service')  # Match extra spaces

    def test_contact_str(self):
        contact = Contact.objects.create(
            name='Test Contact',
            email='contact@example.com',
            subject='Test Subject',
            message='Test Message'
        )
        self.assertEqual(str(contact), 'Test Contact - Test Subject')

    def test_home_view_non_get(self):
        response = self.client.post(reverse('home'))
        self.assertEqual(response.status_code, 405)

    def test_submit_review_unauthenticated(self):
        response = self.client.post(reverse('submit_review'), {
            'review': 'Great service!',
            'rating': '4.5'
        })
        self.assertEqual(response.status_code, 400)

    def test_log_in_view_get(self):
        response = self.client.get(reverse('login'), {'profile-type': 'customer'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/login.html')
        self.assertEqual(response.context['type'], 'customer')

    def test_log_in_view_post_invalid(self):
        response = self.client.post(reverse('login'), {
            'email': 'testuser@example.com',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/login.html')
        self.assertEqual(response.context['message'], 'Invalid email or password')

    def test_log_out_view(self):
        self.client.login(email='testuser@example.com', password='testpass123')
        response = self.client.get(reverse('logout'))  # Verify in urls.py
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_contact_us_post(self):
        response = self.client.post(reverse('contact'), {  # Verify in urls.py
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test Message'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/contact_us.html')
        self.assertTrue(Contact.objects.filter(name='Test User').exists())

    def test_search_view_post(self):
        response = self.client.post(reverse('search'), {'search': 'Test Shop'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/search.html')
        self.assertIn(self.shop_profile, response.context['shops'])
        self.assertEqual(response.context['keyword'], 'Test Shop')

    def test_service_view(self):
        response = self.client.get(reverse('service'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/service.html')
        self.assertIn(self.service, response.context['services'])

    def test_location_view(self):
        response = self.client.get(reverse('location'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/location.html')
        self.assertIn(self.division, response.context['divisions'])
        self.assertIn(self.district, response.context['districts'])


    def test_items_view(self):
        response = self.client.get(reverse('items'), {'service': 'Test Service'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/items.html')
        self.assertIn(self.item, response.context['items'])
        self.assertEqual(response.context['service'], 'Test Service')

    def test_submit_shop_review_no_booking(self):
        self.client.login(email='testuser@example.com', password='testpass123')
        response = self.client.post(reverse('submit_shop_review'), {
            'rating': '4',
            'review': 'Great shop!',
            'shop_id': self.shop_profile.id
        })
        self.assertEqual(response.status_code, 404)  # JSON response
        self.assertJSONEqual(response.content, {'success': False, 'error': 'You are not allowed.'})

  
    def submit_shop_review(request):
        try:
            rating = request.POST.get('rating')
            review = request.POST.get('review')
            shop_id = request.POST.get('shop_id')
            user_id = request.user.id
            shop = ShopProfile.objects.get(id=shop_id)
            if not rating or not review or not shop_id or not user_id:
                return JsonResponse({'success': False, 'error': 'Fill all the required fields.'}, status=400)
            if not BookingSlot.objects.filter(user__id=user_id, shop__id=shop_id, status='completed').exists():
                return JsonResponse({'success': False, 'error': 'You are not allowed.'}, status=200)  # Changed to 200
            ShopReview.objects.create(
                rating=rating,
                review=review,
                shop=shop,
                reviewer_id=user_id
            )
            return JsonResponse({'success': True}, status=200)
        except ShopProfile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Shop not found.'}, status=404)
        except Exception as e:
            import logging
            logging.error("An error occurred: %s", str(e), exc_info=True)
            return JsonResponse({'success': False, 'error': 'An internal error occurred.'}, status=500)
 
    def test_shop_profile_view(self):
        self.client.login(email='testuser@example.com', password='testpass123')
        response = self.client.get(reverse('salon-profile'), {'shop_id': self.shop_profile.id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/saloon_profile/dashboard.html')
        self.assertEqual(response.context['shop'], self.shop_profile)
        self.assertIn(self.shop_service, response.context['shop_services'])
        self.assertIn(self.shop_worker, response.context['shop_workers'])
    
    def test_shop_profile_invalid_id(self):
        self.client.login(email='testuser@example.com', password='testpass123')
        response = self.client.get(reverse('salon-profile'), {'shop_id': 'invalid'})
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Invalid shop ID"})


class AdditionalMyAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        # Create test user with UserProfile
        self.user = UserModel.objects.create_user(
            email='adduser@example.com',
            password='addpass123',
            user_type='user'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            first_name='Add',
            last_name='User',
            gender='Female',
            phone_number='9876543210'
        )

        # Create test shop user with ShopProfile
        self.shop_user = UserModel.objects.create_user(
            email='addshop@example.com',
            password='addshop123',
            user_type='shop'
        )
        self.shop_profile = ShopProfile.objects.create(
            user=self.shop_user,
            shop_name='Add Shop',
            shop_title='Add Title',
            shop_info='Add Info',
            shop_state='Add District',
            shop_city='Add Upazilla',
            shop_area='Add Area',
            shop_rating=4.0,
            shop_customer_count=50,
            gender='Both',
            mobile_number='0123456789'
        )

        # Create location hierarchy
        self.division = Division.objects.create(name='Add Division')
        self.district = District.objects.create(name='Add District', division=self.division)
        self.upazilla = Upazilla.objects.create(name='Add Upazilla', district=self.district)
        self.area = Area.objects.create(name='Add Area', upazilla=self.upazilla)
        self.landmark = Landmark.objects.create(name='Add Landmark', area=self.area)

        # Create service and item
        self.service = Service.objects.create(name='Add Service')
        self.item = Item.objects.create(
            name='Add Item',
            item_description='Add Description',
            service=self.service,
            gender='Both'
        )

        # Create shop service
        self.shop_service = ShopService.objects.create(
            shop=self.shop_profile,
            item=self.item,
            price=75.00
        )

        # Create shop worker
        self.shop_worker = ShopWorker.objects.create(
            shop=self.shop_profile,
            name='Add Worker',
            email='addworker@example.com',
            phone='0987654321',
            experience=3.0
        )

    def test_select_user_type_view(self):
        response = self.client.get(reverse('select_user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/select_user_type.html')

    def test_create_account_view(self):
        response = self.client.get(reverse('select_user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/select_user_type.html')

    def test_submit_review_authenticated_user(self):
        self.client.login(email='adduser@example.com', password='addpass123')
        response = self.client.post(reverse('submit_review'), {
            'review': 'Fantastic service!',
            'rating': '4.5'
        })
        self.assertEqual(response.status_code, 302)
        review = ReviewCarehub.objects.get(comment='Fantastic service!')
        self.assertEqual(review.rating, decimal.Decimal('4.5'))
        self.assertEqual(review.reviewer_type, ContentType.objects.get_for_model(self.user_profile))
        self.assertEqual(review.reviewer_id, self.user_profile.id)

    def test_submit_review_authenticated_shop(self):
        self.client.login(email='addshop@example.com', password='addshop123')
        response = self.client.post(reverse('submit_review'), {
            'review': 'Great platform!',
            'rating': '5.0'
        })
        self.assertEqual(response.status_code, 302)
        review = ReviewCarehub.objects.get(comment='Great platform!')
        self.assertEqual(review.rating, decimal.Decimal('5.0'))
        self.assertEqual(review.reviewer_type, ContentType.objects.get_for_model(self.shop_profile))
        self.assertEqual(review.reviewer_id, self.shop_profile.id)

    def test_submit_review_invalid_rating(self):
        self.client.login(email='adduser@example.com', password='addpass123')
        response = self.client.post(reverse('submit_review'), {
            'review': 'Invalid rating test',
            'rating': '6.0'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ReviewCarehub.objects.filter(comment='Invalid rating test').exists())

    def test_fetch_by_items_view(self):
        response = self.client.get(reverse('fetch_by_items'), {
            'item': 'Add Item',
            'district': 'Add District',
            'limit': 5,
            'offset': 0
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['shop']), 1)
        self.assertEqual(data['shop'][0]['shop_name'], 'Add Shop')
        self.assertFalse(data['has_next'])
        self.assertFalse(data['has_previous'])

    def test_fetch_by_items_no_results(self):
        response = self.client.get(reverse('fetch_by_items'), {
            'item': 'Nonexistent Item',
            'limit': 5,
            'offset': 0
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['shop']), 0)
        self.assertFalse(data['has_next'])
        self.assertFalse(data['has_previous'])

    def test_about_us_view(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/about_us.html')

    def test_privacy_policy_view(self):
        response = self.client.get(reverse('privacy_policy'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/privacy_policy.html')

    def test_terms_conditions_view(self):
        response = self.client.get(reverse('terms_conditions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/terms_conditions.html')

    def test_submit_shop_review_missing_fields(self):
        self.client.login(email='adduser@example.com', password='addpass123')
        response = self.client.post(reverse('submit_shop_review'), {
            'rating': '5',
            'shop_id': self.shop_profile.id
        })
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {'success': False, 'error': 'Fill all the required fields.'})

    def test_search_view_item_based(self):
        response = self.client.post(reverse('search'), {'search': 'Add Item'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/search.html')
        self.assertIn(self.item, response.context['items'])
        self.assertIn(self.shop_profile, response.context['service_based'])
        self.assertEqual(response.context['keyword'], 'Add Item')

    def test_contact_us_invalid_email(self):
        response = self.client.post(reverse('contact'), {
            'name': 'Add User',
            'email': 'invalid-email',
            'subject': 'Add Subject',
            'message': 'Add Message'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/contact_us.html')
        self.assertTrue(Contact.objects.filter(email='invalid-email').exists())
        self.assertContains(response, 'Your message has been sent successfully', status_code=200)

#passed
class CoverageMyAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        # Create test users
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

        # Create second shop user to avoid unique constraint
        self.shop_user2 = UserModel.objects.create_user(
            email='shopuser2@example.com',
            password='shoppass456',
            user_type='shop'
        )
        self.shop_profile2 = ShopProfile.objects.create(
            user=self.shop_user2,
            shop_name='Test Shop 2',
            shop_title='Test Title 2',
            shop_info='Test Info 2',
            shop_state='Test District',
            shop_city='Test Upazilla 2',
            shop_area='Test Area',
            shop_rating=3.5,
            shop_customer_count=50,
            gender='Both',
            mobile_number='0123456789'
        )

        # Create admin user
        self.admin_user = UserModel.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            user_type='admin'
        )

        # Create user without profile for invalid reviewer test
        self.no_profile_user = UserModel.objects.create_user(
            email='noprofile@example.com',
            password='nopass123',
            user_type='user'
        )

        # Create location hierarchy
        self.division = Division.objects.create(name='Test Division')
        self.district = District.objects.create(name='Test District', division=self.division)
        self.upazilla = Upazilla.objects.create(name='Test Upazilla', district=self.district)
        self.upazilla2 = Upazilla.objects.create(name='Test Upazilla 2', district=self.district)
        self.area = Area.objects.create(name='Test Area', upazilla=self.upazilla)
        self.landmark = Landmark.objects.create(name='Test Landmark', area=self.area)

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

    def test_home_non_get(self):
        # Test non-GET request to home
        response = self.client.post(reverse('home'))
        self.assertEqual(response.status_code, 405)
        self.assertIsInstance(response, HttpResponseNotAllowed)

    def test_submit_review_invalid_reviewer(self):
        # Test user without shop_profile or user_profile
        self.client.login(email='noprofile@example.com', password='nopass123')
        response = self.client.post(reverse('submit_review'), {
            'review': 'Test review',
            'rating': '4.0'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), 'Invalid reviewer')

    def test_submit_shop_review_shop_not_found(self):
        # Test ShopProfile.DoesNotExist exception
        self.client.login(email='testuser@example.com', password='testpass123')
        response = self.client.post(reverse('submit_shop_review'), {
            'rating': '4',
            'review': 'Great shop!',
            'shop_id': 999  # Non-existent shop_id
        })
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {'success': False, 'error': 'Shop not found.'})


class CoverageMyAppTestsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        # Create test users
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

        self.shop_user2 = UserModel.objects.create_user(
            email='shopuser2@example.com',
            password='shoppass456',
            user_type='shop'
        )
        self.shop_profile2 = ShopProfile.objects.create(
            user=self.shop_user2,
            shop_name='Test Shop 2',
            shop_title='Test Title 2',
            shop_info='Test Info 2',
            shop_state='Test District',
            shop_city='Test Upazilla 2',
            shop_area='Test Area',
            shop_rating=3.5,
            shop_customer_count=50,
            gender='Both',
            mobile_number='0123456789'
        )

        # Create admin user
        self.admin_user = UserModel.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            user_type='admin'
        )

        # Create user without profile for invalid reviewer test
        self.no_profile_user = UserModel.objects.create_user(
            email='noprofile@example.com',
            password='nopass123',
            user_type='user'
        )

        # Create location hierarchy
        self.division = Division.objects.create(name='Test Division')
        self.district = District.objects.create(name='Test District', division=self.division)
        self.upazilla = Upazilla.objects.create(name='Test Upazilla', district=self.district)
        self.upazilla2 = Upazilla.objects.create(name='Test Upazilla 2', district=self.district)
        self.area = Area.objects.create(name='Test Area', upazilla=self.upazilla)
        self.landmark = Landmark.objects.create(name='Test Landmark', area=self.area)

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

class CoverageMyAppTestsTests1(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        # Create test users
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

        self.shop_user2 = UserModel.objects.create_user(
            email='shopuser2@example.com',
            password='shoppass456',
            user_type='shop'
        )
        self.shop_profile2 = ShopProfile.objects.create(
            user=self.shop_user2,
            shop_name='Test Shop 2',
            shop_title='Test Title 2',
            shop_info='Test Info 2',
            shop_state='Test District',
            shop_city='Test Upazilla 2',
            shop_area='Test Area',
            shop_rating=3.5,
            shop_customer_count=50,
            gender='Both',
            mobile_number='0123456789'
        )

        # Create admin user
        self.admin_user = UserModel.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            user_type='admin'
        )

        # Create user without profile for invalid reviewer test
        self.no_profile_user = UserModel.objects.create_user(
            email='noprofile@example.com',
            password='nopass123',
            user_type='user'
        )

        # Create location hierarchy
        self.division = Division.objects.create(name='Test Division')
        self.district = District.objects.create(name='Test District', division=self.division)
        self.upazilla = Upazilla.objects.create(name='Test Upazilla', district=self.district)
        self.upazilla2 = Upazilla.objects.create(name='Test Upazilla 2', district=self.district)
        self.area = Area.objects.create(name='Test Area', upazilla=self.upazilla)
        self.landmark = Landmark.objects.create(name='Test Landmark', area=self.area)

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

    def test_submit_shop_review_general_exception(self):
        self.client.login(email='testuser@example.com', password='testpass123')
        BookingSlot.objects.create(
            user=self.user_profile,
            shop=self.shop_profile,
            status='completed',
            date=date(2025, 4, 24),
            time=time(12, 0),
            payment_status='unpaid',
            item=self.item,
            worker=self.shop_worker
        )
        with patch('shop_profile.models.ShopReview.objects.create', side_effect=Exception('Database error')):
            response = self.client.post(reverse('submit_shop_review'), {
                'rating': '4',
                'review': 'Great shop!',
                'shop_id': self.shop_profile.id,
                'user_id': self.user_profile.id
            })
        self.assertEqual(response.status_code, 500)

    def test_fetch_shop_filters_and_sorting(self):
        response = self.client.get(reverse('fetch_shop'), {
            'district': 'Test District',
            'upazila': 'Test Upazilla',
            'area': 'Test Area',
            'limit': 5,
            'offset': 0
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['shop_name'], 'Test Shop')
        self.assertEqual(data[0]['shop_rating'], '4.5')

        response = self.client.get(reverse('fetch_shop'), {
            'district': 'Test District',
            'limit': 5,
            'offset': 0
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['shop_name'], 'Test Shop')
        self.assertEqual(data[1]['shop_name'], 'Test Shop 2')



from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.db.models import Q
from django.http import HttpResponseNotAllowed
from .models import Division, District, Upazilla, Area, Landmark, Service, Item, Contact, ReviewCarehub
from shop_profile.models import ShopProfile, ShopService, ShopWorker
from user_profile.models import UserProfile
from booking.models import BookingSlot
from unittest.mock import patch
from datetime import date, time

UserModel = get_user_model()

class UncoveredMyAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        # Create test users
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

        self.shop_user2 = UserModel.objects.create_user(
            email='shopuser2@example.com',
            password='shoppass456',
            user_type='shop'
        )
        self.shop_profile2 = ShopProfile.objects.create(
            user=self.shop_user2,
            shop_name='Test Shop 2',
            shop_title='Test Title 2',
            shop_info='Test Info 2',
            shop_state='Test District',
            shop_city='Test Upazilla 2',
            shop_area='Test Area',
            shop_rating=3.5,
            shop_customer_count=50,
            gender='Both',
            mobile_number='0123456789'
        )

        self.admin_user = UserModel.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            user_type='admin'
        )

        self.no_profile_user = UserModel.objects.create_user(
            email='noprofile@example.com',
            password='nopass123',
            user_type='user'
        )

        # Create location hierarchy
        self.division = Division.objects.create(name='Test Division')
        self.district = District.objects.create(name='Test District', division=self.division)
        self.upazilla = Upazilla.objects.create(name='Test Upazilla', district=self.district)
        self.upazilla2 = Upazilla.objects.create(name='Test Upazilla 2', district=self.district)
        self.area = Area.objects.create(name='Test Area', upazilla=self.upazilla)
        self.landmark = Landmark.objects.create(name='Test Landmark', area=self.area)

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

    def test_home_non_get(self):
        # Cover: if request.method != 'GET' in home
        response = self.client.post(reverse('home'))
        self.assertEqual(response.status_code, 405)
        self.assertIsInstance(response, HttpResponseNotAllowed)


    def test_contact_us_exception(self):
        # Cover: except Exception block in contact_us
        with patch('my_app.models.Contact.objects.create', side_effect=Exception('Database error')):
            response = self.client.post(reverse('contact'), {
                'name': 'Test User',
                'email': 'test@example.com',
                'subject': 'Test Subject',
                'message': 'Test Message'
            })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/contact_us.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Something went wrong: Database error')


class UniqueCoverageMyAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        # Create test users
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

        self.shop_user2 = UserModel.objects.create_user(
            email='shopuser2@example.com',
            password='shoppass456',
            user_type='shop'
        )
        self.shop_profile2 = ShopProfile.objects.create(
            user=self.shop_user2,
            shop_name='Test Shop 2',
            shop_title='Test Title 2',
            shop_info='Test Info 2',
            shop_state='Test District',
            shop_city='Test Upazilla 2',
            shop_area='Test Area',
            shop_rating=3.5,
            shop_customer_count=50,
            gender='Both',
            mobile_number='0123456789'
        )

        self.admin_user = UserModel.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            user_type='admin'
        )

        # Create location hierarchy
        self.division = Division.objects.create(name='Test Division')
        self.district = District.objects.create(name='Test District', division=self.division)
        self.upazilla = Upazilla.objects.create(name='Test Upazilla', district=self.district)
        self.upazilla2 = Upazilla.objects.create(name='Test Upazilla 2', district=self.district)
        self.area = Area.objects.create(name='Test Area', upazilla=self.upazilla)
        self.landmark = Landmark.objects.create(name='Test Landmark', area=self.area)

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

    def test_log_in_admin_user(self):
        # Cover: else branch for admin user type in log_in
        self.client.login(email='admin@example.com', password='adminpass123')
        response = self.client.post(reverse('login'), {
            'email': 'admin@example.com',
            'password': 'adminpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    # def test_success_reset_password(self):
    #     # Cover: success_reset_password function
    #     response = self.client.get(reverse('password_reset_complete'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.content.decode(), 'Password reset successful. This is a test response.')
    #     self.assertIsInstance(response, HttpResponse)


    def test_book_now_non_get(self):
        # Cover: else branch in book_now
        response = self.client.post(reverse('booknow'))
        self.assertEqual(response.status_code, 405)
        self.assertIsInstance(response, HttpResponseNotAllowed)

    # def test_fetch_shop_filters(self):
    #     # Cover: upazilla and area filters in fetch_shop
    #     # Test with upazila filter
    #     response = self.client.get(reverse('fetch_shop'), {
    #         'upazila': 'Test Upazilla',
    #         'limit': 5,
    #         'offset': 0
    #     })
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.content)
    #     self.assertEqual(len(data), 1)
    #     self.assertEqual(data[0]['shop_name'], 'Test Shop')
    #     self.assertEqual(data[0]['shop_city'], 'Test Upazilla')

    #     # Test with area filter
    #     response = self.client.get(reverse('fetch_shop'), {
    #         'area': 'Test Area',
    #         'limit': 5,
    #         'offset': 0
    #     })
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.content)
    #     self.assertEqual(len(data), 2)
    #     self.assertEqual(data[0]['shop_name'], 'Test Shop')
    #     self.assertEqual(data[1]['shop_name'], 'Test Shop 2')
    #     self.assertTrue(all(s['shop_area'] == 'Test Area' for s in data))

    def test_explore_by_items(self):
        # Cover: explore_by_items view
        # Test without item parameter
        response = self.client.get(reverse('explore_by_items'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/explore_by_items.html')
        self.assertEqual(response.context.get('item', ''), '')
        if response.context is not None:
            district = response.context.get('district', [])
            upazilla = response.context.get('Upazilla', [])
            area = response.context.get('Area', [])
            self.assertTrue(any(d['name'] == 'Test District' for d in district))
            self.assertTrue(any('Test Upazilla' in u['upazilla_names'] for u in upazilla))
            self.assertTrue(any('Test Area' in a['area_names'] for a in area))

        # Test with item parameter
        response = self.client.get(reverse('explore_by_items'), {'item': 'Test Item'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/explore_by_items.html')
        self.assertEqual(response.context.get('item', ''), 'Test Item')
        if response.context is not None:
            district = response.context.get('district', [])
            upazilla = response.context.get('Upazilla', [])
            area = response.context.get('Area', [])
            self.assertTrue(any(d['name'] == 'Test District' for d in district))
            self.assertTrue(any('Test Upazilla' in u['upazilla_names'] for u in upazilla))
            self.assertTrue(any('Test Area' in a['area_names'] for a in area))