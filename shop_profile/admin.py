from django.contrib import admin
from .models import *

admin.site.register(MyUser)# Register your models here.
admin.site.register(ShopProfile)
admin.site.register(ShopGallery)
admin.site.register(ShopWorker)
admin.site.register(ShopService)
admin.site.register(ShopReview)
admin.site.register(ShopSchedule)

