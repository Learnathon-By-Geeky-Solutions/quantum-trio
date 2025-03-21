from django.db import models
from my_app.models import Item
from user_profile.models import UserProfile
from shop_profile.models import ShopProfile, ShopWorker
from django.utils import timezone
class BookingSlot(models.Model):
    user = models.ForeignKey(UserProfile, related_name="bookingslot", on_delete=models.CASCADE)
    shop = models.ForeignKey(ShopProfile, related_name="bookingslot", on_delete=models.CASCADE) 
    worker = models.ForeignKey(ShopWorker, related_name="bookingslot", on_delete=models.CASCADE) 
    item = models.ForeignKey(Item, related_name="bookingslot", on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    PAYMENT_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    ]
    payment_status = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='unpaid')
    """When the booking is"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    """If needed any notes"""
    notes = models.TextField(blank=True) 

    def __str__(self):
        return f"Booking by {self.user} at {self.shop} on {self.date} {self.time}"
