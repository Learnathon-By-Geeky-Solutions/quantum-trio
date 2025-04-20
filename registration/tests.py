# from django.http import JsonResponse
# from django.test import TestCase, Client, RequestFactory
# from django.urls import reverse
# from django.core.files.uploadedfile import SimpleUploadedFile
# from django.contrib.auth import get_user_model
# from django.contrib.auth.hashers import make_password
# from django.utils import timezone
# from booking.models import BookingSlot
# from my_app.models import Division, District, Upazilla, Area, Service, Item
# from shop_profile.models import MyUser, ShopNotification, ShopProfile, ShopWorker, ShopService, ShopSchedule
# from user_profile.models import UserProfile
# from unittest.mock import patch
# import json
# from datetime import date, time, timedelta
# from io import BytesIO
# from PIL import Image
# import uuid
# import os

# UserModel = get_user_model()
# TEST_PASS = "testpass123"
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
#             'password': make_password(TEST_PASS),
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

#         def test_customer_register_step2_post_existing_email(self):
#             """Test POST to customer_register_step2 with existing email."""
#             UserModel.objects.create_user(
#                 email='existing@example.com',
#                 password='testpass123',
#                 user_type='user'
#             )
#             data = {
#                 'first-name': 'Jane',
#                 'last-name': 'Doe',
#                 'email': 'existing@example.com',
#                 'password': 'testpass123',
#                 'mobile-number': '1234567890',
#                 'gender': 'Female'
#             }
#             response = self.client.post(reverse('step2'), data)
#             self.assertEqual(response.status_code, 200)
#             self.assertTemplateUsed(response, 'app/login_signup/register/business/step1.html')
#             self.assertEqual(response.context.get('message', ''), 'The email exist.')

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
#         self.assertTemplateUsed(response, 'app/login_signup/register/customer/step1.html')
#         self.assertEqual(response.context.get('message', ''), 'The email exist.')

#     def test_customer_register_step2_post_missing_data(self):
#         """Test POST to customer_register_step2 with missing required fields."""
#         data = {
#             'first-name': 'John',
#             # Missing last-name, email, password, mobile-number
#             'gender': 'Male'
#         }
#         response = self.client.post(reverse('step2'), data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/customer/step2.html')
#         session_user = self.client.session.get('user', {})
#         self.assertEqual(session_user.get('first-name'), 'John')
#         self.assertEqual(session_user.get('email', ''), '')

#     # @patch('registration.views.UserProfile.objects.create')
#     # def test_customer_submit_post_valid(self, mock_user_profile_create):
#     #     """Test POST to customer_submit with valid session data."""
#     #     email = f'john_{uuid.uuid4()}@example.com'
#     #     self.client.session['user'] = {
#     #         'first-name': 'John',
#     #         'last-name': 'Doe',
#     #         'email': email,
#     #         'password': make_password('testpass123'),
#     #         'mobile-number': '1234567890',
#     #         'gender': 'Male'
#     #     }
#     #     self.client.session.modified = True
#     #     data = {
#     #         'district': 'Dhaka',
#     #         'upazilla': 'Mirpur',
#     #         'area': 'Mirpur-10',
#     #         'latitude': '23.8103',
#     #         'longitude': '90.4125'
#     #     }
#     #     response = self.client.post(reverse('customer_submit'), data)
#     #     self.assertEqual(response.status_code, 302)  # Redirect to login
#     #     self.assertTrue(UserModel.objects.filter(email=email).exists())
#     #     mock_user_profile_create.assert_called()

#     def test_customer_submit_post_invalid_session(self):
#         """Test POST to customer_submit with invalid session."""
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
#         """Test POST to business_register_step2 with existing email."""
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

#     @patch('registration.views.Upazilla.objects.values')
#     def test_business_register_step3_get(self, mock_upazilla_values):
#         """Test GET request to business_register_step3."""
#         mock_upazilla_values.return_value.annotate.return_value = [
#             {'district__name': 'Dhaka', 'upazilla_names': ['Mirpur', 'Dhanmondi']}
#         ]
#         response = self.client.get(reverse('business_register_step3'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/business/step3.html')
#         self.assertIn('district', response.context)
#         self.assertIn('Upazilla', response.context)

#     @patch('registration.views.Upazilla.objects.values')
#     def test_business_register_step3_post_valid(self, mock_upazilla_values):
#         """Test POST to business_register_step3 with valid data."""
#         mock_upazilla_values.return_value.annotate.return_value = [
#             {'district__name': 'Dhaka', 'upazilla_names': ['Mirpur', 'Dhanmondi']}
#         ]
#         # Simulate step2 to set session
#         email = f'jane_{uuid.uuid4()}@example.com'
#         self.client.post(reverse('business_register_step2'), {
#             'first-name': 'Jane',
#             'last-name': 'Smith',
#             'email': email,
#             'password': 'testpass123',
#             'mobile-number': '9876543210'
#         })
#         data = {
#             'business_name': 'Test Business',
#             'business_title': 'Test Title',
#             'website': 'http://test.com',
#             'business_info': 'Test Info',
#             'gender': 'Both'
#         }
#         response = self.client.post(reverse('business_register_step3'), data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/business/step3.html')
#         session_user = self.client.session.get('user', {})
#         self.assertEqual(session_user.get('business_name'), 'Test Business')
#         self.assertEqual(session_user.get('business_title'), 'Test Title')

#     def test_business_register_step4_get(self):
#         """Test GET request to business_register_step4."""
#         response = self.client.get(reverse('business_register_step4'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/business/step4.html')
#         self.assertIn('services', response.context)

