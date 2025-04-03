from django.contrib import admin
from django.urls import path,include
from django import views
from shop_profile import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [ 
    path('', views.profile,name='shop_profile'),
    path('gallery', views.gallery,name='shop_gallery'),
    path('calender', views.calender,name='shop_calender'),
    path('appointments', views.appointments,name='appointments'),
    path("accept-booking/", views.accept_booking, name="accept_booking"),
    path("reject-booking/", views.reject_booking, name="reject_booking"),
    path("booking-details/", views.booking_details, name="booking_details"),
    path('slots', views.slots,name='shop_booking_slots'),
    path('message', views.message,name='shop_message'),
    path('staffs', views.staffs,name='shop_staffs'),
    path('customers', views.customers,name='shop_customers'),
    path('review', views.review,name='shop_review'),
    path('notifications', views.notification,name='shop_notifications'),
    path('settings', views.setting,name='shop_setting'),
    path('add_worker', views.add_worker,name='add_worker'),
    path('basic_update', views.basic_update,name='basic_update'),
    path('schedule_update', views.schedule_update,name='schedule_update'),
]
# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)