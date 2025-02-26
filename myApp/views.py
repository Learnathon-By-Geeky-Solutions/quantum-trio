from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from .models import Division,District
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
# use this to import any data from database
from .models import *
from django.contrib.postgres.aggregates import ArrayAgg
from user_profile.models import UserProfile
from shop_profile.models import ShopProfile
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages
# Create your views here.
def home(request):
    if request.method != 'GET':
        # Return a 405 Method Not Allowed response for any non-GET requests
        return HttpResponseNotAllowed(['GET'])

    return render(request, 'app/home.html', {'review': 333})

def select_user_type(request):
    return render(request, 'app\login_signup\select_user_type.html')

"""user defined authenticate function"""
def authenticate(username=None, password=None, type=None, **kwargs):
        if not username or not password or not type:
            return None  # Ensure all required parameters are provided

        try:
            if type == 'user':
                user = UserProfile.objects.filter(email=username).first()
                if user and user.check_password(password):
                    return user

            elif type == 'shop':
                shop = ShopProfile.objects.filter(shop_email=username).first()
                if shop and shop.check_password(password):
                    return shop

        except ObjectDoesNotExist:  
            return None  
        return None

"""This is user defined decorator"""
def login_required_custom(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id') :
            messages.error(request, "You must be logged in to access this page.")
            return redirect('/login')  # Redirect to login page if not authenticated
        return view_func(request, *args, **kwargs)
    return wrapper

"""This function will create a session instance name user_id and shop_id"""
def log_in( request,username,type):
    try:
        if type=='user':
            user = UserProfile.objects.get(username=username)
            request.session['user_id'] = user.id
            return True, "Login successful!"
        else:
            user = ShopProfile.objects.get(shop_email=username)
            request.session['shop_id'] = user.id
            return True, "Login successful!"

    except User.DoesNotExist:
        return False, "User does not exist"

"""Login method"""
def login(request):
    error=''
    user_type = request.GET.get('profile-type', 'Customer')
    if request.method=='POST':
        email = request.POST.get('email', '').strip() 
        password = request.POST.get('password', '').strip()
        print(email,password)
        if user_type=='User':
            if UserProfile.objects.filter(email=email).exists():
                user=authenticate(email,password,'user')
                if isinstance(user,UserProfile):
                    print("You are right.")
                    check,_=log_in(request, email,'user')
                    if check:
                        return redirect("home")
                        
                    else:
                        print("You are right.")
                else:
                    print('You are wrong.') 
            else:
                print('The email is not registered.')

        else:
            print('does exist:',ShopProfile.objects.filter(shop_email=email).exists())
            if ShopProfile.objects.filter(shop_email=email).exists():
                
                shop=ShopProfile.objects.filter(shop_email=email)
                shop = authenticate(email, password, 'shop')
                if isinstance(shop, ShopProfile): 
                    print("You are right.")
                    error='You are right.'
                    check,_=log_in(request, email,'shop')
                    if check:
                        # request.session.flush()
                        return HttpResponse("home")
                    else:
                        print("You are right.")
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
@login_required_custom
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
