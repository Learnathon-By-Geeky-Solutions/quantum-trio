from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile,name='user'),
    path('address', views.address,name='address'),
    path('addressofbooking', views.addressofbooking,name='addressofbooking'),
    path('myreviews', views.myreviews,name='myreviews'),
    path('mybooking', views.mybooking,name='mybooking'), 
    path("update-status/", views.update_status, name="update-status"),
    path("reject-booking/", views.reject_booking, name="reject_booking"),
    path("booking-details/", views.booking_details, name="booking_details"),
    path('mycancellations', views.mycancellations,name='mycancellations'),
    path('mynotifications', views.mynotifications,name='mynotifications'),
    path('mymessage', views.mymessage,name='mymessage'),
]