from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from my_app.models import Division, District, Upazilla, Area, Service, Item
from shop_profile.models import MyUser, ShopProfile, ShopWorker, ShopService, ShopSchedule
from user_profile.models import UserProfile
from unittest.mock import patch
import json
from datetime import time
from io import BytesIO
from PIL import Image
import uuid

UserModel = get_user_model()

class RegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        # Create dependencies
        self.division = Division.objects.create(name='Dhaka Division')
        self.district = District.objects.create(name='Dhaka', division=self.division)
        self.upazilla = Upazilla.objects.create(name='Mirpur', district=self.district)
        self.area = Area.objects.create(name='Mirpur-10', upazilla=self.upazilla)
        self.service = Service.objects.create(name='Haircare')
        self.item = Item.objects.create(
            name='Haircut',
            item_description='Standard haircut',
            service=self.service,
            gender='Both'
        )

        # Define user data for session simulation
        self.user_data = {
            'first-name': 'John',
            'last-name': 'Doe',
            'email': f'john_{uuid.uuid4()}@example.com',
            'password': make_password('testpass123'),
            'mobile-number': '1234567890',
            'gender': 'Male',
            'business_name': 'Test Business',
            'business_title': 'Test Title',
            'website': 'http://test.com',
            'business_info': 'Test Info',
            'district': 'Dhaka',
            'upazilla': 'Mirpur',
            'area': 'Mirpur-10',
            'landmark1': 'Landmark 1',
            'landmark2': '',
            'landmark3': '',
            'landmark4': '',
            'landmark5': '',
            'latitude': '23.8103',
            'longitude': '90.4125',
            'services': [str(self.service.id)],
            'items': {
                f'items[{self.service.id}][name][]': ['Haircut'],
                f'items[{self.service.id}][price][]': ['50.00']
            },
            'member': 1,
            'members': {
                'member[0][name][]': ['Worker One'],
                'member[0][email][]': ['worker1@example.com'],
                'member[0][contact][]': ['1234567890'],
                'member[0][experience][]': ['5'],
                'member[0][expertise][]': ['Haircut']
            },
            'worker_image': [['temp/worker1.jpg']]
        }

    # View Tests
    def test_select_user_type(self):
        """Test GET request to select_user_type."""
        response = self.client.get(reverse('select_user_type'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/sign-up.html')

    def test_customer_register_step1_get(self):
        """Test GET request to customer_register_step1."""
        response = self.client.get(reverse('customer_register_step1'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/customer/step1.html')
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], '')

    @patch('registration.views.Upazilla.objects.values')
    def test_customer_register_step2_get(self, mock_upazilla_values):
        """Test GET request to customer_register_step2."""
        mock_upazilla_values.return_value.annotate.return_value = [
            {'district__name': 'Dhaka', 'upazilla_names': ['Mirpur', 'Dhanmondi']}
        ]
        response = self.client.get(reverse('step2'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/customer/step2.html')
        self.assertIn('district', response.context)
        self.assertIn('Upazilla', response.context)

    @patch('registration.views.Upazilla.objects.values')
    def test_customer_register_step2_post_valid(self, mock_upazilla_values):
        """Test POST to customer_register_step2 with valid data."""
        mock_upazilla_values.return_value.annotate.return_value = [
            {'district__name': 'Dhaka', 'upazilla_names': ['Mirpur', 'Dhanmondi']}
        ]
        data = {
            'first-name': 'John',
            'last-name': 'Doe',
            'email': f'john_{uuid.uuid4()}@example.com',
            'password': 'testpass123',
            'mobile-number': '1234567890',
            'gender': 'Male'
        }
        response = self.client.post(reverse('step2'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/customer/step2.html')
        session_user = self.client.session.get('user', {})
        self.assertEqual(session_user.get('first-name'), 'John')
        self.assertEqual(session_user.get('email'), data['email'])

    def test_customer_register_step2_post_existing_email(self):
        """Test POST to customer_register_step2 with existing email."""
        UserModel.objects.create_user(
            email='existing@example.com',
            password='testpass123',
            user_type='user'
        )
        data = {
            'first-name': 'Jane',
            'last-name': 'Doe',
            'email': 'existing@example.com',
            'password': 'testpass123',
            'mobile-number': '1234567890',
            'gender': 'Female'
        }
        response = self.client.post(reverse('step2'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step1.html')
        self.assertEqual(response.context.get('message', ''), 'The email exist.')

    def test_customer_submit_post_invalid_session(self):
        response = self.client.post(reverse('customer_submit'), {
            'district': 'Dhaka',
            'upazilla': 'Mirpur',
            'area': 'Mirpur-10'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Failed')

    def test_business_register_step1_get(self):
        """Test GET request to business_register_step1."""
        response = self.client.get(reverse('business_register_step1'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step1.html')
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], '')

    def test_business_register_step2_post_valid(self):
        """Test POST to business_register_step2 with valid data."""
        data = {
            'first-name': 'Jane',
            'last-name': 'Smith',
            'email': f'jane_{uuid.uuid4()}@example.com',
            'password': 'testpass123',
            'mobile-number': '9876543210'
        }
        response = self.client.post(reverse('business_register_step2'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step2.html')
        session_user = self.client.session.get('user', {})
        self.assertEqual(session_user.get('first-name'), 'Jane')
        self.assertEqual(session_user.get('email'), data['email'])

    def test_business_register_step2_post_existing_email(self):
        UserModel.objects.create_user(
            email='existing@example.com',
            password='testpass123',
            user_type='shop'
        )
        data = {
            'first-name': 'Jane',
            'last-name': 'Smith',
            'email': 'existing@example.com',
            'password': 'testpass123',
            'mobile-number': '9876543210'
        }
        response = self.client.post(reverse('business_register_step2'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step1.html')
        self.assertEqual(response.context.get('message', ''), 'The email exist.')

    @patch('django.contrib.postgres.aggregates.ArrayAgg', lambda x: x)
    def test_business_register_step3_get(self):
        response = self.client.get(reverse('business_register_step3'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step3.html')
        self.assertIn('district', response.context)
        self.assertIn('Upazilla', response.context)

    def test_business_register_step4_get(self):
        response = self.client.get(reverse('business_register_step4'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step4.html')
        self.assertIn('services', response.context)

    @patch('registration.views.Item.objects.values')
    def test_business_register_step5_post(self, mock_item_values):
        """Test POST to business_register_step5."""
        email = f'jane_{uuid.uuid4()}@example.com'
        self.client.session['user'] = {'email': email}
        self.client.session.modified = True
        mock_item_values.return_value.annotate.return_value = [
            {'service__id': self.service.id, 'service__name': 'Haircare', 'service_names': ['Haircut']}
        ]
        data = {'services[]': [str(self.service.id)]}
        response = self.client.post(reverse('business_register_step5'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step5.html')
        session_user = self.client.session.get('user', {})
        self.assertEqual(session_user.get('services', []), [str(self.service.id)])

    def test_business_submit_post_invalid_session(self):
        response = self.client.post(reverse('business_submit'), {
            'schedule[Monday][start]': '09:00',
            'schedule[Monday][end]': '17:00'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), 'Invalid session data')
