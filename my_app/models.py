from django.db import models
from django.contrib.auth.models import User

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# # Models for location purpose so that we can work on original locations
class Division(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class District(models.Model):
    name = models.CharField(max_length=100, unique=True)
    division=models.ForeignKey(Division, on_delete=models.CASCADE, related_name="districts")
    def __str__(self):
        return self.name

class Upazilla(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="upazillas")

    def __str__(self):
        return f"{self.name}, {self.district.name}"

class Area(models.Model):
    name = models.CharField(max_length=100)
    upazilla = models.ForeignKey(Upazilla, on_delete=models.CASCADE, related_name="areas")

    def __str__(self):
        return f"{self.name}, {self.upazilla.name}"
 
class Landmark(models.Model):
    name = models.CharField(max_length=255)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="landmarks")

    def __str__(self):
        return f"{self.name}, {self.area.name}"
    
class Service(models.Model):
    name=models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"
    
class Item(models.Model):
    GENDER_CHOICES=[
        ('Male','Male'),
        ('Female','Female'),
        ('Both','Both'),
    ]
    name=models.CharField(max_length=100)
    item_description=models.CharField(max_length=800, blank=True, default="No description available")
    service=models.ForeignKey(Service, on_delete=models.CASCADE, related_name="items")
    gender=models.CharField(max_length=10,choices=GENDER_CHOICES,default='Both')
    def __str__(self):
        return f"{self.name},   {self.service.name}"

class ReviewCarehub(models.Model):
    reviewer_type = models.ForeignKey(ContentType, on_delete=models.CASCADE) 
    reviewer_id = models.PositiveIntegerField()  
    reviewer = GenericForeignKey("reviewer_type", "reviewer_id") 
    comment = models.CharField(max_length=255) 
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    created_at = models.DateTimeField(auto_now_add=True) 
    def __str__(self):
        return f"Review by {self.user} - {self.rating}/5"

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"