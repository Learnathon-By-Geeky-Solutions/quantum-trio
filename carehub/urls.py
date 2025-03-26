from django.contrib import admin
from django.urls import path,include
from django import views
from carehub import settings
from my_app import views
from django.conf.urls.static import static

urlpatterns = [ 
    path('admin/', admin.site.urls,name='admin'),
    path('', views.home,name='home'),
    path('home', views.home,name='home'),
    path('submit_review',views.submit_review,name='submit_review'),
    path('register/', include('registration.urls'), name='register'),

    # redirect to Shop profile
    path('dashboard/',include('shop_profile.urls'),name='shop_dashboard'),

    # redirect to customer profile
    path('myprofile/',include('user_profile.urls'),name='user_profile'),
    
     # redirect to booking
    path('book/',include('booking.urls'),name='book'),

    path('select_user', views.select_user_type,name='select_user'),
    path('login', views.log_in,name='login'),
    path('logout',views.log_out,name='logout'),
    
    path('contact', views.contact_us,name='contact'),
    path('search', views.search,name='search'),
    path('booknow', views.book_now,name='booknow'),
    path('fetch-shop/', views.fetch_shop,name='booknow'),
    path('location', views.location,name='location'),
    path('service', views.service,name='service'),
    path('explore_by_items', views.explore_by_item,name='explore_by_item'),
    path('salon-profile', views.shop_profile,name='salon-profile'),
    path('salon_dashboard', views.view_dash_board),
    path('salon_gallery', views.view_salon_gallery),
    path('saloon_calender', views.view_saloon_calender),
    path('staffs', views.view_saloon_stuff),
    path('settings', views.view_settings),
    path('notifications', views.view_notification),
    path('salon_reviews', views.view_reviews),
    path('customers', views.view_customers),
    path('booking-slots', views.booking_slots),
    path('message', views.view_message),
    path('message-reply', views.view_message_reply),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
