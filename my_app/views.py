from uuid import uuid4
from urllib.parse import urlencode
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from .models import District, Upazilla, Division, Service, Area, Item, ReviewCarehub, Contact
from shop_profile.models import ShopGallery, ShopProfile, ShopWorker, ShopService, ShopReview
from booking.models import BookingSlot
from django.contrib.auth import get_user_model

User = get_user_model()

def home(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    
    shops = ShopProfile.objects.all()
    male_items = Item.objects.filter(Q(gender='Male') | Q(gender='Both')).values()
    female_items = Item.objects.filter(Q(gender='Female') | Q(gender='Both')).values()
    reviews = ReviewCarehub.objects.all().order_by("-created_at")
    statistics = _get_statistics()
    reviewer_name = _get_reviewer_name(request.user)
    
    return render(request, 'app/home.html', {
        'reviews': reviews,
        'shops': shops,
        'male': male_items,
        'female': female_items,
        'reviewer_name': reviewer_name,
        'statistics': statistics
    })

def _get_statistics():
    return {
        'booked_appointment': BookingSlot.objects.count(),
        'registered_shop': ShopProfile.objects.count(),
        'available_upazilla': ShopProfile.objects.values('shop_city').distinct().count(),
        'available_barber': ShopWorker.objects.count()
    }

def _get_reviewer_name(user):
    if not user.is_authenticated:
        return "You are not allowed to give review."
    if user.user_type == "shop":
        return user.shop_profile.shop_name
    if user.user_type == "user":
        return f"{user.user_profile.first_name} {user.user_profile.last_name}"
    return "You are not allowed to give review."

def submit_review(request):
    if request.method != "POST" or not request.user.is_authenticated:
        messages.error(request, "Please log in first.")
        return redirect("home")
    
    comment = request.POST.get("review", "").strip()
    rating = _validate_rating(request.POST.get("rating", "0").strip())
    
    if rating is None:
        messages.error(request, "Invalid rating value.")
        return redirect("home")
    
    reviewer_instance = _get_reviewer_instance(request.user)
    if not reviewer_instance:
        messages.error(request, "Please log in first.")
        return redirect("home")
    
    ReviewCarehub.objects.create(
        reviewer_type=ContentType.objects.get_for_model(reviewer_instance),
        reviewer_id=reviewer_instance.id,
        comment=comment,
        rating=rating
    )
    messages.success(request, "The review was submitted successfully. Thank you!")
    return redirect("home")

def _validate_rating(rating_str):
    try:
        rating = float(rating_str)
        return rating if 0 <= rating <= 5 else None
    except ValueError:
        return None

def _get_reviewer_instance(user):
    if hasattr(user, "shop_profile"):
        return user.shop_profile
    if hasattr(user, "user_profile"):
        return user.user_profile
    return None

def select_user_type(request):
    return render(request, 'app/login_signup/select_user_type.html')

def log_in(request):
    user_type = request.GET.get('profile-type', 'customer')
    error = ''
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.user_type == 'user':
                login(request, user)
                return redirect('home')
            elif user.user_type == 'shop':
                login(request, user)
                return redirect('dashboard/')
            elif user.user_type == 'admin':
                login(request, user)
                return redirect('admin/')
            else:
                error = "Unrecognized user type"
        else:
            error = "Invalid email or password"
    
    return render(request, 'app/login_signup/login.html', {'type': user_type, 'message': error})

def success_reset_password():
    return HttpResponse("Password reset successful. This is a test response.")

def log_out(request):
    logout(request)
    return redirect('login')

def create_account(request):
    return render(request, 'app/login_signup/sign-up.html')

def shop_profile(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    
    shop_id = request.GET.get('shop_id')
    if not shop_id or not shop_id.isdigit():
        return JsonResponse({"error": "Invalid shop ID"}, status=400)
    
    shop = ShopProfile.objects.filter(id=int(shop_id)).first()
    if not shop:
        return JsonResponse({"error": "Shop not found"}, status=404)
    
    services = ShopService.objects.filter(shop=shop.id)
    workers = ShopWorker.objects.filter(shop=shop.id)
    images = ShopGallery.objects.filter(shop=shop.id)
    
    return render(request, 'app/saloon_profile/dashboard.html', {
        "shop": shop,
        "shop_services": services,
        "shop_workers": workers,
        "shop_images": images
    })

@require_POST
@login_required
def submit_shop_review(request):
    rating = request.POST.get('rating')
    review = request.POST.get('review')
    shop_id = request.POST.get('shop_id')
    user_id = request.user.id
    
    if not all([rating, review, shop_id]):
        return JsonResponse({'success': False, 'error': 'Fill all the required fields.'}, status=400)
    
    try:
        shop = ShopProfile.objects.get(id=shop_id)
        if not BookingSlot.objects.filter(user__id=user_id, shop__id=shop_id, status='completed').exists():
            return JsonResponse({'success': False, 'error': 'You are not allowed.'}, status=403)
        
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
    return district, upazilla, area

@csrf_protect
def contact_us(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        try:
            Contact.objects.create(name=name, email=email, subject=subject, message=message)
            messages.success(request, "Your message has been sent successfully!")
        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")
    
    return render(request, 'app/contact_us.html')

def about_us(request):
    return render(request, 'app/about_us.html')

def privacy_policy(request):
    return render(request, 'app/privacy_policy.html')

def terms_conditions(request):
    return render(request, 'app/terms_conditions.html')
def search_shops_for_title(keyword):
    return ShopProfile.objects.filter(
            Q(shop_name__icontains=keyword) |
            Q(shop_title__icontains=keyword) |
            Q(shop_info__icontains=keyword)
        ).order_by('-shop_rating')
    
def search_shops_location_based(keyword):
    return ShopProfile.objects.filter(
            Q(shop_state__icontains=keyword) |
            Q(shop_city__icontains=keyword) |
            Q(shop_area__icontains=keyword) |
            Q(shop_landmark_1__icontains=keyword) |
            Q(shop_landmark_2__icontains=keyword) |
            Q(shop_landmark_3__icontains=keyword) |
            Q(shop_landmark_4__icontains=keyword) |
            Q(shop_landmark_5__icontains=keyword)
        ).distinct().order_by('-shop_rating')
    
def search(request):
    if request.method != "POST":
        return render(request, 'app/search.html', {'keyword': '', 'shops': [], 'location_based': [], 'service_based': [], 'items': []})
    keyword = request.POST.get('search', '').strip()
    shops = location_based = service_based = items = []
    if keyword:
        shops = search_shops_for_title(keyword)
        location_based = search_shops_location_based(keyword)
        
        service_based = ShopProfile.objects.filter(
            shopservice__item__name__icontains=keyword
        ).distinct().order_by('-shop_rating')
        
        items = Item.objects.filter(name__icontains=keyword).distinct()
    
    return render(request, 'app/search.html', {
        'keyword': keyword,
        'shops': shops,
        'location_based': location_based,
        'service_based': service_based,
        'items': items
    })

def service(request):
    services = Service.objects.all()
    return render(request, 'app/service.html', {'services': services})

def book_now(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    
    district, upazilla, area = area_database()
    dist = request.GET.get('district', request.GET.get('upazilla', ''))
    
    return render(request, 'app/book_now.html', {
        'district': list(district),
        'Upazilla': list(upazilla),
        'Area': area,
        'dist': dist
    })

def fetch_shop(request):
    district = request.GET.get('district', '')
    upazila = request.GET.get('upazila', '')
    area = request.GET.get('area', '')
    limit = int(request.GET.get('limit', 9))
    offset = int(request.GET.get('offset', 0))
    
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
            'shop_rating': str(float(salon.shop_rating)),
            'shop_customer_count': salon.shop_customer_count,
            'shop_city': salon.shop_city,
            'shop_title': salon.shop_title,
            'image': salon.shop_picture.url if salon.shop_picture and hasattr(salon.shop_picture, 'url') else ''
        }
        for salon in salons
    ]
    return JsonResponse(sorted(salon_list, key=lambda x: x['shop_rating'], reverse=True), safe=False)
def extract_shop_data(shop_page):
    return [
        {
            'shop_id': shop.id,
            'shop_name': shop.shop_name,
            'shop_rating': shop.shop_rating,
            'shop_customer_count': shop.shop_customer_count,
            'shop_city': shop.shop_city,
            'shop_title': shop.shop_title,
            'image': shop.shop_picture.url if shop.shop_picture else ''
        }
        for shop in shop_page
    ]
def fetch_by_items(request):
    item = request.GET.get('item')
    district = request.GET.get('district')
    upazilla = request.GET.get('upazilla')
    area = request.GET.get('area')
    limit = int(request.GET.get('limit', 9))
    offset = int(request.GET.get('offset', 0))
    
    shops = ShopProfile.objects.filter(shopservice__item__name=item).order_by('-shop_rating')
    if district:
        shops = shops.filter(shop_state=district)
    if upazilla:
        shops = shops.filter(shop_city=upazilla)
    if area:
        shops = shops.filter(shop_area=area)
    
    paginator = Paginator(shops, limit)
    shop_page = paginator.get_page(offset // limit + 1)
    
    shop_data = extract_shop_data(shop_page)
    
    return JsonResponse({
        'shop': shop_data,
        'has_next': shop_page.has_next(),
        'has_previous': shop_page.has_previous()
    })

def location(request):
    divisions = Division.objects.all()
    districts = District.objects.all()
    return render(request, 'app/location.html', {'divisions': divisions, 'districts': districts})

def explore_by_items(request):
    item = request.GET.get('item', '')
    district, upazilla, area = area_database()
    return render(request, 'app/explore_by_items.html', {
        'item': item,
        'district': list(district),
        'Upazilla': list(upazilla),
        'Area': area
    })

def items(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(['GET'])
    
    service = request.GET.get('service', '')
    items = Item.objects.filter(service__name=service) if service else []
    return render(request, 'app/items.html', {'service': service, 'items': items})