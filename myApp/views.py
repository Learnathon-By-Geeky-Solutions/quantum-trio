from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.contrib.auth.models import User

from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
# for geolocation purpose
from django.http import JsonResponse
from geopy.geocoders import Nominatim

# use this to import any data from database
from .models import *
from django.contrib.postgres.aggregates import ArrayAgg

#This is a testing purpose only please avoid the function
# I tried to fetch all the location details using the location latitude and longitude
# but it using geolocation it may be not possible cause geolocation doesnt provide me the accurate 
# location pointer
def get_location(request):
    data={}
    if request.method =='GET':
        lat = request.GET.get('lat')
        lon = request.GET.get('lon')
        if lat and lon:
            geolocator = Nominatim(user_agent="geoapi")
            location = geolocator.reverse((lat, lon), exactly_one=True)
            address = location.raw.get('address', {})
            data = {
                "country": address.get("country"),
                "division": address.get("state"),
                "city": address.get("city") or address.get("town") or address.get("village"),
                "village":address.get("village"),
                "postcode": address.get("postcode"),
                "latitude": lat,
                "longitude": lon
            }
            # return JsonResponse(data)
        # return JsonResponse({"error": "Invalid coordinates"}, status=400)
    return render(request, 'app/get_location.html',{'data':data})

# Create your views here.
def home(request):
    if request.method != 'GET':
        # Return a 405 Method Not Allowed response for any non-GET requests
        return HttpResponseNotAllowed(['GET'])

    return render(request, 'app/home.html', {'review': 333})




# added by rakib for login purpose


def select_user_type(request):
    return render(request, 'app\login_signup\select_user_type.html')

# login purpose


def login(request):
    user_type = request.GET.get('profile-type', 'Customer')
    return render(request, 'app\login_signup\login.html', {'type': user_type})

# create_account purpose

def create_account(request):
    return render(request, 'app\login_signup\sign-up.html')

# customer A/c registration steps starts here

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

# For Salon Profile


def view_salon_profile(request):
    return render(request, 'app\saloon_profile\dashboard.html')

# For Salon Deshboard


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
