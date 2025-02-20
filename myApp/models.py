from django.db import models
from django.contrib.auth.models import User

# class person(models.Model):
#     name=models.CharField(max_length=100)
#     age=models.PositiveIntegerField()
    
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
    
class Services(models.Model):
    name=models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"
    
class Items(models.Model):
    name=models.CharField(max_length=50)
    item_description=models.CharField(max_length=500, null=True, blank=True)
    service=models.ForeignKey(Services, on_delete=models.CASCADE, related_name="items")
    def __str__(self):
        return f"{self.name},{self.service.name}"