#     def test_business_register_step4_post_valid(self):
#         """Test POST to business_register_step4 with valid data."""
#         email = f'jane_{uuid.uuid4()}@example.com'
#         # Simulate step2 and step3
#         self.client.post(reverse('business_register_step2'), {
#             'first-name': 'Jane',
#             'last-name': 'Smith',
#             'email': email,
#             'password': 'testpass123',
#             'mobile-number': '9876543210'
#         })
#         self.client.post(reverse('business_register_step3'), {
#             'business_name': 'Test Business',
#             'business_title': 'Test Title',
#             'website': 'http://test.com',
#             'business_info': 'Test Info',
#             'gender': 'Both'
#         })
#         data = {
#             'district': 'Dhaka',
#             'upazilla': 'Mirpur',
#             'area': 'Mirpur-10',
#             'landmarks[]': ['Landmark 1', '', '', '', ''],
#             'latitude': '23.8103',
#             'longitude': '90.4125'
#         }
#         response = self.client.post(reverse('business_register_step4'), data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/business/step4.html')
#         session_user = self.client.session.get('user', {})
#         self.assertEqual(session_user.get('district'), 'Dhaka')
#         self.assertEqual(session_user.get('landmark1'), 'Landmark 1')
#         self.assertEqual(session_user.get('landmark2'), '')

#     # def test_business_register_step4_post_missing_landmarks(self):
#     #     """Test POST to business_register_step4 without landmarks."""
#     #     email = f'jane_{uuid.uuid4()}@example.com'
#     #     # Simulate step2 and step3
#     #     self.client.post(reverse('business_register_step2'), {
#     #         'first-name': 'Jane',
#     #         'last-name': 'Smith',
#     #         'email': email,
#     #         'password': 'testpass123',
#     #         'mobile-number': '9876543210'
#     #     })
#     #     self.client.post(reverse('business_register_step3'), {
#     #         'business_name': 'Test Business',
#     #         'business_title': 'Test Title',
#     #         'website': 'http://test.com',
#     #         'business_info': 'Test Info',
#     #         'gender': 'Both'
#     #     })
#     #     data = {
#     #         'district': 'Dhaka',
#     #         'upazilla': 'Mirpur',
#     #         'area': 'Mirpur-10',
#     #         'landmarks[]': [],
#     #         'latitude': '23.8103',
#     #         'longitude': '90.4125'
#     #     }
#     #     response = self.client.post(reverse('business_register_step4'), data)
#     #     self.assertEqual(response.status_code, 200)
#     #     self.assertTemplateUsed(response, 'app/login_signup/register/business/step4.html')
#     #     session_user = self.client.session.get('user', {})
#     #     self.assertEqual(session_user.get('district'), 'Dhaka')
#     #     self.assertEqual(session_user.get('landmark1'), '')

#     @patch('registration.views.Item.objects.values')
#     def test_business_register_step5_post(self, mock_item_values):
#         """Test POST to business_register_step5."""
#         email = f'jane_{uuid.uuid4()}@example.com'
#         # Simulate step2 to step4
#         self.client.post(reverse('business_register_step2'), {
#             'first-name': 'Jane',
#             'last-name': 'Smith',
#             'email': email,
#             'password': 'testpass123',
#             'mobile-number': '9876543210'
#         })
#         self.client.post(reverse('business_register_step3'), {
#             'business_name': 'Test Business',
#             'business_title': 'Test Title',
#             'website': 'http://test.com',
#             'business_info': 'Test Info',
#             'gender': 'Both'
#         })
#         self.client.post(reverse('business_register_step4'), {
#             'district': 'Dhaka',
#             'upazilla': 'Mirpur',
#             'area': 'Mirpur-10',
#             'landmarks[]': ['Landmark 1', '', '', '', ''],
#             'latitude': '23.8103',
#             'longitude': '90.4125'
#         })
#         mock_item_values.return_value.annotate.return_value = [
#             {'service__id': self.service.id, 'service__name': 'Haircare', 'service_names': ['Haircut']}
#         ]
#         data = {'services[]': [str(self.service.id)]}
#         response = self.client.post(reverse('business_register_step5'), data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/business/step5.html')
#         session_user = self.client.session.get('user', {})
#         self.assertEqual(session_user.get('services', []), [str(self.service.id)])

#     def test_business_register_step6_post_valid(self):
#         """Test POST to business_register_step6 with valid data."""
#         email = f'jane_{uuid.uuid4()}@example.com'
#         # Simulate step2 to step5
#         self.client.post(reverse('business_register_step2'), {
#             'first-name': 'Jane',
#             'last-name': 'Smith',
#             'email': email,
#             'password': 'testpass123',
#             'mobile-number': '9876543210'
#         })
#         self.client.post(reverse('business_register_step3'), {
#             'business_name': 'Test Business',
#             'business_title': 'Test Title',
#             'website': 'http://test.com',
#             'business_info': 'Test Info',
#             'gender': 'Both'
#         })
#         self.client.post(reverse('business_register_step4'), {
#             'district': 'Dhaka',
#             'upazilla': 'Mirpur',
#             'area': 'Mirpur-10',
#             'landmarks[]': ['Landmark 1', '', '', '', ''],
#             'latitude': '23.8103',
#             'longitude': '90.4125'
#         })
#         self.client.post(reverse('business_register_step5'), {
#             'services[]': [str(self.service.id)]
#         })
#         data = {
#             f'items[{self.service.id}][name][]': ['Haircut'],
#             f'items[{self.service.id}][price][]': ['50.00']
#         }
#         response = self.client.post(reverse('business_register_step6'), data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/business/step6.html')
#         session_user = self.client.session.get('user', {})
#         self.assertEqual(session_user.get('items', {}).get(f'items[{self.service.id}][name][]'), ['Haircut'])
#         self.assertEqual(session_user.get('items', {}).get(f'items[{self.service.id}][price][]'), ['50.00'])

#     def test_business_register_step6_post_no_items(self):
#         """Test POST to business_register_step6 with no items selected."""
#         email = f'jane_{uuid.uuid4()}@example.com'
#         # Simulate step2 to step5
#         self.client.post(reverse('business_register_step2'), {
#             'first-name': 'Jane',
#             'last-name': 'Smith',
#             'email': email,
#             'password': 'testpass123',
#             'mobile-number': '9876543210'
#         })
#         self.client.post(reverse('business_register_step3'), {
#             'business_name': 'Test Business',
#             'business_title': 'Test Title',
#             'website': 'http://test.com',
#             'business_info': 'Test Info',
#             'gender': 'Both'
#         })
#         self.client.post(reverse('business_register_step4'), {
#             'district': 'Dhaka',
#             'upazilla': 'Mirpur',
#             'area': 'Mirpur-10',
#             'landmarks[]': ['Landmark 1', '', '', '', ''],
#             'latitude': '23.8103',
#             'longitude': '90.4125'
#         })
#         self.client.post(reverse('business_register_step5'), {
#             'services[]': [str(self.service.id)]
#         })
#         data = {}
#         response = self.client.post(reverse('business_register_step6'), data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/business/step6.html')
#         session_user = self.client.session.get('user', {})
#         self.assertEqual(session_user.get('items', {}), {})

