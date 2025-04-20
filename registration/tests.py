# from django.test import TestCase, Client, RequestFactory
# from django.urls import reverse
# from django.core.files.uploadedfile import SimpleUploadedFile
# from django.contrib.auth import get_user_model
# from django.contrib.auth.hashers import make_password
# from django.utils import timezone
# from my_app.models import Division, District, Upazilla, Area, Service, Item
# from shop_profile.models import MyUser, ShopProfile, ShopWorker, ShopService, ShopSchedule
# from user_profile.models import UserProfile
# from unittest.mock import patch
# import json
# from datetime import time
# from io import BytesIO
# from PIL import Image
# import uuid

# UserModel = get_user_model()

# class RegistrationTests(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.factory = RequestFactory()

#         # Create dependencies
#         self.division = Division.objects.create(name='Dhaka Division')
#         self.district = District.objects.create(name='Dhaka', division=self.division)
#         self.upazilla = Upazilla.objects.create(name='Mirpur', district=self.district)
#         self.area = Area.objects.create(name='Mirpur-10', upazilla=self.upazilla)
#         self.service = Service.objects.create(name='Haircare')
#         self.item = Item.objects.create(
#             name='Haircut',
#             item_description='Standard haircut',
#             service=self.service,
#             gender='Both'
#         )

#         # Define user data for session simulation
#         self.user_data = {
#             'first-name': 'John',
#             'last-name': 'Doe',
#             'email': f'john_{uuid.uuid4()}@example.com',
#             'password': make_password('testpass123'),
#             'mobile-number': '1234567890',
#             'gender': 'Male',
#             'business_name': 'Test Business',
#             'business_title': 'Test Title',
#             'website': 'http://test.com',
#             'business_info': 'Test Info',
#             'district': 'Dhaka',
#             'upazilla': 'Mirpur',
#             'area': 'Mirpur-10',
#             'landmark1': 'Landmark 1',
#             'landmark2': '',
#             'landmark3': '',
#             'landmark4': '',
#             'landmark5': '',
#             'latitude': '23.8103',
#             'longitude': '90.4125',
#             'services': [str(self.service.id)],
#             'items': {
#                 f'items[{self.service.id}][name][]': ['Haircut'],
#                 f'items[{self.service.id}][price][]': ['50.00']
#             },
#             'member': 1,
#             'members': {
#                 'member[0][name][]': ['Worker One'],
#                 'member[0][email][]': ['worker1@example.com'],
#                 'member[0][contact][]': ['1234567890'],
#                 'member[0][experience][]': ['5'],
#                 'member[0][expertise][]': ['Haircut']
#             },
#             'worker_image': [['temp/worker1.jpg']]
#         }

#     # View Tests
#     def test_select_user_type(self):
#         """Test GET request to select_user_type."""
#         response = self.client.get(reverse('select_user_type'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/sign-up.html')

#     def test_customer_register_step1_get(self):
#         """Test GET request to customer_register_step1."""
#         response = self.client.get(reverse('customer_register_step1'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/customer/step1.html')
#         self.assertIn('message', response.context)
#         self.assertEqual(response.context['message'], '')

#     @patch('registration.views.Upazilla.objects.values')
#     def test_customer_register_step2_get(self, mock_upazilla_values):
#         """Test GET request to customer_register_step2."""
#         mock_upazilla_values.return_value.annotate.return_value = [
#             {'district__name': 'Dhaka', 'upazilla_names': ['Mirpur', 'Dhanmondi']}
#         ]
#         response = self.client.get(reverse('step2'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/customer/step2.html')
#         self.assertIn('district', response.context)
#         self.assertIn('Upazilla', response.context)

#     @patch('registration.views.Upazilla.objects.values')
#     def test_customer_register_step2_post_valid(self, mock_upazilla_values):
#         """Test POST to customer_register_step2 with valid data."""
#         mock_upazilla_values.return_value.annotate.return_value = [
#             {'district__name': 'Dhaka', 'upazilla_names': ['Mirpur', 'Dhanmondi']}
#         ]
#         data = {
#             'first-name': 'John',
#             'last-name': 'Doe',
#             'email': f'john_{uuid.uuid4()}@example.com',
#             'password': 'testpass123',
#             'mobile-number': '1234567890',
#             'gender': 'Male'
#         }
#         response = self.client.post(reverse('step2'), data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/customer/step2.html')
#         session_user = self.client.session.get('user', {})
#         self.assertEqual(session_user.get('first-name'), 'John')
#         self.assertEqual(session_user.get('email'), data['email'])

