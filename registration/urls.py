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
    # path('business/step4',views.business_register_step4 ,name='business_register_step4'),
    # path('business/step5',views.business_register_step5 ,name='business_register_step5'),
    # path('business/step6',views.business_register_step6, name='business_register_step6'),
    # path('business/step7',views.business_register_step7, name='business_register_step7'),
    # path('business/step8',views.business_register_step8, name='business_register_step8'),
    # path('business/submit',views.business_submit, name='business_submit'),
    
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
