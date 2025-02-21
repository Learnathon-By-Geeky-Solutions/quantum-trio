from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
# for geolocation purpose
from django.http import JsonResponse
from geopy.geocoders import Nominatim

# use this to import any data from database
# -----------------------------------------
from myApp.models import *
from django.contrib.postgres.aggregates import ArrayAgg

# Create your views here.
def select_user_type(request):
    return render(request, 'app\login_signup\sign-up.html')

# Customer A/c registration steps starts here
# -------------------------------------------
def customer_register_step1(request):
    return render(request, 'app\login_signup\\register\customer\step1.html')

def customer_register_step2(request):
    return render(request, 'app\login_signup\\register\customer\step2.html')

# Business A/c registration steps starts here
# -------------------------------------------
def business_register_step1(request):
    return render(request, 'app\login_signup\\register\\business\step1.html')

def business_register_step2(request):
    # data = list(person.objects.values())  
    # print(data)
    # user = {
    #     'first-name': '',
    #     'last-name': '',
    #     'email': '',
    #     'password': '',
    #     'mobile-number': '',
    # }
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
            'password': make_password(request.POST.get("password", "")),
            'mobile-number': request.POST.get("mobile-number", ""),
        }
    return render(request, 'app\login_signup\\register\\business\step2.html')


def business_register_step3(request):
    district=District.objects.all().values('id', 'name')
    upazilla=Upazilla.objects.values('district__name').annotate(upazilla_names=ArrayAgg('name'))
    # print(upazilla)
    # user = {
    #     'business_name':'',
    #     'business_title':'',
    #     'website':'',
    #     'business_info':'',
    #     'gender':''
    # }
    if request.method == "POST":
        # debugging purpose only
        # user['business_name'] = request.POST.get("business_name", "")
        # user['business_title'] = request.POST.get("business_title", "")
        # user['website'] = request.POST.get("website", "")
        # user['business_info'] = request.POST.get("business_info", "")
        # user['gender'] = request.POST.get("gender", "")
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
    # user = {
    #     'district':'',
    #     'upazilla':'',
    #     'area':'',
    #     'landmark1':'',
    #     'landmark2':'',
    #     'landmark3':'',
    #     'landmark4':'',
    #     'landmark5':'',
    #     'latitude':'',
    #     'longitude':''
    # }
    if request.method == "POST":
        # user['district']=request.POST.get("district","")
        # user['upazilla']=request.POST.get("upazilla","")
        # user['area']=request.POST.get("area","")
        landmarks = request.POST.getlist("landmarks[]")  # Retrieves all landmarks as a list
        # Extract values safely
        # user['landmark1']= landmarks[0] if len(landmarks[0]) > 0 else ""
        # user['landmark2']= landmarks[1] if len(landmarks[1]) > 0 else ""
        # user['landmark3']= landmarks[2] if len(landmarks[2]) > 0 else ""
        # user['landmark4']= landmarks[3] if len(landmarks[3]) > 0 else ""
        # user['landmark5']= landmarks[4] if len(landmarks[4]) > 0 else ""
        
        landmark1= landmarks[0] if len(landmarks[0]) > 0 else ""
        landmark2= landmarks[1] if len(landmarks[1]) > 0 else ""
        landmark3= landmarks[2] if len(landmarks[2]) > 0 else ""
        landmark4= landmarks[3] if len(landmarks[3]) > 0 else ""
        landmark5= landmarks[4] if len(landmarks[4]) > 0 else ""
        # user['latitude']=request.POST.get("latitude", "")
        # user['longitude']=request.POST.get("longitude","")
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
    if request.method=='POST':
        pass
    return render(request, 'app\login_signup\\register\\business\step6.html')


def business_register_step7(request):
    return render(request, 'app\login_signup\\register\\business\step7.html')


def business_register_step8(request):
    return render(request, 'app\login_signup\\register\\business\step8.html')

