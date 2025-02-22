from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Shop Profile Fields
    shop_name = models.CharField(max_length=255)
    shop_title = models.CharField(max_length=255, blank=True, null=True)
    shop_info = models.TextField(blank=True, null=True)
    shop_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    shop_picture = models.ImageField(upload_to='shop_pictures/', blank=True, null=True)
    shop_email = models.EmailField(blank=True, null=True)
    shop_owner = models.CharField(max_length=255, blank=True, null=True)
    shop_customer_count = models.IntegerField(default=0)
    status = models.BooleanField(default=True)  # Is the shop active?

    # Contact Information
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    shop_landmark_1 = models.CharField(max_length=255, blank=True, null=True)
    shop_landmark_2 = models.CharField(max_length=255, blank=True, null=True)
    shop_landmark_3 = models.CharField(max_length=255, blank=True, null=True)
    shop_landmark_4 = models.CharField(max_length=255, blank=True, null=True)
    shop_landmark_5 = models.CharField(max_length=255, blank=True, null=True)

    # Location Fields (For geolocation)
    shop_state = models.CharField(max_length=100, blank=True, null=True)
    shop_city = models.CharField(max_length=100, blank=True, null=True)
    shop_area = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    # Additional Info
    member_since = models.DateField(auto_now_add=True)
    
    # Address Details
    shop_address = models.CharField(max_length=255, blank=True, null=True)

    # Shop Type/Category
    shop_category = models.CharField(max_length=255, blank=True, null=True)

    # Shop Services (can be extended with a Foreign Key to a Service model)
    shop_services = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.shop_name