#     def test_customer_register_step2_post_existing_email(self):
#         """Test POST to customer_register_step2 with existing email."""
#         UserModel.objects.create_user(
#             email='existing@example.com',
#             password='testpass123',
#             user_type='user'
#         )
#         data = {
#             'first-name': 'Jane',
#             'last-name': 'Doe',
#             'email': 'existing@example.com',
#             'password': 'testpass123',
#             'mobile-number': '1234567890',
#             'gender': 'Female'
#         }
#         response = self.client.post(reverse('step2'), data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/business/step1.html')
#         self.assertEqual(response.context.get('message', ''), 'The email exist.')

#     def test_customer_submit_post_invalid_session(self):
#         response = self.client.post(reverse('customer_submit'), {
#             'district': 'Dhaka',
#             'upazilla': 'Mirpur',
#             'area': 'Mirpur-10'
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.content.decode(), 'Failed')

#     def test_business_register_step1_get(self):
#         """Test GET request to business_register_step1."""
#         response = self.client.get(reverse('business_register_step1'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/business/step1.html')
#         self.assertIn('message', response.context)
#         self.assertEqual(response.context['message'], '')

#     def test_business_register_step2_post_valid(self):
#         """Test POST to business_register_step2 with valid data."""
#         data = {
#             'first-name': 'Jane',
#             'last-name': 'Smith',
#             'email': f'jane_{uuid.uuid4()}@example.com',
#             'password': 'testpass123',
#             'mobile-number': '9876543210'
#         }
#         response = self.client.post(reverse('business_register_step2'), data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/business/step2.html')
#         session_user = self.client.session.get('user', {})
#         self.assertEqual(session_user.get('first-name'), 'Jane')
#         self.assertEqual(session_user.get('email'), data['email'])

#     def test_business_register_step2_post_existing_email(self):
#         UserModel.objects.create_user(
#             email='existing@example.com',
#             password='testpass123',
#             user_type='shop'
#         )
#         data = {
#             'first-name': 'Jane',
#             'last-name': 'Smith',
#             'email': 'existing@example.com',
#             'password': 'testpass123',
#             'mobile-number': '9876543210'
#         }
#         response = self.client.post(reverse('business_register_step2'), data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/business/step1.html')
#         self.assertEqual(response.context.get('message', ''), 'The email exist.')

#     def test_business_register_step4_get(self):
#         response = self.client.get(reverse('business_register_step4'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/business/step4.html')
#         self.assertIn('services', response.context)

#     @patch('registration.views.Item.objects.values')
#     def test_business_register_step5_post(self, mock_item_values):
#         """Test POST to business_register_step5."""
#         email = f'jane_{uuid.uuid4()}@example.com'
#         self.client.session['user'] = {'email': email}
#         self.client.session.modified = True
#         mock_item_values.return_value.annotate.return_value = [
#             {'service__id': self.service.id, 'service__name': 'Haircare', 'service_names': ['Haircut']}
#         ]
#         data = {'services[]': [str(self.service.id)]}
#         response = self.client.post(reverse('business_register_step5'), data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/business/step5.html')
#         session_user = self.client.session.get('user', {})
#         self.assertEqual(session_user.get('services', []), [str(self.service.id)])

