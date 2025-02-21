from django.contrib import admin
from django.urls import path, include
from Registration import views
urlpatterns = [
    path('', views.select_user_type),
    # user registration steps
    path('customer/step1',views.customer_register_step1),
    path('customer/step2',views.customer_register_step2,name='step2'),
    # business registration steps
    path('business/step1',views.business_register_step1),
    path('business/step2',views.business_register_step2),
    path('business/step3',views.business_register_step3),
    path('business/step4',views.business_register_step4),
    path('business/step5',views.business_register_step5),
    path('business/step6',views.business_register_step6),
    path('business/step7',views.business_register_step7),
    path('business/step8',views.business_register_step8),
]
