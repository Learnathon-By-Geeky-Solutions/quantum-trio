from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages import get_messages
from registration.views import (
    select_user_type, customer_register_step1, customer_register_step2,
    customer_submit, business_register_step1, business_register_step2,
    business_register_step3
)
from registration.forms import Step1Form, Step2Form, Step3Form
from shop_profile.models import MyUser, ShopProfile
from user_profile.models import UserProfile
from my_app.models import District, Upazilla
from unittest.mock import patch
import uuid

class RegistrationAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password123',
            'country_code': '+880',
            'mobile_number': '1234567890',
            'terms': True,
            'gender': 'Male'
        }
        self.district_data = [
            {'id': 1, 'name': 'Dhaka'},
            {'id': 2, 'name': 'Chittagong'}
        ]
        self.upazilla_data = [
            {'district__name': 'Dhaka', 'upazilla_names': ['Mirpur', 'Gulshan']},
            {'district__name': 'Chittagong', 'upazilla_names': ['Hathazari']}
        ]

    # Helper method to add session and messages middleware to requests
    def _add_middleware(self, request):
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        messages_middleware = MessageMiddleware(lambda x: None)
        messages_middleware.process_request(request)
        return request

    # URL Tests
    def test_url_select_user_type(self):
        url = reverse('select_user_type')
        self.assertEqual(url, '/register/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, select_user_type)

    def test_url_customer_register_step1(self):
        url = reverse('customer_register_step1')
        self.assertEqual(url, '/register/customer/step1')
        resolver = resolve(url)
        self.assertEqual(resolver.func, customer_register_step1)

    def test_url_customer_register_step2(self):
        url = reverse('customer_register_step2')
        self.assertEqual(url, '/register/customer/step2')
        resolver = resolve(url)
        self.assertEqual(resolver.func, customer_register_step2)

    def test_url_customer_submit(self):
        url = reverse('customer_submit')
        self.assertEqual(url, '/register/customer/submit')
        resolver = resolve(url)
        self.assertEqual(resolver.func, customer_submit)

    def test_url_business_register_step1(self):
        url = reverse('business_register_step1')
        self.assertEqual(url, '/register/business/step1')
        resolver = resolve(url)
        self.assertEqual(resolver.func, business_register_step1)

    def test_url_business_register_step2(self):
        url = reverse('business_register_step2')
        self.assertEqual(url, '/register/business/step2')
        resolver = resolve(url)
        self.assertEqual(resolver.func, business_register_step2)

    def test_url_business_register_step3(self):
        url = reverse('business_register_step3')
        self.assertEqual(url, '/register/business/step3')
        resolver = resolve(url)
        self.assertEqual(resolver.func, business_register_step3)

    # View Tests: select_user_type
    def test_select_user_type_get(self):
        response = self.client.get(reverse('select_user_type'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/sign-up.html')

    # View Tests: customer_register_step1
    def test_customer_register_step1_get(self):
        response = self.client.get(reverse('customer_register_step1'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/customer/step1.html')
        self.assertIsInstance(response.context['form'], Step1Form)


    def test_customer_register_step1_post_invalid(self):
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'invalid_email'
        response = self.client.post(reverse('customer_register_step1'), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/customer/step1.html')
        self.assertFalse(response.context['form'].is_valid())

    # View Tests: customer_register_step2
    @patch('registration.views.District.objects.all')
    @patch('registration.views.Upazilla.objects.values')
    def test_customer_register_step2_get_no_session(self, mock_upazilla, mock_district):
        response = self.client.get(reverse('customer_register_step2'))
        self.assertRedirects(response, reverse('customer_register_step1'))

    @patch('registration.views.District.objects.all')
    @patch('registration.views.Upazilla.objects.values')
    def test_customer_register_step2_get(self, mock_upazilla, mock_district):
        mock_district.return_value.values.return_value = self.district_data
        mock_upazilla.return_value.annotate.return_value = self.upazilla_data
        # Set session data
        session = self.client.session
        session['step1_data'] = self.user_data
        session.save()
        response = self.client.get(reverse('customer_register_step2'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/customer/step2.html')


    # View Tests: business_register_step1
    def test_business_register_step1_get(self):
        response = self.client.get(reverse('business_register_step1'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step1.html')
        self.assertIsInstance(response.context['form'], Step1Form)

    def test_business_register_step1_post_valid(self):
        response = self.client.post(reverse('business_register_step1'), self.user_data)
        self.assertRedirects(response, reverse('business_register_step2'))
        self.assertEqual(self.client.session.get('step1_data'), self.user_data)

    # View Tests: business_register_step2
    def test_business_register_step2_get_no_session(self):
        response = self.client.get(reverse('business_register_step2'))
        self.assertRedirects(response, reverse('business_register_step1'))

    def test_business_register_step2_get(self):
        # Set session data
        session = self.client.session
        session['step1_data'] = self.user_data
        session.save()
        response = self.client.get(reverse('business_register_step2'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step2.html')

    def test_business_register_step2_post_valid(self):
        business_data = {
            'business_name': 'Test Shop',
            'business_title': 'Test Title',
            'business_info': 'This is a test business.',
            'gender': 'male'
        }
        request = self.factory.post(reverse('business_register_step2'), business_data)
        request = self._add_middleware(request)
        request.session['step1_data'] = self.user_data
        response = business_register_step2(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('business_register_step3'))

    # View Tests: business_register_step3
    @patch('registration.views.District.objects.all')
    @patch('registration.views.Upazilla.objects.values')
    def test_business_register_step3_get_no_session(self, mock_upazilla, mock_district):
        response = self.client.get(reverse('business_register_step3'))
        self.assertRedirects(response, reverse('business_register_step1'))


    # Form Tests: Step1Form
    def test_step1_form_valid(self):
        form = Step1Form(data=self.user_data)
        self.assertTrue(form.is_valid())

    def test_step1_form_invalid_email(self):
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'invalid_email'
        form = Step1Form(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_step1_form_duplicate_email(self):
        MyUser.objects.create_user(email=self.user_data['email'], password='testpass', user_type='user')
        form = Step1Form(data=self.user_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    # Form Tests: Step2Form
    def test_step2_form_valid(self):
        form = Step2Form(data={
            'business_name': 'Test Shop',
            'business_title': 'Test Title',
            'business_info': 'This is a test business.',
            'gender': 'male'
        })
        self.assertTrue(form.is_valid())

    def test_step2_form_invalid_business_info(self):
        form = Step2Form(data={
            'business_name': 'Test Shop',
            'business_title': 'Test Title',
            'business_info': 'Short',
            'gender': 'male'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('business_info', form.errors)

    # Form Tests: Step3Form
    def test_step3_form_valid_customer(self):
        form = Step3Form(
            data={
                'district': 'Dhaka',
                'upazilla': 'Mirpur',
                'area': 'Test Area',
                'latitude': 23.8103,
                'longitude': 90.4125
            },
            user_type='customer',
            districts=self.district_data,
            upazillas=['Mirpur', 'Gulshan']
        )
        self.assertTrue(form.is_valid())

    def test_step3_form_valid_shop(self):
        form = Step3Form(
            data={
                'district': 'Dhaka',
                'upazilla': 'Mirpur',
                'area': 'Test Area',
                'shop_landmark_1': 'Landmark 1',
                'shop_landmark_2': 'Landmark 2',
                'shop_landmark_3': 'Landmark 3',
                'latitude': 23.8103,
                'longitude': 90.4125
            },
            user_type='shop',
            districts=self.district_data,
            upazillas=['Mirpur', 'Gulshan']
        )
        self.assertTrue(form.is_valid())


from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages import get_messages
from registration.views import (
    select_user_type, customer_register_step1, customer_register_step2,
    customer_submit, business_register_step1, business_register_step2,
    business_register_step3
)
from registration.forms import Step1Form, Step2Form, Step3Form
from shop_profile.models import MyUser, ShopProfile, ShopSchedule
from user_profile.models import UserProfile
from my_app.models import District, Upazilla, Area
from unittest.mock import patch
from datetime import time
import uuid

class RegistrationAppTests1(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password123',
            'country_code': '+880',
            'mobile_number': '1234567890',
            'terms': True,
            'gender': 'Male'
        }
        self.district_data = [
            {'id': 1, 'name': 'Dhaka'},
            {'id': 2, 'name': 'Chittagong'}
        ]
        self.upazilla_data = [
            {'district__name': 'Dhaka', 'upazilla_names': ['Mirpur', 'Gulshan']},
            {'district__name': 'Chittagong', 'upazilla_names': ['Hathazari']}
        ]

    # Helper method to add session and messages middleware to requests
    def _add_middleware(self, request):
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        messages_middleware = MessageMiddleware(lambda x: None)
        messages_middleware.process_request(request)
        return request

    # URL Tests
    def test_url_select_user_type(self):
        url = reverse('select_user_type')
        self.assertEqual(url, '/register/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, select_user_type)

    def test_url_customer_register_step1(self):
        url = reverse('customer_register_step1')
        self.assertEqual(url, '/register/customer/step1')
        resolver = resolve(url)
        self.assertEqual(resolver.func, customer_register_step1)

    def test_url_customer_register_step2(self):
        url = reverse('customer_register_step2')
        self.assertEqual(url, '/register/customer/step2')
        resolver = resolve(url)
        self.assertEqual(resolver.func, customer_register_step2)

    def test_url_customer_submit(self):
        url = reverse('customer_submit')
        self.assertEqual(url, '/register/customer/submit')
        resolver = resolve(url)
        self.assertEqual(resolver.func, customer_submit)

    def test_url_business_register_step1(self):
        url = reverse('business_register_step1')
        self.assertEqual(url, '/register/business/step1')
        resolver = resolve(url)
        self.assertEqual(resolver.func, business_register_step1)

    def test_url_business_register_step2(self):
        url = reverse('business_register_step2')
        self.assertEqual(url, '/register/business/step2')
        resolver = resolve(url)
        self.assertEqual(resolver.func, business_register_step2)

    def test_url_business_register_step3(self):
        url = reverse('business_register_step3')
        self.assertEqual(url, '/register/business/step3')
        resolver = resolve(url)
        self.assertEqual(resolver.func, business_register_step3)

    # View Tests: select_user_type
    def test_select_user_type_get(self):
        response = self.client.get(reverse('select_user_type'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/sign-up.html')

    # View Tests: customer_register_step1
    def test_customer_register_step1_get(self):
        response = self.client.get(reverse('customer_register_step1'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/customer/step1.html')
        self.assertIsInstance(response.context['form'], Step1Form)
        self.assertEqual(response.context['message'], '')

    def test_customer_register_step1_post_invalid(self):
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'invalid_email'
        response = self.client.post(reverse('customer_register_step1'), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/customer/step1.html')
        self.assertFalse(response.context['form'].is_valid())

    # View Tests: customer_register_step2
    @patch('registration.views.District.objects.all')
    @patch('registration.views.Upazilla.objects.values')
    def test_customer_register_step2_get_no_session(self, mock_upazilla, mock_district):
        response = self.client.get(reverse('customer_register_step2'))
        self.assertRedirects(response, reverse('customer_register_step1'))

    @patch('registration.views.District.objects.all')
    @patch('registration.views.Upazilla.objects.values')
    def test_customer_register_step2_get(self, mock_upazilla, mock_district):
        mock_district.return_value.values.return_value = self.district_data
        mock_upazilla.return_value.annotate.return_value = self.upazilla_data
        session = self.client.session
        session['step1_data'] = self.user_data
        session.save()
        response = self.client.get(reverse('customer_register_step2'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/customer/step2.html')
        self.assertIsInstance(response.context['form'], Step3Form)
        self.assertEqual(response.context['district'], list(self.district_data))
        self.assertEqual(response.context['Upazilla'], list(self.upazilla_data))


    @patch('registration.views.District.objects.all')
    @patch('registration.views.Upazilla.objects.values')
    @patch('registration.views.MyUser.objects.create_user')
    def test_customer_register_step2_post_failure(self, mock_create_user, mock_upazilla, mock_district):
        mock_district.return_value.values.return_value = self.district_data
        mock_upazilla.return_value.annotate.return_value = self.upazilla_data
        mock_create_user.side_effect = Exception("Database error")
        request = self.factory.post(reverse('customer_register_step2'), {
            'district': 'Dhaka',
            'upazilla': 'Mirpur',
            'area': 'Test Area',
            'latitude': 23.8103,
            'longitude': 90.4125
        })
        request = self._add_middleware(request)
        request.session['step1_data'] = self.user_data
        response = customer_register_step2(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Failed")
        self.assertFalse(MyUser.objects.filter(email=self.user_data['email']).exists())

   
    # View Tests: business_register_step1
    def test_business_register_step1_get(self):
        response = self.client.get(reverse('business_register_step1'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step1.html')
        self.assertIsInstance(response.context['form'], Step1Form)

    def test_business_register_step1_post_valid(self):
        response = self.client.post(reverse('business_register_step1'), self.user_data)
        self.assertRedirects(response, reverse('business_register_step2'))
        self.assertEqual(self.client.session.get('step1_data'), self.user_data)

    # View Tests: business_register_step2
    def test_business_register_step2_get_no_session(self):
        response = self.client.get(reverse('business_register_step2'))
        self.assertRedirects(response, reverse('business_register_step1'))

    def test_business_register_step2_get(self):
        session = self.client.session
        session['step1_data'] = self.user_data
        session.save()
        response = self.client.get(reverse('business_register_step2'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step2.html')
        self.assertIsInstance(response.context['form'], Step2Form)

    def test_business_register_step2_post_valid(self):
        business_data = {
            'business_name': 'Test Shop',
            'business_title': 'Test Title',
            'business_info': 'This is a test business.',
            'gender': 'male'
        }
        request = self.factory.post(reverse('business_register_step2'), business_data)
        request = self._add_middleware(request)
        request.session['step1_data'] = self.user_data
        response = business_register_step2(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('business_register_step3'))

    # View Tests: business_register_step3
    @patch('registration.views.District.objects.all')
    @patch('registration.views.Upazilla.objects.values')
    def test_business_register_step3_get_no_session(self, mock_upazilla, mock_district):
        response = self.client.get(reverse('business_register_step3'))
        self.assertRedirects(response, reverse('business_register_step1'))
        session = self.client.session
        session['step1_data'] = self.user_data
        session.save()
        response = self.client.get(reverse('business_register_step3'))
        self.assertRedirects(response, reverse('business_register_step1'))

    @patch('registration.views.District.objects.all')
    @patch('registration.views.Upazilla.objects.values')
    def test_business_register_step3_get(self, mock_upazilla, mock_district):
        mock_district.return_value.values.return_value = self.district_data
        mock_upazilla.return_value.annotate.return_value = self.upazilla_data
        session = self.client.session
        session['step1_data'] = self.user_data
        session['step2_data'] = {
            'business_name': 'Test Shop',
            'business_title': 'Test Title',
            'business_info': 'This is a test business.',
            'gender': 'male',
            'website': ''
        }
        session.save()
        response = self.client.get(reverse('business_register_step3'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/login_signup/register/business/step3.html')
        self.assertIsInstance(response.context['form'], Step3Form)
        self.assertEqual(response.context['district'], list(self.district_data))
        self.assertEqual(response.context['Upazilla'], list(self.upazilla_data))


    # Form Tests: Step1Form
    def test_step1_form_valid(self):
        form = Step1Form(data=self.user_data)
        self.assertTrue(form.is_valid())

    def test_step1_form_invalid_email(self):
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'invalid_email'
        form = Step1Form(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_step1_form_duplicate_email(self):
        MyUser.objects.create_user(email=self.user_data['email'], password='testpass', user_type='user')
        form = Step1Form(data=self.user_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    # Form Tests: Step2Form
    def test_step2_form_valid(self):
        form = Step2Form(data={
            'business_name': 'Test Shop',
            'business_title': 'Test Title',
            'business_info': 'This is a test business.',
            'gender': 'male'
        })
        self.assertTrue(form.is_valid())

    def test_step2_form_invalid_business_info(self):
        form = Step2Form(data={
            'business_name': 'Test Shop',
            'business_title': 'Test Title',
            'business_info': 'Short',
            'gender': 'male'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('business_info', form.errors)

    # Form Tests: Step3Form
    def test_step3_form_valid_customer(self):
        form = Step3Form(
            data={
                'district': 'Dhaka',
                'upazilla': 'Mirpur',
                'area': 'Test Area',
                'latitude': 23.8103,
                'longitude': 90.4125
            },
            user_type='customer',
            districts=self.district_data,
            upazillas=['Mirpur', 'Gulshan']
        )
        self.assertTrue(form.is_valid())

    def test_step3_form_valid_shop(self):
        form = Step3Form(
            data={
                'district': 'Dhaka',
                'upazilla': 'Mirpur',
                'area': 'Test Area',
                'shop_landmark_1': 'Landmark 1',
                'shop_landmark_2': 'Landmark 2',
                'shop_landmark_3': 'Landmark 3',
                'latitude': 23.8103,
                'longitude': 90.4125
            },
            user_type='shop',
            districts=self.district_data,
            upazillas=['Mirpur', 'Gulshan']
        )
        self.assertTrue(form.is_valid())

from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages import get_messages
from registration.views import (
    select_user_type, customer_register_step1, customer_register_step2,
    customer_submit, business_register_step1, business_register_step2,
    business_register_step3
)
from registration.forms import Step1Form, Step2Form, Step3Form
from shop_profile.models import MyUser, ShopProfile, ShopSchedule
from user_profile.models import UserProfile
from my_app.models import District, Upazilla, Area, Division  # Added Division import
from unittest.mock import patch
from datetime import time
import uuid

class RegistrationAppCoverageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password123',
            'country_code': '+880',
            'mobile_number': '1234567890',
            'terms': True,
            'gender': 'Male'
        }
        self.district_data = [
            {'id': 1, 'name': 'Dhaka'},
            {'id': 2, 'name': 'Chittagong'}
        ]
        self.upazilla_data = [
            {'district__name': 'Dhaka', 'upazilla_names': ['Mirpur', 'Gulshan']},
            {'district__name': 'Chittagong', 'upazilla_names': ['Hathazari']}
        ]

    # Helper method to add session and messages middleware to requests
    def _add_middleware(self, request):
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        messages_middleware = MessageMiddleware(lambda x: None)
        messages_middleware.process_request(request)
        return request

    # URL Tests
    def test_url_select_user_type(self):
        url = reverse('select_user_type')
        self.assertEqual(url, '/register/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, select_user_type)

    def test_url_customer_register_step1(self):
        url = reverse('customer_register_step1')
        self.assertEqual(url, '/register/customer/step1')
        resolver = resolve(url)
        self.assertEqual(resolver.func, customer_register_step1)

    def test_url_customer_register_step2(self):
        url = reverse('customer_register_step2')
        self.assertEqual(url, '/register/customer/step2')
        resolver = resolve(url)
        self.assertEqual(resolver.func, customer_register_step2)

    def test_url_customer_submit(self):
        url = reverse('customer_submit')
        self.assertEqual(url, '/register/customer/submit')
        resolver = resolve(url)
        self.assertEqual(resolver.func, customer_submit)

    def test_url_business_register_step1(self):
        url = reverse('business_register_step1')
        self.assertEqual(url, '/register/business/step1')
        resolver = resolve(url)
        self.assertEqual(resolver.func, business_register_step1)

    def test_url_business_register_step2(self):
        url = reverse('business_register_step2')
        self.assertEqual(url, '/register/business/step2')
        resolver = resolve(url)
        self.assertEqual(resolver.func, business_register_step2)

    def test_url_business_register_step3(self):
        url = reverse('business_register_step3')
        self.assertEqual(url, '/register/business/step3')
        resolver = resolve(url)
        self.assertEqual(resolver.func, business_register_step3)

    # View Tests: customer_register_step1
    def test_customer_register_step1_post_valid(self):
        response = self.client.post(reverse('customer_register_step1'), self.user_data)
        self.assertRedirects(response, reverse('customer_register_step2'))
        self.assertEqual(self.client.session.get('step1_data'), self.user_data)

    # View Tests: customer_register_step2
    @patch('registration.views.District.objects.all')
    @patch('registration.views.Upazilla.objects.values')
    @patch('registration.views.Upazilla.objects.get')
    def test_customer_register_step2_post_valid(self, mock_upazilla_get, mock_upazilla, mock_district):
        mock_district.return_value.values.return_value = self.district_data
        mock_upazilla.return_value.annotate.return_value = self.upazilla_data
        # Create a Division and District with required division_id
        division = Division.objects.create(name='Dhaka Division')
        district = District.objects.create(name='Dhaka', division=division)
        upazilla = Upazilla.objects.create(name='Mirpur', district=district)
        mock_upazilla_get.return_value = upazilla
        request = self.factory.post(reverse('customer_register_step2'), {
            'district': 'Dhaka',
            'upazilla': 'Mirpur',
            'area': 'Test Area',
            'latitude': 23.8103,
            'longitude': 90.4125
        })
        request = self._add_middleware(request)
        request.session['step1_data'] = self.user_data
        response = customer_register_step2(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        self.assertTrue(MyUser.objects.filter(email=self.user_data['email']).exists())
        self.assertTrue(UserProfile.objects.filter(user__email=self.user_data['email']).exists())
        self.assertTrue(Area.objects.filter(name='Test Area', upazilla=upazilla).exists())
        messages = list(get_messages(request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You have successfully created account.")
        self.assertEqual(dict(request.session), {})

    # View Tests: business_register_step3
    @patch('registration.views.District.objects.all')
    @patch('registration.views.Upazilla.objects.values')
    @patch('registration.views.Upazilla.objects.get')
    @patch('registration.views.time')
    def test_business_register_step3_post_valid(self, mock_time, mock_upazilla_get, mock_upazilla, mock_district):
        mock_district.return_value.values.return_value = self.district_data
        mock_upazilla.return_value.annotate.return_value = self.upazilla_data
        # Create a Division and District with required division_id
        division = Division.objects.create(name='Dhaka Division')
        district = District.objects.create(name='Dhaka', division=division)
        upazilla = Upazilla.objects.create(name='Mirpur', district=district)
        mock_upazilla_get.return_value = upazilla
        mock_time.side_effect = lambda hour, minute: time(hour=hour, minute=minute)
        business_data = {
            'district': 'Dhaka',
            'upazilla': 'Mirpur',
            'area': 'Test Area',
            'shop_landmark_1': 'Landmark 1',
            'shop_landmark_2': 'Landmark 2',
            'shop_landmark_3': 'Landmark 3',
            'latitude': 23.8103,
            'longitude': 90.4125
        }
        request = self.factory.post(reverse('business_register_step3'), business_data)
        request = self._add_middleware(request)
        request.session['step1_data'] = self.user_data
        request.session['step2_data'] = {
            'business_name': 'Test Shop',
            'business_title': 'Test Title',
            'business_info': 'This is a test business.',
            'gender': 'male',
            'website': ''
        }
        response = business_register_step3(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        self.assertTrue(MyUser.objects.filter(email=self.user_data['email']).exists())
        shop_profile = ShopProfile.objects.get(user__email=self.user_data['email'])
        self.assertTrue(shop_profile)
        self.assertTrue(Area.objects.filter(name='Test Area', upazilla=upazilla).exists())
        schedules = ShopSchedule.objects.filter(shop=shop_profile)
        self.assertEqual(schedules.count(), 7)
        for schedule in schedules:
            if schedule.day_of_week == 'Friday':
                self.assertEqual(schedule.end, time(hour=17, minute=0))
            else:
                self.assertEqual(schedule.end, time(hour=20, minute=0))
            self.assertEqual(schedule.start, time(hour=9, minute=0))
        messages = list(get_messages(request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You have successfully created account.")
        self.assertEqual(dict(request.session), {})
        self.assertNotIn('step1_data', request.session)
        self.assertNotIn('step2_data', request.session)
