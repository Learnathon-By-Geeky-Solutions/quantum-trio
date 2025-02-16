from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render

# Create your views here.


def home(request):
    if request.method != 'GET':
        # Return a 405 Method Not Allowed response for any non-GET requests
        return HttpResponseNotAllowed(['GET'])

    return render(request, 'app/home.html')

# added by rakib for login purpose
def select_user_type(request):
    return render(request, 'app\login_signup\select_user_type.html')

def login(request):
    user_type=request.GET.get('profile-type', 'Customer')
    return render(request, 'app\login_signup\login.html',{'type': user_type})
      
def contact_us(request):
    return render(request, 'app\contact_us.html')

def search(request):
    return render(request, 'app\search.html')

def service(request):
    return render(request, 'app\service.html')


def book_now(request):
    if request.method == 'GET':
        return render(request, 'app/book_now.html')
    else:
        return HttpResponseNotAllowed(['GET'])


def location(request):
    return render(request, 'app\location.html')


def explore_by_item(request):
    return render(request, 'app\explore_by_items.html')

#For Salon Profile
def view_salon_profile(request):
    return render(request, 'app\saloon_profile\dashboard.html')

#For Salon Deshboard
def view_dash_board(request):
    return render(request, 'app\salon_dashboard\index.html')

def view_salon_gallery(request):
    return render(request, 'app\salon_dashboard\saloon_gallery.html')

def view_saloon_calender(request):
    return render(request, 'app\salon_dashboard\saloon-calender.html')

def view_saloon_stuff(request):
    return render(request, 'app\salon_dashboard\staffs.html')

def view_settings(request):
    return render(request, 'app\salon_dashboard\saloon-setting.html')

def view_notification(request):
    return render(request, 'app/salon_dashboard/notifications.html')

def view_reviews(request):
    return render(request, 'app/salon_dashboard/reviews.html')

def view_customers(request):
    return render(request, 'app/salon_dashboard/customers.html')

def booking_slots(request):
    return render(request, 'app/salon_dashboard/booking-slots.html')

def view_message(request):
    return render(request, 'app/salon_dashboard/message.html')

def view_message_reply(request):
    return render(request, 'app/salon_dashboard/reply-message.html')


