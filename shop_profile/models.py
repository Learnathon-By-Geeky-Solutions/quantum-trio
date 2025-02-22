# from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from myApp.models import *
from user_profile.models import *
class shop_profile(models.Model):
    # Shop Profile Fields
    shop_name = models.CharField(max_length=255)
    shop_title = models.CharField(max_length=255, blank=True, null=True)
    shop_info = models.TextField(blank=True, null=True)
    shop_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    shop_owner = models.CharField(max_length=255, blank=True, null=True)
    shop_customer_count = models.IntegerField(default=0)
    status = models.BooleanField(default=True)  # Is the shop active?

    # Contact Information
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    shop_email = models.EmailField(blank=True, null=True)

    # Location Fields (For geolocation)
    shop_state = models.CharField(max_length=100, blank=True, null=True)
    shop_city = models.CharField(max_length=100, blank=True, null=True)
    shop_area = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    shop_landmark_1 = models.CharField(max_length=255, blank=True, null=True)
    shop_landmark_2 = models.CharField(max_length=255, blank=True, null=True)
    shop_landmark_3 = models.CharField(max_length=255, blank=True, null=True)
    shop_landmark_4 = models.CharField(max_length=255, blank=True, null=True)
    shop_landmark_5 = models.CharField(max_length=255, blank=True, null=True)
    
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
    
class shop_gallery(models.Model):
    shop = models.ForeignKey(shop_profile, related_name="gallery", on_delete=models.CASCADE)  # Link to Shop
    image = models.ImageField(upload_to='shop_gallery/', blank=True, null=True)  # Image field
    description = models.CharField(max_length=255, blank=True, null=True)  # Optional description for the image
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Time when image is uploaded

    def __str__(self):
        return f"Image for {self.shop.name} - {self.id}"

class Shop_worker(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)  # Ensures unique phone numbers
    profile_pic = models.ImageField(upload_to='worker_profiles/', blank=True, null=True)
    experience = models.PositiveIntegerField(help_text="Experience in years")  # Only positive numbers
    expertise = models.ManyToManyField(Item, related_name="experts")

    def __str__(self):
        return f"{self.name} ({self.experience} years experience)"
    
class shop_service(models.Model):
    shop = models.ForeignKey(shop_profile, related_name="services", on_delete=models.CASCADE)  # Shop providing the service
    service = models.ForeignKey(Service, related_name="shops", on_delete=models.CASCADE)  # Service provided by the shop
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Price of the service at this shop (could be different per shop)
    availability = models.BooleanField(default=True)  # Is this service available at the shop?

    def __str__(self):
        return f"{self.shop.name} - {self.service.name}"

class Shop_review(models.Model):
    shop = models.ForeignKey(shop_profile, related_name="reviews", on_delete=models.CASCADE)  # The shop being reviewed
    user = models.ForeignKey(user_profile, related_name="shop_reviews", on_delete=models.CASCADE)  # The user who gave the review
    rating = models.PositiveIntegerField(default=1)  # Rating between 1 and 5
    review = models.TextField(blank=True, null=True)  # Optional text review
    created_at = models.DateTimeField(auto_now_add=True)  # The date and time when the review was created

    class Meta:
        unique_together = ('shop', 'user')  # Ensures a user can only review a shop once

    def __str__(self):
        return f"Review by {self.user.username} for {self.shop.name} - Rating: {self.rating}"

