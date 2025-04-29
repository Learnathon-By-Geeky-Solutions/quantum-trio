from django import forms
from django.core.validators import MinLengthValidator, RegexValidator
from shop_profile.models import MyUser
att_1='border border-gray-300 px-4 py-3 rounded-lg w-full focus:outline-none focus:border-pink-600'
att_2='border border-gray-300 p-3 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-pink-500'
att_3='border border-gray-300 p-3 rounded-lg w-full focus:outline-none focus:border-pink-600'

class Step1Form(forms.Form):
    first_name = forms.CharField(
        max_length=255,
        required=True,
        label="First Name",
        widget=forms.TextInput(attrs={
            'class': att_1,
            'id': 'first-name'
        })
    )
    last_name = forms.CharField(
        max_length=255,
        required=True,
        label="Last Name",
        widget=forms.TextInput(attrs={
            'class': att_1,
            'id': 'last-name'
        })
    )
    email = forms.EmailField(
        max_length=255,
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': att_1,
            'id': 'email'
        })
    )
    password = forms.CharField(
        max_length=128,
        required=True,
        label="Password",
        validators=[MinLengthValidator(6)],
        widget=forms.PasswordInput(attrs={
            'class': att_1,
            'id': 'password',
            'minlength': '6'
        })
    )
    country_code = forms.ChoiceField(
        choices=[('+880', '+880')],
        required=True,
        label="Country Code",
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 px-4 py-3 rounded-l-lg focus:outline-none focus:border-pink-600',
            'id': 'country-code'
        })
    )
    mobile_number = forms.CharField(
        max_length=15,
        required=True,
        label="Mobile Number",
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit mobile number.')],
        widget=forms.TextInput(attrs={
            'class': 'border border-gray-300 px-4 py-3 rounded-r-lg w-full focus:outline-none focus:border-pink-600',
            'id': 'mobile-number',
            'type': 'tel'
        })
    )
    terms = forms.BooleanField(
        required=True,
        label="I agree to the Privacy Policy and Terms of Business",
        widget=forms.CheckboxInput(attrs={
            'class': 'text-pink-600 focus:ring-pink-500 h-5 w-5',
            'id': 'terms'
        })
    )
    gender = forms.ChoiceField(
        choices=[('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female')],
        required=False,  # Default to not required
        label="Gender",
        widget=forms.Select(attrs={
            'class': att_2,
            'id': 'gender'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if MyUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

class Step2Form(forms.Form):
    business_name = forms.CharField(
        max_length=255,
        required=True,
        label="Business Name",
        widget=forms.TextInput(attrs={
            'class': att_1,
            'id': 'business-name'
        })
    )
    business_title = forms.CharField(
        max_length=255,
        required=True,
        label="Business Title",
        widget=forms.TextInput(attrs={
            'class': att_1,
            'id': 'business-title'
        })
    )
    website = forms.URLField(
        max_length=200,
        required=False,
        label="Website",
        widget=forms.URLInput(attrs={
            'class': att_1,
            'id': 'website'
        })
    )
    business_info = forms.CharField(
        max_length=255,
        required=True,
        label="Business Info",
        validators=[MinLengthValidator(10, "Business info must be at least 10 characters.")],
        widget=forms.Textarea(attrs={
            'class': att_1,
            'id': 'info',
            'rows': '5'
        })
    )
    gender = forms.ChoiceField(
        choices=[('male', 'Male'), ('female', 'Female'), ('both', 'Both')],
        required=True,
        label="For",
        widget=forms.Select(attrs={
            'class': att_1,
            'id': 'gender'
        })
    )

    def clean_gender(self):
        gender = self.cleaned_data.get('gender')
        gender_map = {'male': 'Male', 'female': 'Female', 'both': 'Other'}
        return gender_map.get(gender, 'Other')

class Step3Form(forms.Form):
    district = forms.ChoiceField(
        choices=[],
        required=True,
        label="District",
        widget=forms.Select(attrs={
            'class': att_3,
            'id': 'district'
        })
    )
    upazilla = forms.ChoiceField(
        choices=[],
        required=True,
        label="Upazilla",
        widget=forms.Select(attrs={
            'class': att_3,
            'id': 'upazilla'
        })
    )
    area = forms.CharField(
        max_length=100,
        required=True,
        label="Shop Area",
        widget=forms.TextInput(attrs={
            'class': att_3,
            'id': 'area'
        })
    )
    shop_landmark_1 = forms.CharField(
        max_length=255,
        required=True,
        label="Landmark 1",
        widget=forms.TextInput(attrs={
            'class': att_2,
            'id': 'shop-landmark-1',
            'placeholder': 'Enter first landmark (Mandatory)'
        })
    )
    shop_landmark_2 = forms.CharField(
        max_length=255,
        required=True,
        label="Landmark 2",
        widget=forms.TextInput(attrs={
            'class': att_2,
            'id': 'shop-landmark-2',
            'placeholder': 'Enter second landmark (Mandatory)'
        })
    )
    shop_landmark_3 = forms.CharField(
        max_length=255,
        required=True,
        label="Landmark 3",
        widget=forms.TextInput(attrs={
            'class': att_2,
            'id': 'shop-landmark-3',
            'placeholder': 'Enter third landmark (Mandatory)'
        })
    )
    shop_landmark_4 = forms.CharField(
        max_length=255,
        required=False,
        label="Landmark 4",
        widget=forms.TextInput(attrs={
            'class': att_2,
            'id': 'shop-landmark-4',
            'placeholder': 'Enter fourth landmark (optional)'
        })
    )
    shop_landmark_5 = forms.CharField(
        max_length=255,
        required=False,
        label="Landmark 5",
        widget=forms.TextInput(attrs={
            'class': att_2,
            'id': 'shop-landmark-5',
            'placeholder': 'Enter fifth landmark (optional)'
        })
    )
    latitude = forms.FloatField(
        required=True,
        label="Latitude",
        widget=forms.TextInput(attrs={
            'class': att_3,
            'id': 'latitude'
        })
    )
    longitude = forms.FloatField(
        required=True,
        label="Longitude",
        widget=forms.TextInput(attrs={
            'class': att_3,
            'id': 'longitude'
        })
    )

    def __init__(self, *args, **kwargs):
        user_type = kwargs.pop('user_type', 'shop')
        districts = kwargs.pop('districts', [])
        upazillas = kwargs.pop('upazillas', [])
        super().__init__(*args, **kwargs)
        if user_type=='customer':
            self.fields['shop_landmark_1'].required = False
            self.fields['shop_landmark_2'].required = False
            self.fields['shop_landmark_3'].required = False
        
        self.fields['district'].choices = [(d['name'], d['name']) for d in districts]
        self.fields['upazilla'].choices = [(u, u) for u in upazillas]