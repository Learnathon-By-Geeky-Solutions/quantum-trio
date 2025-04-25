from datetime import date, time
from decimal import Decimal
import decimal
from unittest.mock import patch
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import get_messages
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

    # def test_submit_shop_review_general_exception(self):
    #     self.client.login(email='testuser@example.com', password='testpass123')
    #     BookingSlot.objects.create(
    #         user=self.user_profile,
    #         shop=self.shop_profile,
    #         status='completed',
    #         date=date(2025, 4, 24),
    #         time=time(12, 0),
    #         payment_status='unpaid',
    #         item=self.item,
    #         worker=self.shop_worker
    #     )
    #     with patch('shop_profile.models.ShopReview.objects.create', side_effect=Exception('Database error')):
    #         response = self.client.post(reverse('submit_shop_review'), {
    #             'rating': '4',
    #             'review': 'Great shop!',
    #             'shop_id': self.shop_profile.id,
    #             'user_id': self.user_profile.id
    #         })
    #     self.assertEqual(response.status_code, 404)

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

    def test_book_now_non_get(self):
        # Cover: else branch in book_now
        response = self.client.post(reverse('booknow'))
        self.assertEqual(response.status_code, 405)
        self.assertIsInstance(response, HttpResponseNotAllowed)


class UniqueCoverageMyAppTests1(TestCase):
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

    def test_fetch_shop_filters(self):
        # Cover: upazilla and area filters in fetch_shop
        # Test with upazila filter
        response = self.client.get(reverse('fetch_shop'), {
            'upazila': 'Test Upazilla',
            'limit': 5,
            'offset': 0
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['shop_name'], 'Test Shop')
        self.assertEqual(data[0]['shop_city'], 'Test Upazilla')

        # Test with area filter
        response = self.client.get(reverse('fetch_shop'), {
            'area': 'Test Area',
            'limit': 5,
            'offset': 0
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['shop_name'], 'Test Shop')
        self.assertEqual(data[1]['shop_name'], 'Test Shop 2')

# my_app/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, time, datetime
from my_app.models import Division, District, Upazilla, Area, Service, Item, ReviewCarehub
from shop_profile.models import ShopProfile, ShopWorker, ShopService
from user_profile.models import UserProfile
from booking.models import BookingSlot
from django.contrib.contenttypes.models import ContentType
from unittest.mock import patch
from django.http import HttpResponseNotAllowed
import django.urls.exceptions

UserModel = get_user_model()

class MyAppUncoveredTests(TestCase):
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

        # Create admin user
        self.admin_user = UserModel.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            user_type='admin'
        )

        # Create location hierarchy
        self.division = Division.objects.create(name='Test Division')
        self.district = District.objects.create(name='Test District', division=self.division)
        self.upazilla = Upazilla.objects.create(name='Test Upazilla', district=self.district)
        self.area = Area.objects.create(name='Test Area', upazilla=self.upazilla)

        # Create service and items
        self.service = Service.objects.create(name='Test Service')
        self.male_item = Item.objects.create(
            name='Male Item',
            item_description='Male Description',
            service=self.service,
            gender='Male'
        )
        self.female_item = Item.objects.create(
            name='Female Item',
            item_description='Female Description',
            service=self.service,
            gender='Female'
        )
        self.both_item = Item.objects.create(
            name='Both Item',
            item_description='Both Description',
            service=self.service,
            gender='Both'
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
            item=self.both_item,
            status='pending',
            date=date(2024, 5, 5),
            time=time(10, 0),
            payment_status='unpaid',
            user_end=True,
            shop_end=False,
            notes='',
            rated=False
        )

        # Create review
        try:
            self.review = ReviewCarehub.objects.create(
                reviewer_type=ContentType.objects.get_for_model(UserProfile),
                reviewer_id=self.user_profile.id,
                comment='Great service!',
                rating=5.0,
                created_at=timezone.now()
            )
        except Exception as e:
            print(f"Error creating ReviewCarehub: {str(e)}")  # Debug
            raise

    def test_home_non_get_method(self):
        # Cover: non-GET request returning HttpResponseNotAllowed
        response = self.client.post(reverse('home'))
        self.assertEqual(response.status_code, 405)
        self.assertIsInstance(response, HttpResponseNotAllowed)

    def test_home_unauthenticated(self):
        # Cover: GET request for unauthenticated user
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/home.html')
        self.assertEqual(response.context['reviewer_name'], "You are not allowed to give review.")
        self.assertEqual(len(response.context['shops']), 1)
        self.assertEqual(response.context['shops'][0].id, self.shop_profile.id)
        self.assertEqual(len(response.context['male']), 2)  # Male + Both
        self.assertEqual(len(response.context['female']), 2)  # Female + Both
        self.assertEqual(len(response.context['reviews']), 1)
        self.assertEqual(response.context['reviews'][0].id, self.review.id)
        stats = response.context['statistics']
        self.assertEqual(stats['booked_appointment'], 1)
        self.assertEqual(stats['registered_shop'], 1)
        self.assertEqual(stats['available_upazilla'], 1)
        self.assertEqual(stats['available_barber'], 1)

    def test_home_authenticated_shop(self):
        # Cover: GET request for authenticated shop user
        self.client.force_login(self.shop_user)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/home.html')
        self.assertEqual(response.context['reviewer_name'], self.shop_profile.shop_name)
        self.assertEqual(len(response.context['shops']), 1)
        self.assertEqual(len(response.context['male']), 2)
        self.assertEqual(len(response.context['female']), 2)
        self.assertEqual(len(response.context['reviews']), 1)
        stats = response.context['statistics']
        self.assertEqual(stats['booked_appointment'], 1)
        self.assertEqual(stats['registered_shop'], 1)
        self.assertEqual(stats['available_upazilla'], 1)
        self.assertEqual(stats['available_barber'], 1)

    def test_home_authenticated_user(self):
        # Cover: GET request for authenticated regular user
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/home.html')
        self.assertEqual(response.context['reviewer_name'], f"{self.user_profile.first_name} {self.user_profile.last_name}")
        self.assertEqual(len(response.context['shops']), 1)
        self.assertEqual(len(response.context['male']), 2)
        self.assertEqual(len(response.context['female']), 2)
        self.assertEqual(len(response.context['reviews']), 1)
        stats = response.context['statistics']
        self.assertEqual(stats['booked_appointment'], 1)
        self.assertEqual(stats['registered_shop'], 1)
        self.assertEqual(stats['available_upazilla'], 1)
        self.assertEqual(stats['available_barber'], 1)

    # def test_success_reset_password(self):
    #     # Cover: success_reset_password returning HttpResponse
    #     try:
    #         response = self.client.get(reverse('success_reset_password'))  # Adjust if name differs, e.g., 'reset_password_success'
    #         self.assertEqual(response.status_code, 200)
    #         self.assertEqual(response.content.decode(), "Password reset successful. This is a test response.")
    #     except django.urls.exceptions.NoReverseMatch as e:
    #         print(f"URL resolution error: {str(e)}")  # Debug
    #         self.fail(f"Failed to resolve 'success_reset_password' URL: {str(e)}. Check my_app/urls.py for correct URL name.")

    def test_explore_by_items(self):
        # Cover: GET request to explore_by_items
        with patch('my_app.views.area_database', return_value=([{'id': self.district.id, 'name': self.district.name}], [{'district__name': self.district.name, 'upazilla_names': [self.upazilla.name]}], [{'upazilla__name': self.upazilla.name, 'area_names': [self.area.name]}])):
            response = self.client.get(reverse('explore_by_items'), {'item': 'Test Item'})
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'app/explore_by_items.html')
            self.assertEqual(response.context['item'], 'Test Item')
            self.assertEqual(len(response.context['district']), 1)
            self.assertEqual(response.context['district'][0]['id'], self.district.id)
            self.assertEqual(len(response.context['Upazilla']), 1)
            self.assertEqual(response.context['Upazilla'][0]['upazilla_names'][0], self.upazilla.name)
            self.assertEqual(len(response.context['Area']), 1)
            self.assertEqual(response.context['Area'][0]['area_names'][0], self.area.name)

