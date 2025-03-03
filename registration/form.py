from django import forms
from .models import user_profile
from django import forms
from .models import user_profile, shop_profile

class user_profile_form(forms.ModelForm):
    class Meta:
        model = user_profile
        fields = ['username', 'email', 'phone_number', 'password', 'address', 'date_of_birth', 'profile_picture']
    
    # check if username already exist
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if user_profile.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists!")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if user_profile.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists!")
        return email

class shop_profile_form(forms.ModelForm):
    class Meta:
        model = shop_profile
        fields = ['shop_name', 'shop_title', 'shop_info', 'shop_rating', 'shop_owner', 'shop_customer_count', 'status',
                  'mobile_number', 'shop_email', 'shop_state', 'shop_city', 'shop_area', 'latitude', 'longitude',
                  'shop_landmark_1', 'shop_landmark_2', 'shop_landmark_3', 'shop_landmark_4', 'shop_landmark_5',
                  'member_since']
    
    # check if shop already exist
    # def clean_shop_name(self):
    #     shop_name = self.cleaned_data.get('shop_name')
    #     if shop_profile.objects.filter(shop_name=shop_name).exists():
    #         raise forms.ValidationError("Shop name already exists!")
    #     return shop_name
    # check if email already exist
    
    def clean_shop_email(self):
        shop_email = self.cleaned_data.get('shop_email')
        if shop_profile.objects.filter(shop_email=shop_email).exists():
            raise forms.ValidationError("Shop email already exists!")
        return shop_email