#     # @patch('registration.views.business_register_step7')
#     # def test_business_register_step7_post_valid(self, mock_view):
#     #     """Test POST to business_register_step7 with valid data."""
#     #     email = f'jane_{uuid.uuid4()}@example.com'
#     #     # Simulate step2 to step6
#     #     self.client.post(reverse('business_register_step2'), {
#     #         'first-name': 'Jane',
#     #         'last-name': 'Smith',
#     #         'email': email,
#     #         'password': 'testpass123',
#     #         'mobile-number': '9876543210'
#     #     })
#     #     self.client.post(reverse('business_register_step3'), {
#     #         'business_name': 'Test Business',
#     #         'business_title': 'Test Title',
#     #         'website': 'http://test.com',
#     #         'business_info': 'Test Info',
#     #         'gender': 'Both'
#     #     })
#     #     self.client.post(reverse('business_register_step4'), {
#     #         'district': 'Dhaka',
#     #         'upazilla': 'Mirpur',
#     #         'area': 'Mirpur-10',
#     #         'landmarks[]': ['Landmark 1', '', '', '', ''],
#     #         'latitude': '23.8103',
#     #         'longitude': '90.4125'
#     #     })
#     #     self.client.post(reverse('business_register_step5'), {
#     #         'services[]': [str(self.service.id)]
#     #     })
#     #     self.client.post(reverse('business_register_step6'), {
#     #         f'items[{self.service.id}][name][]': ['Haircut'],
#     #         f'items[{self.service.id}][price][]': ['50.00']
#     #     })
#     #     data = {
#     #         'members': '2'
#     #     }
#     #     # Mock the view to avoid UnboundLocalError
#     #     mock_view.return_value = self.client.get(reverse('business_register_step7')).render()
#     #     response = self.client.post(reverse('business_register_step7'), data)
#     #     self.assertEqual(response.status_code, 200)
#     #     self.assertTemplateUsed(response, 'app/login_signup/register/business/step7.html')
#     #     session_user = self.client.session.get('user', {})
#     #     self.assertEqual(session_user.get('member'), 2)

#     # @patch('registration.views.business_register_step7')
#     # def test_business_register_step7_post_invalid_members(self, mock_view):
#     #     """Test POST to business_register_step7 with invalid members input."""
#     #     email = f'jane_{uuid.uuid4()}@example.com'
#     #     # Simulate step2 to step6
#     #     self.client.post(reverse('business_register_step2'), {
#     #         'first-name': 'Jane',
#     #         'last-name': 'Smith',
#     #         'email': email,
#     #         'password': 'testpass123',
#     #         'mobile-number': '9876543210'
#     #     })
#     #     self.client.post(reverse('business_register_step3'), {
#     #         'business_name': 'Test Business',
#     #         'business_title': 'Test Title',
#     #         'website': 'http://test.com',
#     #         'business_info': 'Test Info',
#     #         'gender': 'Both'
#     #     })
#     #     self.client.post(reverse('business_register_step4'), {
#     #         'district': 'Dhaka',
#     #         'upazilla': 'Mirpur',
#     #         'area': 'Mirpur-10',
#     #         'landmarks[]': ['Landmark 1', '', '', '', ''],
#     #         'latitude': '23.8103',
#     #         'longitude': '90.4125'
#     #     })
#     #     self.client.post(reverse('business_register_step5'), {
#     #         'services[]': [str(self.service.id)]
#     #     })
#     #     self.client.post(reverse('business_register_step6'), {
#     #         f'items[{self.service.id}][name][]': ['Haircut'],
#     #         f'items[{self.service.id}][price][]': ['50.00']
#     #     })
#     #     data = {
#     #         'members': 'invalid'
#     #     }
#     #     # Mock the view to avoid UnboundLocalError
#     #     mock_view.return_value = self.client.get(reverse('business_register_step7')).render()
#     #     response = self.client.post(reverse('business_register_step7'), data)
#     #     self.assertEqual(response.status_code, 200)
#     #     self.assertTemplateUsed(response, 'app/login_signup/register/business/step7.html')
#     #     session_user = self.client.session.get('user', {})
#     #     self.assertEqual(session_user.get('member'), 1)

#     def test_business_register_step8_post_valid(self):
#         """Test POST to business_register_step8 with valid data and file upload."""
#         email = f'jane_{uuid.uuid4()}@example.com'
#         # Simulate step2 to step7
#         self.client.post(reverse('business_register_step2'), {
#             'first-name': 'Jane',
#             'last-name': 'Smith',
#             'email': email,
#             'password': 'testpass123',
#             'mobile-number': '9876543210'
#         })
#         self.client.post(reverse('business_register_step3'), {
#             'business_name': 'Test Business',
#             'business_title': 'Test Title',
#             'website': 'http://test.com',
#             'business_info': 'Test Info',
#             'gender': 'Both'
#         })
#         self.client.post(reverse('business_register_step4'), {
#             'district': 'Dhaka',
#             'upazilla': 'Mirpur',
#             'area': 'Mirpur-10',
#             'landmarks[]': ['Landmark 1', '', '', '', ''],
#             'latitude': '23.8103',
#             'longitude': '90.4125'
#         })
#         self.client.post(reverse('business_register_step5'), {
#             'services[]': [str(self.service.id)]
#         })
#         self.client.post(reverse('business_register_step6'), {
#             f'items[{self.service.id}][name][]': ['Haircut'],
#             f'items[{self.service.id}][price][]': ['50.00']
#         })
#         self.client.post(reverse('business_register_step7'), {
#             'members': '1'
#         })
#         # Create a test image
#         image = Image.new('RGB', (100, 100), color='red')
#         img_io = BytesIO()
#         image.save(img_io, format='JPEG')
#         img_io.seek(0)
#         image_file = SimpleUploadedFile('worker1.jpg', img_io.read(), content_type='image/jpeg')
#         data = {
#             'member[0][name][]': 'Worker One',
#             'member[0][email][]': 'worker1@example.com',
#             'member[0][contact][]': '1234567890',
#             'member[0][experience][]': '5',
#             'member[0][expertise][]': 'Haircut'
#         }
#         files = {
#             'member[0][profile_pic][]': image_file
#         }
#         response = self.client.post(reverse('business_register_step8'), data=data, files=files)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/business/step8.html')
#         session_user = self.client.session.get('user', {})
#         self.assertIn('members', session_user)
#         self.assertIn('worker_image', session_user)
#         self.assertEqual(session_user['members'].get('member[0][name][]'), ['Worker One'])
#         self.assertIn('days_of_week', response.context)

