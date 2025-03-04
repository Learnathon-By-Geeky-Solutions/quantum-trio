from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse

# use this to import any data from database
from .models import District, Division, Service
from shop_profile.models import ShopProfile, ShopWorker
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
temp_user=get_user_model()
# Create your views here.
def home(request):
    if request.method != 'GET':
        # Return a 405 Method Not Allowed response for any non-GET requests
        return HttpResponseNotAllowed(['GET'])
    shop=ShopProfile.objects.all()

    return render(request, 'app/home.html', {'review': 333,'shops':shop})

def select_user_type(request):
    return render(request, 'app/login_signup/select_user_type.html')

"""Login method"""
def log_in(request):
    error = ''
    user_type = 'customer'
    if request.method=='GET':
        user_type=request.GET.get('profile-type')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Authenticate the user
        user = authenticate(request, username=email, password=password)
        # print(user.email)
        print(request.user.is_authenticated)
        print(user)
        if user is not None:
            login(request, user)
            """Redirect to user profile or Landing page"""
            if user.user_type=='shop':
                return redirect('home')
                
            elif user.user_type=='user':
                print('User')
                return redirect('home')
                
            else:
                print('Admin')  
        else:
            print('invalid username')
            error = "Invalid email or password"
            user_type = 'customer'  

    return render(request, 'app/login_signup/login.html', {'type': user_type, 'message': error})
def log_out(request):
    logout(request)
    return redirect('login')
# create_account purpose
def create_account(request):
    return render(request, 'app/login_signup/sign-up.html')

"""Shop profile view for customer end"""
def shop_profile(request):
    if request.method == 'GET':
        shop_id = request.GET.get('shop_id')

        # Validate shop_id
        if not shop_id or not shop_id.isdigit():
            return JsonResponse({"error": "Invalid shop ID"}, status=400)

        shop_id = int(shop_id)  # Convert to integer safely

        # Fetch the shop profile safely
        shop = get_object_or_404(ShopProfile, id=shop_id)

        # Retrieve workers related to the shop
        workers = ShopWorker.objects.filter(shop=shop)
        worker_names = [worker.name for worker in workers]

        # Return structured JSON response
        return JsonResponse({
            "shop_id": shop.id,
            "shop_name": shop.name,
            "workers": worker_names
        })

    return HttpResponseNotAllowed(['GET'])

"""Added login requred only for testing purpose"""
@login_required  
def contact_us(request):
    return render(request, 'app/contact_us.html')

def search(request):
    return render(request, 'app/search.html')

def service(request):
    services=Service.objects.all()
    return render(request, 'app/service.html',{'services':services})

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
    return render(request, 'app/explore_by_items.html')

# For Salon Profile


def view_salon_profile(request):
    return render(request, 'app/saloon_profile/dashboard.html')

# For Salon Deshboard


def view_dash_board(request):
    return render(request, 'app/salon_dashboard/index.html')


def view_salon_gallery(request):
    return render(request, 'app/salon_dashboard/saloon_gallery.html')


def view_saloon_calender(request):
    return render(request, 'app/salon_dashboard/saloon-calender.html')


def view_saloon_stuff(request):
    return render(request, 'app/salon_dashboard/staffs.html')


def view_settings(request):
    return render(request, 'app/salon_dashboard/saloon-setting.html')


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
