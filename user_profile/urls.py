from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile,name='user'),
    path('address', views.address,name='address'),
    path('addressofbooking', views.addressofbooking,name='addressofbooking'),
    path('myreviews', views.myreviews,name='myreviews'),
    path('mybooking', views.mybooking,name='mybooking'),
    path('mycancellations', views.mycancellations,name='mycancellations'),
    path('mynotifications', views.mynotifications,name='mynotifications'),
    path('mymessage', views.mymessage,name='mymessage'),
]