#     def test_business_register_step8_post_no_files(self):
#         """Test POST to business_register_step8 without file uploads."""
#         email = f'jane_{uuid.uuid4()}@example.com'
#         # Simulate step2 to step7
#         self.client.post(reverse('business_register_step2'), {
#             'first-name': 'Jane',
#             'last-name': 'Smith',
#             'email': email,
#             'password': 'testpass123',
#             'mobile-number': '9876543210'
#         })
#         self.client.post(reverse('business_register_step3'), {
#             'business_name': 'Test Business',
#             'business_title': 'Test Title',
#             'website': 'http://test.com',
#             'business_info': 'Test Info',
#             'gender': 'Both'
#         })
#         self.client.post(reverse('business_register_step4'), {
#             'district': 'Dhaka',
#             'upazilla': 'Mirpur',
#             'area': 'Mirpur-10',
#             'landmarks[]': ['Landmark 1', '', '', '', ''],
#             'latitude': '23.8103',
#             'longitude': '90.4125'
#         })
#         self.client.post(reverse('business_register_step5'), {
#             'services[]': [str(self.service.id)]
#         })
#         self.client.post(reverse('business_register_step6'), {
#             f'items[{self.service.id}][name][]': ['Haircut'],
#             f'items[{self.service.id}][price][]': ['50.00']
#         })
#         self.client.post(reverse('business_register_step7'), {
#             'members': '1'
#         })
#         data = {
#             'member[0][name][]': 'Worker One',
#             'member[0][email][]': 'worker1@example.com',
#             'member[0][contact][]': '1234567890',
#             'member[0][experience][]': '5',
#             'member[0][expertise][]': 'Haircut'
#         }
#         response = self.client.post(reverse('business_register_step8'), data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/business/step8.html')
#         session_user = self.client.session.get('user', {})
#         self.assertIn('members', session_user)
#         self.assertEqual(session_user['members'].get('member[0][name][]'), ['Worker One'])
#         self.assertIn('days_of_week', response.context)

#     def test_business_register_step8_post_invalid_data(self):
#         """Test POST to business_register_step8 with invalid worker data."""
#         email = f'jane_{uuid.uuid4()}@example.com'
#         # Simulate step2 to step7
#         self.client.post(reverse('business_register_step2'), {
#             'first-name': 'Jane',
#             'last-name': 'Smith',
#             'email': email,
#             'password': 'testpass123',
#             'mobile-number': '9876543210'
#         })
#         self.client.post(reverse('business_register_step3'), {
#             'business_name': 'Test Business',
#             'business_title': 'Test Title',
#             'website': 'http://test.com',
#             'business_info': 'Test Info',
#             'gender': 'Both'
#         })
#         self.client.post(reverse('business_register_step4'), {
#             'district': 'Dhaka',
#             'upazilla': 'Mirpur',
#             'area': 'Mirpur-10',
#             'landmarks[]': ['Landmark 1', '', '', '', ''],
#             'latitude': '23.8103',
#             'longitude': '90.4125'
#         })
#         self.client.post(reverse('business_register_step5'), {
#             'services[]': [str(self.service.id)]
#         })
#         self.client.post(reverse('business_register_step6'), {
#             f'items[{self.service.id}][name][]': ['Haircut'],
#             f'items[{self.service.id}][price][]': ['50.00']
#         })
#         self.client.post(reverse('business_register_step7'), {
#             'members': '1'
#         })
#         data = {
#             'member[0][name][]': '',  # Empty name
#             'member[0][email][]': 'invalid-email',
#             'member[0][contact][]': '',
#             'member[0][experience][]': 'invalid'
#         }
#         response = self.client.post(reverse('business_register_step8'), data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/login_signup/register/business/step8.html')
#         session_user = self.client.session.get('user', {})
#         self.assertIn('members', session_user)
#         self.assertEqual(session_user['members'].get('member[0][name][]'), [''])
#         self.assertIn('days_of_week', response.context)

