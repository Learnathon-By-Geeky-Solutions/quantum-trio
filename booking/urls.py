from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.booking_step_1, name='index'),
    path('booking-step-2', views.booking_step_2, name='step-2'), 
    path('available_slots/', views.available_slots, name='available_slots'),
    path('success', views.success, name='success'),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 