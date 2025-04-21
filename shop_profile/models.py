from django.db import models
from my_app.models import Item
from decimal import Decimal
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, user_type="user"):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            email=self.normalize_email(email),
            user_type=user_type,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email=email,
            password=password,
            user_type="admin",
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class MyUser(AbstractBaseUser):
    USER_TYPE_CHOICES = [
        ("user", "User"),
        ("shop", "Shop Owner"),
        ("admin", "Admin"),
    ]

    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default="user")
 
    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"

    @property
    def is_staff(self):
        return self.is_admin

class ShopProfile(models.Model): 
    # Shop Profile Fields
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'), 
    ]
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name="shop_profile")
    shop_name = models.CharField(max_length=255)
    shop_title = models.CharField(max_length=255, blank=True,default='')
    shop_info = models.TextField(max_length=255,blank=True,default='')
    shop_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    shop_owner = models.CharField(max_length=255, blank=True,default='')
    shop_picture=models.ImageField(upload_to='ShopGallery/', blank=True, null=True)
    shop_customer_count = models.IntegerField(default=0)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True,default="Other")
    status = models.BooleanField(default=True)  # Is the shop active?
    mobile_number = models.CharField(max_length=15, blank=True,default='')
    shop_website = models.URLField(blank=True, max_length=200,default='')
    shop_state = models.CharField(max_length=100, blank=True,default='')
    shop_city = models.CharField(max_length=100, blank=True,default='')
    shop_area = models.CharField(max_length=100, blank=True,default='')
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    shop_landmark_1 = models.CharField(max_length=255, blank=True,default='')
    shop_landmark_2 = models.CharField(max_length=255, blank=True,default='')
    shop_landmark_3 = models.CharField(max_length=255, blank=True,default='')
    shop_landmark_4 = models.CharField(max_length=255, blank=True,default='')
    shop_landmark_5 = models.CharField(max_length=255, blank=True,default='')
    
    # Additional Info
    member_since = models.DateField(auto_now_add=True)

    def update_rating(self, rating):
        current_rating = self.shop_rating  # Already a Decimal
        current_total = current_rating * self.shop_customer_count

        self.shop_customer_count += 1
        new_rating = (current_total + Decimal(str(rating))) / self.shop_customer_count  # Convert float to Decimal

        if Decimal("0.00") <= new_rating <= Decimal("5.00"):
            self.shop_rating = new_rating.quantize(Decimal("0.01"))  # Round to 2 decimal places
            self.save()
            return True
        return False
    
    def __str__(self): 
        return self.shop_name
    
class ShopGallery(models.Model):
    shop = models.ForeignKey(ShopProfile, related_name="shopgallery", on_delete=models.CASCADE)  # Link to Shop
    image = models.ImageField(upload_to='ShopGallery/', blank=True, null=True)  # Image field
    description = models.CharField(max_length=255, blank=True, default="No description available")  # Optional description for the image
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Time when image is uploaded
    def __str__(self):
        return f"Image for {self.shop.name} - {self.id}"

class ShopWorker(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField() 
    phone = models.CharField(max_length=15)
    profile_pic = models.ImageField(upload_to='ShopWorker/', blank=True, default='default-profile.jpg')
    experience = models.FloatField(help_text="Experience in years")
    expertise = models.ManyToManyField(Item, related_name="experts",blank=True)
    shop = models.ForeignKey(ShopProfile, related_name="shopworker", on_delete=models.CASCADE)
    rating=models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    def update_rating(self, new_rating):
        """Update the average rating when a new rating is submitted."""
        self.total_reviews += 1
        current_total = self.rating * (self.total_reviews - 1)
        new_avg = (current_total + Decimal(str(new_rating))) / self.total_reviews
        self.rating = round(new_avg, 2)
        self.save()
    def __str__(self):
        return f"{self.name} ({self.experience} years experience)"
     
class ShopService(models.Model): 
    shop = models.ForeignKey(ShopProfile, related_name="shopservice", on_delete=models.CASCADE)  # Shop providing the service
    item = models.ForeignKey(Item, related_name="shopservices", on_delete=models.CASCADE)  # Service provided by the shop
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Price of the service at this shop (could be different per shop)
    
    def __str__(self):
        return f"{self.shop.shop_name} - {self.item.name}"

class ShopReview(models.Model):
    shop = models.ForeignKey(ShopProfile, related_name="shopreview", on_delete=models.CASCADE)  # The shop being reviewed
    reviewer_id = models.IntegerField(null=True, blank=True)  # The shop reviewed by whom only id
    rating = models.PositiveIntegerField(default=1)  # Rating between 1 and 5
    review = models.TextField(blank=True,default='')  # Optional text review
    created_at = models.DateTimeField(auto_now_add=True)  # The date and time when the review was created
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.shop.update_rating(self.rating)
        print('Updated rating')
    def __str__(self):
        return f"Review by {self.reviewer_id} for {self.shop.shop_name} - Rating: {self.rating}"

class ShopSchedule(models.Model):
    DAYS_OF_WEEK = [
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]
    shop = models.ForeignKey(ShopProfile, related_name="shopschedule", on_delete=models.CASCADE)  # The shop being reviewed
    day_of_week=models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start=models.TimeField()
    end=models.TimeField()
    def __str__(self):
        return f"{self.shop.shop_name} for {self.day_of_week}"
    
class ShopNotification(models.Model):
    shop = models.ForeignKey(ShopProfile, related_name="notifications", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    NOTIFICATION_TYPES = [
        ('booking', 'Booking'),
        ('payment', 'Payment'),
        ('message', 'Message'),
        ('general', 'General'), 
        ('cancel', 'cancel'), 
    ]
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='general')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.shop.shop_name} ({'Read' if self.is_read else 'Unread'})"