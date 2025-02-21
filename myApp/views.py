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


def customer_register_step1(request):
    return render(request, 'app\login_signup\\register\customer\step1.html')


def customer_register_step2(request):
    return render(request, 'app\login_signup\\register\customer\step2.html')

# Business A/c registration steps starts here

def business_register_step1(request):
    return render(request, 'app\login_signup\\register\\business\step1.html')

def business_register_step2(request):
    # data = list(person.objects.values())  
    # print(data)
    user = {
        'first-name': '',
        'last-name': '',
        'email': '',
        'password': '',
        'mobile-number': '',
    }
    if request.method == "POST":
        # user['first_name'] = request.POST.get("first-name", "")
        # user['last_name'] = request.POST.get("last-name", "")
        # user['email'] = request.POST.get("email", "")
        # user['password'] = request.POST.get(
        #     "password", "")  # Encrypt before storing!
        # user['mobile_number'] = request.POST.get("mobile-number", "")
        # Debugging: Print data to verify
        # print(user)
        request.session["user"] = {
            'first-name': request.POST.get("first-name", ""),
            'last-name': request.POST.get("last-name", ""),
            'email': request.POST.get("email", ""),
            'password': request.POST.get("password", ""),
            'mobile-number': request.POST.get("mobile-number", ""),
        }
    return render(request, 'app\login_signup\\register\\business\step2.html')


def business_register_step3(request):
    district=District.objects.all().values('id', 'name')
    upazilla=Upazilla.objects.values('district__name').annotate(upazilla_names=ArrayAgg('name'))
    # print(upazilla)
    user = {
        'business_name':'',
        'business_title':'',
        'website':'',
        'business_info':'',
        'gender':''
    }
    if request.method == "POST":
        # debugging purpose only
        user['business_name'] = request.POST.get("business_name", "")
        user['business_title'] = request.POST.get("business_title", "")
        user['website'] = request.POST.get("website", "")
        user['business_info'] = request.POST.get("business_info", "")
        user['gender'] = request.POST.get("gender", "")
        # print(user)

        request.session["user"].update({
            'business_name': request.POST.get("business_name", ""),
            'business_title': request.POST.get("business_title", ""),
            'website': request.POST.get("website", ""),
            'business_info': request.POST.get("business_info", ""),
            'gender': request.POST.get("gender", ""),
        })
        request.session.modified = True #update the session variable
    return render(request, 'app\login_signup\\register\\business\step3.html',{'district':list(district),'Upazilla':list(upazilla)})


def business_register_step4(request):
    # for debugging purpose only
    user = {
        'district':'',
        'upazilla':'',
        'area':'',
        'landmark1':'',
        'landmark2':'',
        'landmark3':'',
        'landmark4':'',
        'landmark5':'',
        'latitude':'',
        'longitude':''
    }
    if request.method == "POST":
        user['district']=request.POST.get("district","")
        user['upazilla']=request.POST.get("upazilla","")
        user['area']=request.POST.get("area","")
        landmarks = request.POST.getlist("landmarks[]")  # Retrieves all landmarks as a list
        # Extract values safely
        landmark1=user['landmark1']= landmarks[0] if len(landmarks[0]) > 0 else ""
        landmark2=user['landmark2']= landmarks[1] if len(landmarks[1]) > 0 else ""
        landmark3=user['landmark3']= landmarks[2] if len(landmarks[2]) > 0 else ""
        landmark4=user['landmark4']= landmarks[3] if len(landmarks[3]) > 0 else ""
        landmark5=user['landmark5']= landmarks[4] if len(landmarks[4]) > 0 else ""
        user['latitude']=request.POST.get("latitude", "")
        user['longitude']=request.POST.get("longitude","")
        # print(user)
        request.session["user"].update({
                'district': request.POST.get("district", ""),
                'upazilla': request.POST.get("upazilla", ""),
                'area': request.POST.get("area", ""),
                'landmark1':landmark1,
                'landmark2':landmark2,
                'landmark3':landmark3,
                'landmark4':landmark4,
                'landmark5':landmark5,
                'latitude':request.POST.get("latitude", ""),
                'longitude':request.POST.get("longitude",""),
        })
        request.session.modified = True  #update the session variable
    service=Service.objects.all().values('id', 'name')
    # print(service)
    return render(request, 'app\login_signup\\register\\business\step4.html',{'services':service})


def business_register_step5(request):
    if request.method =='POST':
        services = request.POST.getlist("services[]", []) #posts only the id's of service
        # Fetch available services
        available_services = Item.objects.values('service__id','service__name').annotate(service_names=ArrayAgg('name'))
        # print(available_services)
        # Convert IDs to strings for comparison
        matching_services = [
            service for service in available_services if str(service['service__id']) in services
        ]
        print(matching_services)  # Debug output
    # print(request.session['user'])
    return render(request, 'app\login_signup\\register\\business\step5.html',{'services':matching_services})


def business_register_step6(request):
    return render(request, 'app\login_signup\\register\\business\step6.html')


def business_register_step7(request):
    return render(request, 'app\login_signup\\register\\business\step7.html')


def business_register_step8(request):
    return render(request, 'app\login_signup\\register\\business\step8.html')


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