#     def test_business_submit_post_invalid_session(self):
#         response = self.client.post(reverse('business_submit'), {
#             'schedule[Monday][start]': '09:00',
#             'schedule[Monday][end]': '17:00'
#         })
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.content.decode(), 'Invalid session data')
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from carehub import settings
from my_app.models import Division, District, Upazilla, Area, Service, Item
from shop_profile.models import MyUser, ShopProfile, ShopWorker, ShopService, ShopSchedule
from user_profile.models import UserProfile
from unittest.mock import patch
import json
from datetime import time
from io import BytesIO
from PIL import Image
import uuid
import os

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
            'password': 'testpass123',
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

    @patch('django.contrib.postgres.aggregates.ArrayAgg')
    def test_customer_register_step2_get(self, mock_array_agg):
        """Test GET request to customer_register_step2."""
        mock_array_agg.return_value = ['Mirpur', 'Dhanmondi']
        response = self.client.get(reverse('step2'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/customer/step2.html')
        self.assertIn('district', response.context)
        self.assertIn('Upazilla', response.context)
        self.assertEqual(response.context['district'][0]['name'], 'Dhaka')
        self.assertEqual(response.context['Upazilla'][0]['upazilla_names'], ['Mirpur', 'Dhanmondi'])

    @patch('django.contrib.postgres.aggregates.ArrayAgg')
    def test_customer_register_step2_post_valid(self, mock_array_agg):
        """Test POST to customer_register_step2 with valid data."""
        mock_array_agg.return_value = ['Mirpur', 'Dhanmondi']
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

    def test_customer_submit_post_valid(self):
        """Test POST to customer_submit with valid session data."""
        self.client.session['user'] = {
            'first-name': 'John',
            'last-name': 'Doe',
            'email': f'john_{uuid.uuid4()}@example.com',
            'password': make_password('testpass123'),
            'mobile-number': '1234567890',
            'gender': 'Male'
        }
        self.client.session.modified = True
        data = {
            'district': 'Dhaka',
            'upazilla': 'Mirpur',
            'area': 'Mirpur-10',
            'latitude': '23.8103',
            'longitude': '90.4125'
        }
        response = self.client.post(reverse('customer_submit'), data)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(UserModel.objects.filter(email=self.client.session['user']['email']).exists())
        self.assertTrue(UserProfile.objects.filter(user__email=self.client.session['user']['email']).exists())

    def test_customer_submit_post_invalid_session(self):
        """Test POST to customer_submit with invalid session."""
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

    def test_business_register_step2_get(self):
        """Test GET request to business_register_step2."""
        response = self.client.get(reverse('business_register_step2'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step2.html')

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
        """Test POST to business_register_step2 with existing email."""
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

    @patch('django.contrib.postgres.aggregates.ArrayAgg')
    def test_business_register_step3_get(self, mock_array_agg):
        """Test GET request to business_register_step3."""
        mock_array_agg.return_value = ['Mirpur', 'Dhanmondi']
        response = self.client.get(reverse('business_register_step3'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step3.html')
        self.assertIn('district', response.context)
        self.assertIn('Upazilla', list(response.context))
        self.assertEqual(response.context['district'][0]['name'], 'Dhaka')
        self.assertEqual(response.context['Upazilla'][0]['upazilla_names'], ['Mirpur', 'Dhanmondi'])

    @patch('django.contrib.postgres.aggregates.ArrayAgg')
    def test_business_register_step3_post_valid(self, mock_array_agg):
        """Test POST to business_register_step3 with valid data."""
        mock_array_agg.return_value = ['Mirpur', 'Dhanmondi']
        self.client.session['user'] = {
            'first-name': 'Jane',
            'last-name': 'Smith',
            'email': f'jane_{uuid.uuid4()}@example.com',
            'password': make_password('testpass123'),
            'mobile-number': '9876543210'
        }
        self.client.session.modified = True
        data = {
            'business_name': 'Test Business',
            'business_title': 'Test Title',
            'website': 'http://test.com',
            'business_info': 'Test Info',
            'gender': 'Male'
        }
        response = self.client.post(reverse('business_register_step3'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step3.html')
        session_user = self.client.session.get('user', {})
        self.assertEqual(session_user.get('business_name'), 'Test Business')
        self.assertEqual(session_user.get('gender'), 'Male')

    def test_business_register_step4_get(self):
        """Test GET request to business_register_step4."""
        response = self.client.get(reverse('business_register_step4'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step4.html')
        self.assertIn('services', response.context)
        self.assertEqual(response.context['services'][0]['name'], 'Haircare')

    def test_business_register_step4_post_valid(self):
        """Test POST to business_register_step4 with valid data."""
        self.client.session['user'] = {
            'first-name': 'Jane',
            'last-name': 'Smith',
            'email': f'jane_{uuid.uuid4()}@example.com',
            'password': make_password('testpass123'),
            'mobile-number': '9876543210',
            'business_name': 'Test Business'
        }
        self.client.session.modified = True
        data = {
            'district': 'Dhaka',
            'upazilla': 'Mirpur',
            'area': 'Mirpur-10',
            'landmarks[]': ['Landmark 1', '', '', '', ''],
            'latitude': '23.8103',
            'longitude': '90.4125'
        }
        response = self.client.post(reverse('business_register_step4'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step4.html')
        session_user = self.client.session.get('user', {})
        self.assertEqual(session_user.get('district'), 'Dhaka')
        self.assertEqual(session_user.get('landmark1'), 'Landmark 1')

    @patch('django.contrib.postgres.aggregates.ArrayAgg')
    def test_business_register_step5_get(self, mock_array_agg):
        """Test GET request to business_register_step5."""
        mock_array_agg.return_value = ['Haircut']
        self.client.session['user'] = {
            'email': f'jane_{uuid.uuid4()}@example.com',
            'services': [str(self.service.id)]
        }
        self.client.session.modified = True
        response = self.client.get(reverse('business_register_step5'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step5.html')
        self.assertIn('services', response.context)
        self.assertEqual(response.context['services'][0]['service__name'], 'Haircare')

    @patch('django.contrib.postgres.aggregates.ArrayAgg')
    def test_business_register_step5_post(self, mock_array_agg):
        """Test POST to business_register_step5."""
        mock_array_agg.return_value = ['Haircut']
        email = f'jane_{uuid.uuid4()}@example.com'
        self.client.session['user'] = {'email': email}
        self.client.session.modified = True
        data = {'services[]': [str(self.service.id)]}
        response = self.client.post(reverse('business_register_step5'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step5.html')
        session_user = self.client.session.get('user', {})
        self.assertEqual(session_user.get('services', []), [str(self.service.id)])

    def test_business_register_step6_post(self):
        """Test POST to business_register_step6."""
        self.client.session['user'] = {
            'email': f'jane_{uuid.uuid4()}@example.com',
            'services': [str(self.service.id)]
        }
        self.client.session.modified = True
        data = {
            f'items[{self.service.id}][name][]': ['Haircut'],
            f'items[{self.service.id}][price][]': ['50.00']
        }
        response = self.client.post(reverse('business_register_step6'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step6.html')
        session_user = self.client.session.get('user', {})
        self.assertIn(f'items[{self.service.id}][name][]', session_user['items'])
        self.assertEqual(session_user['items'][f'items[{self.service.id}][name][]'], ['Haircut'])

    def test_business_register_step7_post(self):
        """Test POST to business_register_step7."""
        self.client.session['user'] = {
            'email': f'jane_{uuid.uuid4()}@example.com',
            'items': {
                f'items[{self.service.id}][name][]': ['Haircut'],
                f'items[{self.service.id}][price][]': ['50.00']
            }
        }
        self.client.session.modified = True
        data = {'members': '2'}
        response = self.client.post(reverse('business_register_step7'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step7.html')
        session_user = self.client.session.get('user', {})
        self.assertEqual(session_user.get('member'), 2)
        self.assertEqual(response.context['items'], ['Haircut'])

    def test_business_register_step7_post_invalid_members(self):
        """Test POST to business_register_step7 with invalid members input."""
        self.client.session['user'] = {
            'email': f'jane_{uuid.uuid4()}@example.com',
            'items': {
                f'items[{self.service.id}][name][]': ['Haircut'],
                f'items[{self.service.id}][price][]': ['50.00']
            }
        }
        self.client.session.modified = True
        data = {'members': 'invalid'}
        response = self.client.post(reverse('business_register_step7'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step7.html')
        session_user = self.client.session.get('user', {})
        self.assertEqual(session_user.get('member'), 1)  # Fallback to 1

    def test_business_register_step8_post(self):
        """Test POST to business_register_step8 with valid data."""
        self.client.session['user'] = {
            'email': f'jane_{uuid.uuid4()}@example.com',
            'member': 1
        }
        self.client.session.modified = True
        # Create a temporary image file
        img = Image.new('RGB', (100, 100), color='red')
        img_io = BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        data = {
            'member[0][name][]': ['Worker One'],
            'member[0][email][]': ['worker1@example.com'],
            'member[0][contact][]': ['1234567890'],
            'member[0][experience][]': ['5'],
            'member[0][expertise][]': ['Haircut']
        }
        files = {
            'member[0][image][]': SimpleUploadedFile('worker1.jpg', img_io.read(), content_type='image/jpeg')
        }
        response = self.client.post(reverse('business_register_step8'), data=data, files=files)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step8.html')
        session_user = self.client.session.get('user', {})
        self.assertIn('members', session_user)
        self.assertIn('worker_image', session_user)
        self.assertEqual(session_user['members']['member[0][name][]'], ['Worker One'])
        self.assertTrue(session_user['worker_image'][0][0].startswith('temp/worker1'))

    def test_business_submit_post_valid(self):
        """Test POST to business_submit with valid session data."""
        self.client.session['user'] = self.user_data
        self.client.session.modified = True
        # Create a temporary image file for worker
        img = Image.new('RGB', (100, 100), color='red')
        img_io = BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        with open(os.path.join(settings.MEDIA_ROOT, 'temp/worker1.jpg'), 'wb') as f:
            f.write(img_io.read())
        data = {
            'schedule[Monday][start]': '09:00',
            'schedule[Monday][end]': '17:00',
            'schedule[Tuesday][start]': '',
            'schedule[Tuesday][end]': ''
        }
        response = self.client.post(reverse('business_submit'), data)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(UserModel.objects.filter(email=self.user_data['email']).exists())
        self.assertTrue(ShopProfile.objects.filter(shop_name=self.user_data['business_name']).exists())
        self.assertTrue(ShopWorker.objects.filter(name='Worker One').exists())
        self.assertTrue(ShopService.objects.filter(price='50.00').exists())
        self.assertTrue(ShopSchedule.objects.filter(day_of_week='Monday', start='09:00').exists())

    def test_business_submit_post_invalid_session(self):
        """Test POST to business_submit with invalid session."""
        response = self.client.post(reverse('business_submit'), {
            'schedule[Monday][start]': '09:00',
            'schedule[Monday][end]': '17:00'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), 'Invalid session data')

    def test_business_submit_post_invalid_method(self):
        """Test non-POST request to business_submit."""
        response = self.client.get(reverse('business_submit'))
        self.assertEqual(response.status_code, 302)  # Redirect to login