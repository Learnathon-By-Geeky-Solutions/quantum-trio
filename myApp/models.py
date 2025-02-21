from django.db import models
from django.contrib.auth.models import User

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
    name=models.CharField(max_length=100)
    item_description=models.CharField(max_length=800, null=True, blank=True)
    service=models.ForeignKey(Service, on_delete=models.CASCADE, related_name="items")
    def __str__(self):
        return f"{self.name},   {self.service.name}"