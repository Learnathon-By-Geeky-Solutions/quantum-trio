from django.contrib import admin
from django.urls import path,include
from django import views
from myApp import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path('home', views.home),
    path('register/',include('Registration.urls')),
    # added by rakib for login purpose
    path('select_user', views.select_user_type),
    path('login', views.log_in),
    path('contact', views.contact_us),
    path('search', views.search),
    path('booknow', views.book_now),
    path('location', views.location),
    path('service', views.service),
    path('explore_by_items', views.explore_by_item),
    path('saloon_profile', views.view_salon_profile),
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


#     path('afterlogin', views.afterlogin_view,name='afterlogin'),
#     path('logout', LogoutView.as_view(template_name='ecom/logout.html'),name='logout'),
#     
#     path('contactus', views.contactus_view,name='contactus'),
#     path('search', views.search_view,name='search'),
#     path('send-feedback', views.send_feedback_view,name='send-feedback'),
#     path('view-feedback', views.view_feedback_view,name='view-feedback'),

#     path('adminclick', views.adminclick_view),
#     path('adminlogin', LoginView.as_view(template_name='ecom/adminlogin.html'),name='adminlogin'),
#     path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),

#     path('view-customer', views.view_customer_view,name='view-customer'),
#     path('delete-customer/<int:pk>', views.delete_customer_view,name='delete-customer'),
#     path('update-customer/<int:pk>', views.update_customer_view,name='update-customer'),

#     path('admin-products', views.admin_products_view,name='admin-products'),
#     path('admin-add-product', views.admin_add_product_view,name='admin-add-product'),
#     path('delete-product/<int:pk>', views.delete_product_view,name='delete-product'),
#     path('update-product/<int:pk>', views.update_product_view,name='update-product'),

#     path('admin-view-booking', views.admin_view_booking_view,name='admin-view-booking'),
#     path('delete-order/<int:pk>', views.delete_order_view,name='delete-order'),
#     path('update-order/<int:pk>', views.update_order_view,name='update-order'),


#     path('customersignup', views.customer_signup_view),
#     path('customerlogin', LoginView.as_view(template_name='ecom/customerlogin.html'),name='customerlogin'),
#     path('customer-home', views.customer_home_view,name='customer-home'),
#     path('my-order', views.my_order_view,name='my-order'),
#     path('my-profile', views.my_profile_view,name='my-profile'),
#     path('edit-profile', views.edit_profile_view,name='edit-profile'),
#     path('download-invoice/<int:orderID>/<int:productID>', views.download_invoice_view,name='download-invoice'),


#     path('add-to-cart/<int:pk>', views.add_to_cart_view,name='add-to-cart'),
#     path('cart', views.cart_view,name='cart'),
#     path('remove-from-cart/<int:pk>', views.remove_from_cart_view,name='remove-from-cart'),
#     path('customer-address', views.customer_address_view,name='customer-address'),
#     path('payment-success', views.payment_success_view,name='payment-success'),
