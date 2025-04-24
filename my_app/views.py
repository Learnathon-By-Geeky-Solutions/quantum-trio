from urllib.parse import urlencode
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
# use this to import any data from database
from .models import District,Upazilla, Division, Service, Area,Item,ReviewCarehub,Contact
from shop_profile.models import ShopProfile, ShopWorker, ShopService, ShopReview
from booking.models import BookingSlot
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate,login, logout
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.urls import reverse
temp_user=get_user_model()
# Create your views here. 
def home(request):
    if request.method != 'GET':
        # Return a 405 Method Not Allowed response for any non-GET requests
        return HttpResponseNotAllowed(['GET'])
    shop=ShopProfile.objects.all()
    print(shop)
    male_item = Item.objects.filter(Q(gender='Male') | Q(gender='Both')).values()
    female_item = Item.objects.filter(Q(gender='Female') | Q(gender='Both')).values()
    reviews = ReviewCarehub.objects.all().order_by("-created_at")  # Get all reviews sorted by latest

    ##for review
    reviewer_name = "You are not allowed to give review."
    if request.user.is_authenticated:
        if request.user.user_type == "shop":
            reviewer_name = request.user.shop_profile.shop_name
        elif request.user.user_type == "user":
            reviewer_name = f"{request.user.user_profile.first_name} {request.user.user_profile.last_name}"
    
    booked_appointment=BookingSlot.objects.all().count()
    registered_shop=ShopProfile.objects.all().count()
    available_upazilla = ShopProfile.objects.order_by('shop_city').distinct('shop_city').count()
    available_barber=ShopWorker.objects.all().count()
    statistics = {
        'booked_appointment': booked_appointment,
        'registered_shop': registered_shop,
        'available_upazilla': available_upazilla,
        'available_barber': available_barber
    }
    return render(request, 'app/home.html', {
        'reviews': reviews,
        'shops':shop,
        'male':male_item,
        'female':female_item,
        'reviewer_name':reviewer_name,
        'statistics':statistics
    })
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages

def submit_review(request):
    if request.method == "POST" and request.user.is_authenticated:
        comment = request.POST.get("review", "").strip()
        rating = request.POST.get("rating", "0").strip()

        # Validate rating
        try:
            rating = float(rating)
            if rating < 0 or rating > 5:
                raise ValueError("Rating must be between 0 and 5.")
        except ValueError:
            messages.error(request, "Invalid rating value.")
            return redirect("home")

        # Determine reviewer type
        if hasattr(request.user, "shop_profile"):
            reviewer_instance = request.user.shop_profile
        elif hasattr(request.user, "user_profile"):
            reviewer_instance = request.user.user_profile
        else:
            return HttpResponse("Invalid reviewer", status=400)

        # Create the review
        ReviewCarehub.objects.create(
            reviewer_type=ContentType.objects.get_for_model(reviewer_instance),
            reviewer_id=reviewer_instance.id,
            comment=comment,
            rating=rating
        )

        messages.success(request, "The review was submitted successfully. Thank you!")
        return redirect("home")

    return HttpResponse("Invalid request", status=400)
 
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
                return redirect('home')
        else:
            print('invalid username')
            error = "Invalid email or password"
            user_type = 'customer'  

    return render(request, 'app/login_signup/login.html', {'type': user_type, 'message': error})
def success_reset_password(request):
    return HttpResponse("Password reset successful. This is a test response.")

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
    
@require_POST
@login_required
def submit_shop_review(request):
    try:
        # Assume you're extracting data from POST
        rating = request.POST.get('rating')
        review = request.POST.get('review')
        shop_id = request.POST.get('shop_id')
        user_id = request.user.id  # or wherever you're getting user_id from
        shop = ShopProfile.objects.get(id=shop_id)
        """If any field is missing"""
        if not rating or not review or not shop_id or not user_id:
            return JsonResponse({'success': False, 'error': 'Fill all the required fields.'}, status=404)
        """If the user has not received any services of the shop then how can he rate?"""
        if not BookingSlot.objects.filter(user__id=user_id,shop__id=shop_id,status='completed').exists():
            return JsonResponse({'success': False, 'error': 'You are not allowed.'}, status=404)
        ShopReview.objects.create(
            rating=rating,
            review=review,
            shop=shop,
            reviewer_id=user_id
        )
        return JsonResponse({'success': True})

    except ShopProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Shop not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
def area_database():
    district = District.objects.all().values('id', 'name')
    upazilla = Upazilla.objects.values('district__name').annotate(upazilla_names=ArrayAgg('name'))
    area = Area.objects.values('upazilla__name').annotate(area_names=ArrayAgg('name')) 
    return district,upazilla,area

@csrf_protect
def contact_us(request):
    if request.method=="POST":
        name=request.POST.get('name')
        email=request.POST.get('email')
        subject=request.POST.get('subject')
        message=request.POST.get('message')
        try:
            Contact.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, "Your message has been sent successfully!")  # optional
        except Exception as e: 
            messages.error(request, f"Something went wrong: {str(e)}") 
        print(name,email,subject,message)
    return render(request, 'app/contact_us.html')

def about_us(request):
    return render(request, 'app/about_us.html')

def privacy_policy(request):
    return render(request, 'app/privacy_policy.html')

