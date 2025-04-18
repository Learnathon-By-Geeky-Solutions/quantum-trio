from django.http import JsonResponse
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
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

    def test_explore_by_items_view(self):
        response = self.client.get(reverse('explore_by_items'), {'item': 'Test Item'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/explore_by_items.html')
        self.assertEqual(response.context['item'], 'Test Item')

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
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
 
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
    