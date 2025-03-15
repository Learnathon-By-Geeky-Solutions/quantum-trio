from urllib.parse import urlencode
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.contrib.postgres.aggregates import ArrayAgg
# use this to import any data from database
from .models import District,Upazilla, Division, Service, Area,Item
from shop_profile.models import ShopProfile, ShopWorker, ShopService
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
    male_item=Item.objects.all()
    female_item=Item.objects.get()
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


def shop_profile(request):
    if request.method == 'GET':
        shop_id = request.GET.get('shop_id')
        # Validate shop_id
        if not shop_id or not shop_id.isdigit():
            return JsonResponse({"error": "Invalid shop ID"}, status=400)

        shop_id = int(shop_id)  # Convert to integer safely

        shop = ShopProfile.objects.filter(id=shop_id).first()  # Fetch as object
        service = ShopService.objects.filter(shop=shop_id)
        workers = ShopWorker.objects.filter(shop=shop_id)
 
    return render(request, 'app/saloon_profile/dashboard.html', {
             "shop": shop, 
             "shop_services": service,
             "shop_workers": workers
        })

def contact_us(request):
    return render(request, 'app/contact_us.html')

def search(request):
    return render(request, 'app/search.html')

def service(request):
    services=Service.objects.all()
    return render(request, 'app/service.html',{'services':services})

def book_now(request):
    district = District.objects.all().values('id', 'name')
    upazilla = Upazilla.objects.values('district__name').annotate(upazilla_names=ArrayAgg('name'))
    area = Area.objects.values('upazilla__name').annotate(area_names=ArrayAgg('name')) 

    print(area)
    if request.method == 'GET':
        return render(request, 'app/book_now.html',{'district':list(district),'Upazilla':list(upazilla),'Area':area})
    else:
        return HttpResponseNotAllowed(['GET'])
    
def fetch_shop(request):
    district = request.GET.get('district', '')
    upazila = request.GET.get('upazila', '')
    area = request.GET.get('area', '')
    limit = int(request.GET.get('limit', 9))
    offset = int(request.GET.get('offset', 0))
    print(district,upazila,area)
    salons = ShopProfile.objects.all()
    if district:
        salons = salons.filter(shop_state=district)
    if upazila:
        salons = salons.filter(shop_city=upazila)
    if area:
        salons = salons.filter(shop_area=area)

    salons = salons[offset:offset + limit]
    
    salon_list = [
        {
            'shop_id': salon.id,
            'shop_name': salon.shop_name,
            'shop_rating': salon.shop_rating,
            'shop_customer_count': salon.shop_customer_count,
            'shop_city': salon.shop_city,
            'shop_title': salon.shop_title,
            # 'image': salon.shop_picture.url if salon.shop_picture else '',  # Ensure media URLs work
        }
        for salon in salons
    ]
    
    return JsonResponse(salon_list, safe=False)

def location(request):
    divisions = Division.objects.all()  # Fetch all Division objects
    districts = District.objects.all()
    return render(request, 'app/location.html', {'divisions': divisions, 'districts': districts})

def explore_by_item(request):
    return render(request, 'app/explore_by_items.html')


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
