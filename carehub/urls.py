from django.contrib import admin
from django.urls import path,include
from django import views
from carehub import settings
from my_app import views
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
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
    
    #For resetting password
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', views.success_reset_password, name='password_reset_complete'),
    
    path('contact', views.contact_us,name='contact'),
    path('about', views.about_us,name='about'),

    path('privacy-policy', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions', views.terms_conditions, name='terms_conditions'),
    
    path('search', views.search,name='search'),
    path('booknow', views.book_now,name='booknow'),
    path('explore_by_items',views.explore_by_items,name='explore_by_items'),
    path('fetch_by_items',views.fetch_by_items,name='fetch_by_items'),
    path('fetch-shop/', views.fetch_shop,name='booknow'),
    path('location', views.location,name='location'),
    path('service', views.service,name='service'),
    path('items', views.items,name='items'),
    path('salon-profile', views.shop_profile,name='salon-profile'),
    path('submit-shop-review/', views.submit_shop_review, name='submit_shop_review'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