def terms_conditions(request):
    return render(request, 'app/terms_conditions.html')

def search(request):
    shops=location_based=items=service_based = []
    keyword = ''
    if request.method == "POST":
        keyword = request.POST.get('search', '').strip()
        if keyword:
            # Based on name, title and info only
            shops = ShopProfile.objects.filter(
                Q(shop_name__icontains=keyword) |
                Q(shop_title__icontains=keyword) |
                Q(shop_info__icontains=keyword)
            ).order_by('-shop_rating')
            
            # Based on location 
            # If the keyword matches with any shops location
            location_based = ShopProfile.objects.filter(
                Q(shop_state__icontains=keyword) |
                Q(shop_city__icontains=keyword) |
                Q(shop_area__icontains=keyword) |
                Q(shop_landmark_1__icontains=keyword)|
                Q(shop_landmark_2__icontains=keyword)|
                Q(shop_landmark_3__icontains=keyword)|
                Q(shop_landmark_4__icontains=keyword)|
                Q(shop_landmark_5__icontains=keyword)
            ).distinct().order_by('-shop_rating')
            print(location_based)
            
            # Based on service 
            # If the keyword matches with shops service 
            service_based = ShopProfile.objects.filter(
                shopservice__item__name__icontains=keyword
            ).distinct().order_by('-shop_rating')
            print(service_based)
            # Based on item
            # If the keyword matches with any item 
            items = Item.objects.filter(
                name__icontains=keyword
            ).distinct()
            
    return render(request, 'app/search.html', {
        'keyword': keyword,
        'shops': shops,
        'location_based':location_based,
        'service_based':service_based,
        'items':items        
    })

def service(request):
    services=Service.objects.all()
    return render(request, 'app/service.html',{'services':services})

def book_now(request):
    district,upazilla,area=area_database()
    dist=""
    if request.GET.get('district'):
        dist=request.GET.get('district')
    if request.GET.get('upazilla'):
        dist=request.GET.get('upazilla')
        
    if request.method == 'GET':
        return render(request, 'app/book_now.html',{'district':list(district),'Upazilla':list(upazilla),'Area':area,'dist':dist})
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
            # 'shop_rating': salon.shop_rating,
            'shop_rating': str(float(salon.shop_rating)),
            'shop_customer_count': salon.shop_customer_count,
            'shop_city': salon.shop_city,
            'shop_title': salon.shop_title,
            'image': salon.shop_picture.url if salon.shop_picture and hasattr(salon.shop_picture, 'url') else '',
            # 'image': salon.shop_picture.url if salon.shop_picture else '',  # Ensure media URLs work
        }
        for salon in salons
    ]
    salon_list = sorted(salon_list, key=lambda x: x['shop_rating'], reverse=True)
    return JsonResponse(salon_list, safe=False)

def fetch_by_items(request):
    """First find by items"""
    item=request.GET.get('item')
    shop=ShopProfile.objects.filter(shopservice__item__name=item)
    
    """Then filter by area if any criteria given"""
    district=request.GET.get('district')
    upazilla=request.GET.get('upazilla')
    area=request.GET.get('area')
    
    if district:
        shop = shop.filter(shop_state=district)
    if upazilla:
        shop = shop.filter(shop_city=upazilla)
    if area:
        shop = shop.filter(shop_area=area)
  
    limit = int(request.GET.get('limit', 9))  # Default to 9 if no limit is provided
    offset = int(request.GET.get('offset', 0))  # Default to 0 if no offset is provided
    """Finding available shops of the desired service or item"""

    paginator = Paginator(shop, limit)
    shop_page = paginator.get_page(offset // limit + 1)  # Get the current page based on the offset
    shop_data=[]
    for temp in shop_page:
        
        shop_data.append({
            'shop_id': temp.id,
            'shop_name': temp.shop_name,
            'shop_rating': temp.shop_rating,
            'shop_customer_count': temp.shop_customer_count,
            'shop_city': temp.shop_city,
            'shop_title': temp.shop_title,
            'image': temp.shop_picture.url if temp.shop_picture else '',
           
        })
    response_data = {
        'shop': shop_data,
        'has_next': shop_page.has_next(),  # if there's another page
        'has_previous': shop_page.has_previous(),  # if there's a previous page
    }
    return JsonResponse(response_data)
def location(request):
    divisions = Division.objects.all()  # Fetch all Division objects
    districts = District.objects.all()
    return render(request, 'app/location.html', {'divisions': divisions, 'districts': districts})

# def explore_by_items(request):
#     item=""
#     if(request.method=="GET"):
#         item=request.GET.get('item')
#     print(item)
#     district,upazilla,area=area_database()
#     return render(request, 'app/explore_by_items.html',{'item':item,'district':list(district),'Upazilla':list(upazilla),'Area':area})

def explore_by_items(request):
    item = request.GET.get('item', '')
    print(item)
    district, upazilla, area = area_database()
    return render(request, 'app/explore_by_items.html', {'item': item, 'district': list(district), 'Upazilla': list(upazilla), 'Area': area})
 
def items(request):
    item=service=''
    if(request.method=="GET"):
        service=request.GET.get('service')
        item=Item.objects.filter(service__name=service)
        print(item)
    return render(request, 'app/items.html',{'service':service,'items':item})

