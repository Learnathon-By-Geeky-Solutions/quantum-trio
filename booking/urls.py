from django.urls import path
from . import views

urlpatterns = [
    path('', views.booking_step_1, name='index'),
]
 