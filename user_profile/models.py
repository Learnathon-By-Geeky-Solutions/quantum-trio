from django.db import models 
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password, check_password
from shop_profile.models import MyUser
class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'), 
        ('Other', 'Other'),
    ]
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name="user_profile")
    first_name = models.CharField(max_length=150)
    last_name  = models.CharField(max_length=150)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True,default='')
    phone_number = models.CharField(max_length=15, blank=True,default='')
    user_state = models.CharField(max_length=100, blank=True,default='')
    user_city = models.CharField(max_length=100, blank=True,default='')
    user_area = models.CharField(max_length=100, blank=True,default='')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # If this user can access admin functionalities
    is_superuser = models.BooleanField(default=False)  # If this user has super admin rights

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

    def set_password(self, raw_password):
        """Hashes the password and stores it."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verifies the password with the stored hash."""
        return check_password(raw_password, self.password)

    def generate_random_password(self, length=12):
        """Generates a random password (useful for password resets)."""
        return get_random_string(length)