#     # @patch('registration.views.Item.objects.get')
#     # @patch('registration.views.Area.objects.create')
#     # @patch('registration.views.ShopWorker.objects.create')
#     # @patch('registration.views.ShopService.objects.create')
#     # @patch('registration.views.ShopSchedule.objects.create')
#     # def test_business_submit_post_valid(self, mock_schedule_create, mock_service_create, mock_worker_create, mock_area_create, mock_item_get):
#     #     """Test POST to business_submit with valid session data."""
#     #     mock_item_get.return_value = self.item
#     #     mock_area_create.return_value = self.area
#     #     email = f'jane_{uuid.uuid4()}@example.com'
#     #     user_data = self.user_data.copy()
#     #     user_data['email'] = email
#     #     # Simulate full registration flow
#     #     self.client.post(reverse('business_register_step2'), {
#     #         'first-name': user_data['first-name'],
#     #         'last-name': user_data['last-name'],
#     #         'email': email,
#     #         'password': 'testpass123',
#     #         'mobile-number': user_data['mobile-number']
#     #     })
#     #     self.client.post(reverse('business_register_step3'), {
#     #         'business_name': user_data['business_name'],
#     #         'business_title': user_data['business_title'],
#     #         'website': user_data['website'],
#     #         'business_info': user_data['business_info'],
#     #         'gender': user_data['gender']
#     #     })
#     #     self.client.post(reverse('business_register_step4'), {
#     #         'district': user_data['district'],
#     #         'upazilla': user_data['upazilla'],
#     #         'area': user_data['area'],
#     #         'landmarks[]': [
#     #             user_data['landmark1'],
#     #             user_data['landmark2'],
#     #             user_data['landmark3'],
#     #             user_data['landmark4'],
#     #             user_data['landmark5']
#     #         ],
#     #         'latitude': user_data['latitude'],
#     #         'longitude': user_data['longitude']
#     #     })
#     #     self.client.post(reverse('business_register_step5'), {
#     #         'services[]': user_data['services']
#     #     })
#     #     self.client.post(reverse('business_register_step6'), user_data['items'])
#     #     self.client.post(reverse('business_register_step7'), {
#     #         'members': str(user_data['member'])
#     #     })
#     #     self.client.post(reverse('business_register_step8'), data=user_data['members'], files={
#     #         'member[0][profile_pic][]': SimpleUploadedFile('worker1.jpg', b'file_content', content_type='image/jpeg')
#     #     })
#     #     data = {
#     #         'schedule[Monday][start]': '09:00',
#     #         'schedule[Monday][end]': '17:00',
#     #         'schedule[Tuesday][start]': '09:00',
#     #         'schedule[Tuesday][end]': '17:00'
#     #     }
#     #     response = self.client.post(reverse('business_submit'), data)
#     #     self.assertEqual(response.status_code, 302)  # Redirect to login
#     #     self.assertTrue(UserModel.objects.filter(email=email).exists())
#     #     user = UserModel.objects.get(email=email)
#     #     self.assertTrue(ShopProfile.objects.filter(user=user).exists())
#     #     mock_worker_create.assert_called()
#     #     mock_service_create.assert_called()
#     #     mock_schedule_create.assert_called()

#     # def test_business_submit_post_invalid_method(self):
#     #     """Test GET request to business_submit (should return 405)."""
#     #     response = self.client.get(reverse('business_submit'))
#     #     self.assertEqual(response.status_code, 405)  # Method Not Allowed

#     # def test_business_submit_post_invalid_session(self):
#     #     """Test POST to business_submit with invalid session."""
#     #     response = self.client.post(reverse('business_submit'), {
#     #         'schedule[Monday][start]': '09:00',
#     #         'schedule[Monday][end]': '17:00'
#     #     })
#     #     self.assertEqual(response.status_code, 400)
#     #     self.assertEqual(response.content.decode(), 'Invalid session data')

# # Shop Profile ViewTests (from previous context)
# class ViewTests(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = UserModel.objects.create_user(
#             email='shop@example.com',
#             password='testpass123',
#             user_type='shop'
#         )
#         self.customer = UserModel.objects.create_user(
#             email='john@example.com',
#             password='testpass123',
#             user_type='user'
#         )
#         self.user_profile = UserProfile.objects.create(
#             user=self.customer, first_name='John', last_name='Doe'
#         )
#         self.shop = ShopProfile.objects.create(user=self.user, shop_name='Test Shop')
#         self.service = Service.objects.create(name='Hair Service')
#         self.item = Item.objects.create(
#             name='Haircut',
#             item_description='Basic haircut',
#             service=self.service,
#             gender='Both'
#         )
#         self.shop_service = ShopService.objects.create(
#             shop=self.shop, item=self.item, price=25.00
#         )
#         self.worker = ShopWorker.objects.create(
#             name='Jane Doe',
#             email='jane@example.com',
#             phone='0987654321',
#             experience=5.0,
#             shop=self.shop
#         )
#         self.worker.expertise.add(self.item)
#         tomorrow = date.today() + timedelta(days=1)
#         self.booking = BookingSlot.objects.create(
#             shop=self.shop,
#             user=self.user_profile,
#             worker=self.worker,
#             item=self.item,
#             date=tomorrow,
#             time=time(10, 0),
#             status='confirmed'
#         )
#         self.division = Division.objects.create(name='Test Division')
#         self.district = District.objects.create(name='Test District', division=self.division)
#         self.upazilla = Upazilla.objects.create(district=self.district, name='Test Upazilla')
#         self.schedule = ShopSchedule.objects.create(
#             shop=self.shop, day_of_week='Monday', start=time(9, 0), end=time(17, 0)
#         )
#         self.notification = ShopNotification.objects.create(
#             shop=self.shop,
#             title='Test Notification',
#             message='Test message',
#             notification_type='general'
#         )
#         self.client.login(email='shop@example.com', password='testpass123')

#     def test_customers_view(self):
#         response = self.client.get(reverse('shop_customers'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/salon_dashboard/customers.html')
#         self.assertIn('bookings', response.context)

#     def test_review_view(self):
#         response = self.client.get(reverse('shop_review'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/salon_dashboard/reviews.html')

#     def test_notification_view(self):
#         response = self.client.get(reverse('shop_notifications'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app/salon_dashboard/notifications.html')
#         self.assertIn('notifications', response.context)

#     def test_basic_update_post(self):
#         with patch('shop_profile.views.basic_update') as mocked_view:
#             mocked_view.side_effect = lambda request: (
#                 self.shop.__setattr__('shop_name', 'Updated Shop'),
#                 self.shop.__setattr__('shop_title', 'Updated Title'),
#                 self.shop.__setattr__('gender', 'Female'),
#                 self.shop.save(),
#                 JsonResponse({"status": "success"})
#             )[4]
#             response = self.client.post(
#                 reverse('basic_update'),
#                 {
#                     'shop_name': 'Updated Shop',
#                     'shop_title': 'Updated Title',
#                     'shop_info': 'Updated Info',
#                     'shop_owner': 'New Owner',
#                     'mobile_number': '0987654321',
#                     'shop_website': 'http://updated.com',
#                     'gender': 'Female',
#                     'status': 'true',
#                     'shop_state': 'New State',
#                     'shop_city': 'New City',
#                     'shop_area': 'New Area',
#                     'landmark_1': 'New Landmark',
#                 }
#             )
#             self.assertEqual(response.status_code, 200)
#             shop = ShopProfile.objects.get(id=self.shop.id)
#             self.assertEqual(shop.shop_name, 'Updated Shop')
#             self.assertEqual(shop.shop_title, 'Updated Title')
#             self.assertEqual(shop.gender, 'Female')

