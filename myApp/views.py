from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from .models import Division,District
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
# use this to import any data from database
from .models import *
from django.contrib.postgres.aggregates import ArrayAgg
from Registration.backends import Authenticate
from user_profile.models import UserProfile
from shop_profile.models import ShopProfile
# Create your views here.
def home(request):
    if request.method != 'GET':
        # Return a 405 Method Not Allowed response for any non-GET requests
        return HttpResponseNotAllowed(['GET'])

    return render(request, 'app/home.html', {'review': 333})

def select_user_type(request):
    return render(request, 'app\login_signup\select_user_type.html')

# login purpose
def login(request):
    error=''
    user_type = request.GET.get('profile-type', 'Customer')
    if request.method=='POST':
        email = request.POST.get('email', '').strip() 
        password = request.POST.get('password', '').strip()
        if user_type=='User':
            if UserProfile.objects.filter(email=email):
                user=Authenticate.authenticate(email,password,'user')
                if isinstance(user,UserProfile):
                    print("You are right.")
                else:
                    print('You are wrong.') 
            else:
                print('The email is not registered.')

        else:
            if ShopProfile.objects.filter(shop_email=email).exists():
                shop = Authenticate.authenticate(email, password, 'shop')
                shop=ShopProfile.objects.filter(shop_email=email)
                if isinstance(shop, ShopProfile): 
                    print("You are right.")
                    error='You are right.'
                else:
                    print("You are wrong.") 
                    error='You are wrong.'
            else:
                print("The email is not registered.")
                error='The email is not registered.'
    return render(request, 'app\login_signup\login.html', {'type': user_type,'message':error})

# create_account purpose

def create_account(request):
    return render(request, 'app\login_signup\sign-up.html')

# customer A/c registration steps starts here

def contact_us(request):
    return render(request, 'app\contact_us.html')


def search(request):
    return render(request, 'app\search.html')

 
def service(request):
    services=Service.objects.all()
    return render(request, 'app\service.html',{'services':services})


def book_now(request):
    if request.method == 'GET':
        return render(request, 'app/book_now.html')
    else:
        return HttpResponseNotAllowed(['GET'])


def location(request):
    divisions = Division.objects.all()  # Fetch all Division objects
    districts = District.objects.all()
    return render(request, 'app/location.html', {'divisions': divisions, 'districts': districts})


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
