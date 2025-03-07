from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.booking_step_1, name='index'),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 