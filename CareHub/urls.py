
from django.contrib import admin
from django.urls import path
from django import views
from myApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
]