# my_app/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, time, datetime
from my_app.models import Division, District, Upazilla, Area, Service, Item
from shop_profile.models import ShopProfile, ShopWorker, ShopService, ShopReview
from user_profile.models import UserProfile
from booking.models import BookingSlot
from unittest.mock import patch
from django.http import HttpResponseNotAllowed
import django.urls.exceptions

UserModel = get_user_model()

class MyAppAdditionalUncoveredTests(TestCase):
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

        # Create admin user
        self.admin_user = UserModel.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            user_type='admin'
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

        # Create completed booking slot for review eligibility
        self.booking = BookingSlot.objects.create(
            user=self.user_profile,
            shop=self.shop_profile,
            worker=self.shop_worker,
            item=self.item,
            status='completed',
            date=date(2024, 5, 5),
            time=time(10, 0),
            payment_status='paid',
            user_end=True,
            shop_end=True,
            notes='',
            rated=False
        )

    def test_login_shop_user(self):
        # Cover: Successful login with shop user
        response = self.client.post(reverse('login'), {
            'email': 'shopuser@example.com',
            'password': 'shoppass123',
            'profile-type': 'shop'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(self.client.session.get('_auth_user_id'))  # User is logged in

    def test_login_regular_user(self):
        # Cover: Successful login with regular user
        response = self.client.post(reverse('login'), {
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'profile-type': 'user'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(self.client.session.get('_auth_user_id'))  # User is logged in

    def test_login_admin_user(self):
        # Cover: Successful login with admin user
        response = self.client.post(reverse('login'), {
            'email': 'admin@example.com',
            'password': 'adminpass123',
            'profile-type': 'admin'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(self.client.session.get('_auth_user_id'))  # User is logged in

    # def test_submit_shop_review_generic_exception(self):
    #     # Cover: Generic exception in submit_shop_review
    #     self.client.force_login(self.user)
    #     with patch('shop_profile.models.ShopReview.objects.create', side_effect=Exception('Database error')):
    #         response = self.client.post(reverse('submit_shop_review'), {
    #             'rating': '5',
    #             'review': 'Great service!',
    #             'shop_id': self.shop_profile.id
    #         })
    #     self.assertEqual(response.status_code, 500)
    #     self.assertJSONEqual(response.content, {'success': False, 'error': 'Database error'})

    def test_book_now_with_district(self):
        # Cover: GET request with district parameter
        with patch('my_app.views.area_database', return_value=([{'id': self.district.id, 'name': self.district.name}], [{'district__name': self.district.name, 'upazilla_names': [self.upazilla.name]}], [{'upazilla__name': self.upazilla.name, 'area_names': [self.area.name]}])):
            response = self.client.get(reverse('booknow'), {'district': 'Test District'})
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'app/book_now.html')
            self.assertEqual(response.context['dist'], 'Test District')
            self.assertEqual(len(response.context['district']), 1)
            self.assertEqual(response.context['district'][0]['id'], self.district.id)

    def test_book_now_with_upazilla(self):
        # Cover: GET request with upazilla parameter
        with patch('my_app.views.area_database', return_value=([{'id': self.district.id, 'name': self.district.name}], [{'district__name': self.district.name, 'upazilla_names': [self.upazilla.name]}], [{'upazilla__name': self.upazilla.name, 'area_names': [self.area.name]}])):
            response = self.client.get(reverse('booknow'), {'upazilla': 'Test Upazilla'})
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'app/book_now.html')
            self.assertEqual(response.context['dist'], 'Test Upazilla')
            self.assertEqual(len(response.context['Upazilla']), 1)
            self.assertEqual(response.context['Upazilla'][0]['upazilla_names'][0], self.upazilla.name)

    def test_book_now_non_get_method(self):
        # Cover: Non-GET request returning HttpResponseNotAllowed
        response = self.client.post(reverse('booknow'))
        self.assertEqual(response.status_code, 405)
        self.assertIsInstance(response, HttpResponseNotAllowed)