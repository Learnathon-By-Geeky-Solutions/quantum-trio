from django.contrib import admin
from django.urls import path, include
from registration import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.select_user_type, name='select_user_type'),
    # user registration steps
    path('customer/step1',views.customer_register_step1,name='customer_register_step1'),
    path('customer/step2',views.customer_register_step2,name='customer_register_step2'),
    path('customer/submit',views.customer_submit , name='customer_submit'),
    # business registration steps
    path('business/step1', views.business_register_step1, name='business_register_step1'),
    path('business/step2', views.business_register_step2, name='business_register_step2'),
    path('business/step3', views.business_register_step3, name='business_register_step3'),
   
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