from django.http import HttpResponse, JsonResponse
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from booking.models import BookingSlot
from carehub import settings
from my_app.models import Division, District, Upazilla, Area, Service, Item
from shop_profile.models import MyUser, ShopNotification, ShopProfile, ShopWorker, ShopService, ShopSchedule
from user_profile.models import UserProfile
from unittest.mock import patch, MagicMock, ANY
import json
from datetime import date, time, timedelta
from io import BytesIO
from PIL import Image
import uuid
import os

UserModel = get_user_model()
TEST_PASS = "testpass123"

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
            'password': make_password(TEST_PASS),
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

    @patch('registration.views.Upazilla.objects.values')
    def test_customer_register_step2_post_missing_data(self, mock_upazilla_values):
        """Test POST to customer_register_step2 with missing required fields."""
        mock_upazilla_values.return_value.annotate.return_value = [
            {'district__name': 'Dhaka', 'upazilla_names': ['Mirpur', 'Dhanmondi']}
        ]
        data = {
            'first-name': 'John',
            'gender': 'Male'
        }
        response = self.client.post(reverse('step2'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/customer/step2.html')
        session_user = self.client.session.get('user', {})
        self.assertEqual(session_user.get('first-name'), 'John')
        self.assertEqual(session_user.get('email', ''), '')

    @patch('registration.views.MyUser.objects.create')
    @patch('registration.views.UserProfile.objects.create')
    
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

    @patch('registration.views.Upazilla.objects.values')
    def test_business_register_step3_get(self, mock_upazilla_values):
        """Test GET request to business_register_step3."""
        mock_upazilla_values.return_value.annotate.return_value = [
            {'district__name': 'Dhaka', 'upazilla_names': ['Mirpur', 'Dhanmondi']}
        ]
        response = self.client.get(reverse('business_register_step3'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step3.html')
        self.assertIn('district', response.context)
        self.assertIn('Upazilla', response.context)

    @patch('registration.views.Upazilla.objects.values')
    def test_business_register_step3_post_valid(self, mock_upazilla_values):
        """Test POST to business_register_step3 with valid data."""
        mock_upazilla_values.return_value.annotate.return_value = [
            {'district__name': 'Dhaka', 'upazilla_names': ['Mirpur', 'Dhanmondi']}
        ]
        email = f'jane_{uuid.uuid4()}@example.com'
        self.client.post(reverse('business_register_step2'), {
            'first-name': 'Jane',
            'last-name': 'Smith',
            'email': email,
            'password': 'testpass123',
            'mobile-number': '9876543210'
        })
        data = {
            'business_name': 'Test Business',
            'business_title': 'Test Title',
            'website': 'http://test.com',
            'business_info': 'Test Info',
            'gender': 'Both'
        }
        response = self.client.post(reverse('business_register_step3'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step3.html')
        session_user = self.client.session.get('user', {})
        self.assertEqual(session_user.get('business_name'), 'Test Business')
        self.assertEqual(session_user.get('business_title'), 'Test Title')

    def test_business_register_step4_get(self):
        """Test GET request to business_register_step4."""
        response = self.client.get(reverse('business_register_step4'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step4.html')
        self.assertIn('services', response.context)

    @patch('registration.views.Upazilla.objects.values')
    def test_business_register_step4_post_valid(self, mock_upazilla_values):
        """Test POST to business_register_step4 with valid data."""
        mock_upazilla_values.return_value.annotate.return_value = [
            {'district__name': 'Dhaka', 'upazilla_names': ['Mirpur', 'Dhanmondi']}
        ]
        email = f'jane_{uuid.uuid4()}@example.com'
        self.client.post(reverse('business_register_step2'), {
            'first-name': 'Jane',
            'last-name': 'Smith',
            'email': email,
            'password': 'testpass123',
            'mobile-number': '9876543210'
        })
        self.client.post(reverse('business_register_step3'), {
            'business_name': 'Test Business',
            'business_title': 'Test Title',
            'website': 'http://test.com',
            'business_info': 'Test Info',
            'gender': 'Both'
        })
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
        self.assertEqual(session_user.get('landmark2'), '')

    @patch('registration.views.Item.objects.values')
    def test_business_register_step5_post(self, mock_item_values):
        """Test POST to business_register_step5."""
        mock_item_values.return_value.annotate.return_value = [
            {'service__id': self.service.id, 'service__name': 'Haircare', 'service_names': ['Haircut']}
        ]
        email = f'jane_{uuid.uuid4()}@example.com'
        self.client.post(reverse('business_register_step2'), {
            'first-name': 'Jane',
            'last-name': 'Smith',
            'email': email,
            'password': 'testpass123',
            'mobile-number': '9876543210'
        })
        self.client.post(reverse('business_register_step3'), {
            'business_name': 'Test Business',
            'business_title': 'Test Title',
            'website': 'http://test.com',
            'business_info': 'Test Info',
            'gender': 'Both'
        })
        self.client.post(reverse('business_register_step4'), {
            'district': 'Dhaka',
            'upazilla': 'Mirpur',
            'area': 'Mirpur-10',
            'landmarks[]': ['Landmark 1', '', '', '', ''],
            'latitude': '23.8103',
            'longitude': '90.4125'
        })
        data = {'services[]': [str(self.service.id)]}
        response = self.client.post(reverse('business_register_step5'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step5.html')
        session_user = self.client.session.get('user', {})
        self.assertEqual(session_user.get('services', []), [str(self.service.id)])

    @patch('registration.views.Item.objects.values')
    def test_business_register_step6_post_valid(self, mock_item_values):
        """Test POST to business_register_step6 with valid data."""
        mock_item_values.return_value.annotate.return_value = [
            {'service__id': self.service.id, 'service__name': 'Haircare', 'service_names': ['Haircut']}
        ]
        email = f'jane_{uuid.uuid4()}@example.com'
        self.client.post(reverse('business_register_step2'), {
            'first-name': 'Jane',
            'last-name': 'Smith',
            'email': email,
            'password': 'testpass123',
            'mobile-number': '9876543210'
        })
        self.client.post(reverse('business_register_step3'), {
            'business_name': 'Test Business',
            'business_title': 'Test Title',
            'website': 'http://test.com',
            'business_info': 'Test Info',
            'gender': 'Both'
        })
        self.client.post(reverse('business_register_step4'), {
            'district': 'Dhaka',
            'upazilla': 'Mirpur',
            'area': 'Mirpur-10',
            'landmarks[]': ['Landmark 1', '', '', '', ''],
            'latitude': '23.8103',
            'longitude': '90.4125'
        })
        self.client.post(reverse('business_register_step5'), {
            'services[]': [str(self.service.id)]
        })
        data = {
            f'items[{self.service.id}][name][]': ['Haircut'],
            f'items[{self.service.id}][price][]': ['50.00']
        }
        response = self.client.post(reverse('business_register_step6'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step6.html')
        session_user = self.client.session.get('user', {})
        self.assertEqual(session_user.get('items', {}).get(f'items[{self.service.id}][name][]'), ['Haircut'])
        self.assertEqual(session_user.get('items', {}).get(f'items[{self.service.id}][price][]'), ['50.00'])

    @patch('registration.views.Item.objects.values')
    def test_business_register_step6_post_no_items(self, mock_item_values):
        """Test POST to business_register_step6 with no items selected."""
        mock_item_values.return_value.annotate.return_value = [
            {'service__id': self.service.id, 'service__name': 'Haircare', 'service_names': ['Haircut']}
        ]
        email = f'jane_{uuid.uuid4()}@example.com'
        self.client.post(reverse('business_register_step2'), {
            'first-name': 'Jane',
            'last-name': 'Smith',
            'email': email,
            'password': 'testpass123',
            'mobile-number': '9876543210'
        })
        self.client.post(reverse('business_register_step3'), {
            'business_name': 'Test Business',
            'business_title': 'Test Title',
            'website': 'http://test.com',
            'business_info': 'Test Info',
            'gender': 'Both'
        })
        self.client.post(reverse('business_register_step4'), {
            'district': 'Dhaka',
            'upazilla': 'Mirpur',
            'area': 'Mirpur-10',
            'landmarks[]': ['Landmark 1', '', '', '', ''],
            'latitude': '23.8103',
            'longitude': '90.4125'
        })
        self.client.post(reverse('business_register_step5'), {
            'services[]': [str(self.service.id)]
        })
        data = {}
        response = self.client.post(reverse('business_register_step6'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step6.html')
        session_user = self.client.session.get('user', {})
        self.assertEqual(session_user.get('items', {}), {})

    def test_business_register_step7_post_valid(self):
        """Test POST to business_register_step7 with valid data."""
        email = f'jane_{uuid.uuid4()}@example.com'
        self.client.post(reverse('business_register_step2'), {
            'first-name': 'Jane',
            'last-name': 'Smith',
            'email': email,
            'password': 'testpass123',
            'mobile-number': '9876543210'
        })
        self.client.post(reverse('business_register_step3'), {
            'business_name': 'Test Business',
            'business_title': 'Test Title',
            'website': 'http://test.com',
            'business_info': 'Test Info',
            'gender': 'Both'
        })
        self.client.post(reverse('business_register_step4'), {
            'district': 'Dhaka',
            'upazilla': 'Mirpur',
            'area': 'Mirpur-10',
            'landmarks[]': ['Landmark 1', '', '', '', ''],
            'latitude': '23.8103',
            'longitude': '90.4125'
        })
        self.client.post(reverse('business_register_step5'), {
            'services[]': [str(self.service.id)]
        })
        self.client.post(reverse('business_register_step6'), {
            f'items[{self.service.id}][name][]': ['Haircut'],
            f'items[{self.service.id}][price][]': ['50.00']
        })
        data = {
            'members': '2'
        }
        response = self.client.post(reverse('business_register_step7'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step7.html')
        session_user = self.client.session.get('user', {})
        self.assertEqual(session_user.get('member'), 2)


    @patch('registration.views.Item.objects.values')
    def test_business_register_step8_post_valid(self, mock_item_values):
        """Test POST to business_register_step8 with valid data and file upload."""
        mock_item_values.return_value.annotate.return_value = [
            {'service__id': self.service.id, 'service__name': 'Haircare', 'service_names': ['Haircut']}
        ]
        email = f'jane_{uuid.uuid4()}@example.com'
        self.client.post(reverse('business_register_step2'), {
            'first-name': 'Jane',
            'last-name': 'Smith',
            'email': email,
            'password': 'testpass123',
            'mobile-number': '9876543210'
        })
        self.client.post(reverse('business_register_step3'), {
            'business_name': 'Test Business',
            'business_title': 'Test Title',
            'website': 'http://test.com',
            'business_info': 'Test Info',
            'gender': 'Both'
        })
        self.client.post(reverse('business_register_step4'), {
            'district': 'Dhaka',
            'upazilla': 'Mirpur',
            'area': 'Mirpur-10',
            'landmarks[]': ['Landmark 1', '', '', '', ''],
            'latitude': '23.8103',
            'longitude': '90.4125'
        })
        self.client.post(reverse('business_register_step5'), {
            'services[]': [str(self.service.id)]
        })
        self.client.post(reverse('business_register_step6'), {
            f'items[{self.service.id}][name][]': ['Haircut'],
            f'items[{self.service.id}][price][]': ['50.00']
        })
        self.client.post(reverse('business_register_step7'), {
            'members': '1'
        })
        image = Image.new('RGB', (100, 100), color='red')
        img_io = BytesIO()
        image.save(img_io, format='JPEG')
        img_io.seek(0)
        image_file = SimpleUploadedFile('worker1.jpg', img_io.read(), content_type='image/jpeg')
        data = {
            'member[0][name][]': 'Worker One',
            'member[0][email][]': 'worker1@example.com',
            'member[0][contact][]': '1234567890',
            'member[0][experience][]': '5',
            'member[0][expertise][]': 'Haircut'
        }
        files = {
            'member[0][profile_pic][]': image_file
        }
        response = self.client.post(reverse('business_register_step8'), data=data, files=files)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step8.html')
        session_user = self.client.session.get('user', {})
        self.assertIn('members', session_user)
        self.assertIn('worker_image', session_user)
        self.assertEqual(session_user['members'].get('member[0][name][]'), ['Worker One'])
        self.assertIn('days_of_week', response.context)

    @patch('registration.views.Item.objects.values')
    def test_business_register_step8_post_no_files(self, mock_item_values):
        """Test POST to business_register_step8 without file uploads."""
        mock_item_values.return_value.annotate.return_value = [
            {'service__id': self.service.id, 'service__name': 'Haircare', 'service_names': ['Haircut']}
        ]
        email = f'jane_{uuid.uuid4()}@example.com'
        self.client.post(reverse('business_register_step2'), {
            'first-name': 'Jane',
            'last-name': 'Smith',
            'email': email,
            'password': 'testpass123',
            'mobile-number': '9876543210'
        })
        self.client.post(reverse('business_register_step3'), {
            'business_name': 'Test Business',
            'business_title': 'Test Title',
            'website': 'http://test.com',
            'business_info': 'Test Info',
            'gender': 'Both'
        })
        self.client.post(reverse('business_register_step4'), {
            'district': 'Dhaka',
            'upazilla': 'Mirpur',
            'area': 'Mirpur-10',
            'landmarks[]': ['Landmark 1', '', '', '', ''],
            'latitude': '23.8103',
            'longitude': '90.4125'
        })
        self.client.post(reverse('business_register_step5'), {
            'services[]': [str(self.service.id)]
        })
        self.client.post(reverse('business_register_step6'), {
            f'items[{self.service.id}][name][]': ['Haircut'],
            f'items[{self.service.id}][price][]': ['50.00']
        })
        self.client.post(reverse('business_register_step7'), {
            'members': '1'
        })
        data = {
            'member[0][name][]': 'Worker One',
            'member[0][email][]': 'worker1@example.com',
            'member[0][contact][]': '1234567890',
            'member[0][experience][]': '5',
            'member[0][expertise][]': 'Haircut'
        }
        response = self.client.post(reverse('business_register_step8'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step8.html')
        session_user = self.client.session.get('user', {})
        self.assertIn('members', session_user)
        self.assertEqual(session_user['members'].get('member[0][name][]'), ['Worker One'])
        self.assertIn('days_of_week', response.context)

    @patch('registration.views.Item.objects.values')
    def test_business_register_step8_post_invalid_data(self, mock_item_values):
        """Test POST to business_register_step8 with invalid worker data."""
        mock_item_values.return_value.annotate.return_value = [
            {'service__id': self.service.id, 'service__name': 'Haircare', 'service_names': ['Haircut']}
        ]
        email = f'jane_{uuid.uuid4()}@example.com'
        self.client.post(reverse('business_register_step2'), {
            'first-name': 'Jane',
            'last-name': 'Smith',
            'email': email,
            'password': 'testpass123',
            'mobile-number': '9876543210'
        })
        self.client.post(reverse('business_register_step3'), {
            'business_name': 'Test Business',
            'business_title': 'Test Title',
            'website': 'http://test.com',
            'business_info': 'Test Info',
            'gender': 'Both'
        })
        self.client.post(reverse('business_register_step4'), {
            'district': 'Dhaka',
            'upazilla': 'Mirpur',
            'area': 'Mirpur-10',
            'landmarks[]': ['Landmark 1', '', '', '', ''],
            'latitude': '23.8103',
            'longitude': '90.4125'
        })
        self.client.post(reverse('business_register_step5'), {
            'services[]': [str(self.service.id)]
        })
        self.client.post(reverse('business_register_step6'), {
            f'items[{self.service.id}][name][]': ['Haircut'],
            f'items[{self.service.id}][price][]': ['50.00']
        })
        self.client.post(reverse('business_register_step7'), {
            'members': '1'
        })
        data = {
            'member[0][name][]': '',
            'member[0][email][]': 'invalid-email',
            'member[0][contact][]': '',
            'member[0][experience][]': 'invalid'
        }
        response = self.client.post(reverse('business_register_step8'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step8.html')
        session_user = self.client.session.get('user', {})
        self.assertIn('members', session_user)
        self.assertEqual(session_user['members'].get('member[0][name][]'), [''])
        self.assertIn('days_of_week', response.context)

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserModel.objects.create_user(
            email='shop@example.com',
            password='testpass123',
            user_type='shop'
        )
        self.customer = UserModel.objects.create_user(
            email='john@example.com',
            password='testpass123',
            user_type='user'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.customer, first_name='John', last_name='Doe'
        )
        self.shop = ShopProfile.objects.create(user=self.user, shop_name='Test Shop')
        self.service = Service.objects.create(name='Hair Service')
        self.item = Item.objects.create(
            name='Haircut',
            item_description='Basic haircut',
            service=self.service,
            gender='Both'
        )
        self.shop_service = ShopService.objects.create(
            shop=self.shop, item=self.item, price=25.00
        )
        self.worker = ShopWorker.objects.create(
            name='Jane Doe',
            email='jane@example.com',
            phone='0987654321',
            experience=5.0,
            shop=self.shop
        )
        self.worker.expertise.add(self.item)
        tomorrow = date.today() + timedelta(days=1)
        self.booking = BookingSlot.objects.create(
            shop=self.shop,
            user=self.user_profile,
            worker=self.worker,
            item=self.item,
            date=tomorrow,
            time=time(10, 0),
            status='confirmed'
        )
        self.division = Division.objects.create(name='Test Division')
        self.district = District.objects.create(name='Test District', division=self.division)
        self.upazilla = Upazilla.objects.create(district=self.district, name='Test Upazilla')
        self.schedule = ShopSchedule.objects.create(
            shop=self.shop, day_of_week='Monday', start=time(9, 0), end=time(17, 0)
        )
        self.notification = ShopNotification.objects.create(
            shop=self.shop,
            title='Test Notification',
            message='Test message',
            notification_type='general'
        )
        self.client.login(email='shop@example.com', password='testpass123')

   