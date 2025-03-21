from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile,name='user'),
    path('address', views.address,name='address'),
    path('reviews', views.reviews,name='reviews'),
    
]