import json
from collections import OrderedDict
from datetime import datetime, date, timedelta, timezone  # Add timezone import
from decimal import Decimal
from calendar import HTMLCalendar
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q, Avg, F, ExpressionWrapper, DateTimeField, Value, CharField, BooleanField, Case, When
from django.db.models.functions import Concat, Cast
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404,redirect
from django.utils import timezone
from django.utils.timezone import make_aware, now
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.contrib.postgres.aggregates import ArrayAgg
from booking.models import BookingSlot
from my_app.models import Item, District, Upazilla, Service
from shop_profile.models import ShopGallery, ShopWorker, ShopService, ShopNotification, ShopSchedule, ShopReview
from user_profile.models import UserProfile
from datetime import datetime, timedelta
from django.core.paginator import Paginator

# Constants
BOOKING_NOT_FOUND = "Booking not found."
DAYS_IN_PAST = 15
HOURS_OFFSET = 6
CANCEL_HOURS_LIMIT = 30
SHOP_STAFFS = "shop_staffs"

def get_shop_from_user(user):
    """Retrieve shop profile from user."""
    return user.shop_profile

def get_response_data(shop, days=DAYS_IN_PAST):
    """Generate response data for the past n days."""
    return [
        {
            "date": (datetime.now() - timedelta(days=i)).strftime("%d %b"),
            "value": BookingSlot.objects.filter(
                shop=shop,
                status='completed',
                date=(datetime.now() - timedelta(days=i)).date()
            ).count()
        }
        for i in range(days - 1, -1, -1)
    ]

def get_monthly_data(shop, year):
    """Calculate monthly revenue data for completed bookings."""
    months = OrderedDict((datetime(2000, m, 1).strftime('%b'), Decimal('0.00')) 
                        for m in range(1, datetime.now().month + 1))
    price_map = {service.item_id: service.price for service in ShopService.objects.filter(shop=shop)}
    
    for booking in BookingSlot.objects.filter(shop=shop, status='completed', date__year=year).select_related('item'):
        month_name = booking.date.strftime('%b')
        months[month_name] += price_map.get(booking.item_id, Decimal('0.00'))
    
    return [{"month": month, "value": float(value)} for month, value in months.items()]

def get_customer_counts(shop):
    """Calculate total and new customer counts."""
    total_customer = BookingSlot.objects.filter(shop=shop, status='completed').count()
    
    start_of_month = now().replace(day=1)
    completed_this_month = BookingSlot.objects.filter(
        shop=shop, status='completed', created_at__gte=start_of_month
    ).values_list('user', flat=True).distinct()
    
    old_customers = BookingSlot.objects.filter(
        shop=shop, status='completed', created_at__lt=start_of_month,
        user__in=completed_this_month
    ).values_list('user', flat=True).distinct()
    
    new_customer = len(set(completed_this_month) - set(old_customers))
    return total_customer, new_customer

def get_review_data(shop):
    """Fetch and format shop reviews."""
    reviews = ShopReview.objects.filter(shop=shop).order_by('-created_at')
    for review in reviews:
        review.reviewer = UserProfile.objects.filter(id=review.reviewer_id).first()
        review.stars = '★' * review.rating
    
    happy_count = reviews.filter(rating__gte=4).count()
    unhappy_count = reviews.filter(rating__lte=3).count()
    average_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    return reviews, happy_count, unhappy_count, average_rating

def get_current_datetime_with_offset(hours=HOURS_OFFSET):
    """Get current datetime with timezone offset in UTC."""
    print("check again")
    updated_time = timezone.now() + timedelta(hours=hours)
    return updated_time

@csrf_protect
@login_required
@require_http_methods(["GET"])
def profile(request):
    shop = get_shop_from_user(request.user)
    context = {
        'response_data': get_response_data(shop),
        'monthly_data': get_monthly_data(shop, now().year),
        'total_customer': get_customer_counts(shop)[0],
        'new_customer': get_customer_counts(shop)[1],
        **dict(zip(['reviews', 'happy_count', 'unhappy_count', 'average_rating'], get_review_data(shop)))
    }
    return render(request, "app/salon_dashboard/index.html", context)

@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def gallery(request):
    shop = get_shop_from_user(request.user)
    message = ""
    
    if request.method == "POST":
        if request.FILES.get("image"):
            ShopGallery.objects.create(shop=shop, image=request.FILES["image"])
            message = "success"
        elif "delete_image" in request.POST:
            image = get_object_or_404(ShopGallery, id=request.POST.get("img_id"), shop=shop)
            image.image.delete()
            image.delete()
    
    images = ShopGallery.objects.filter(shop=shop)
    return render(request, "app/salon_dashboard/saloon-gallery.html", {"image": images, "message": message})

@csrf_protect
@login_required
@require_http_methods(["GET"])
def calender(request):
    month = int(request.GET.get("month", datetime.now().month))
    year = int(request.GET.get("year", datetime.now().year))
    cal = HTMLCalendar().formatmonth(year, month)
    return render(request, "app/salon_dashboard/saloon-calender.html", {"cal": cal, "month": month, "year": year})

@csrf_protect
@login_required
@require_http_methods(["GET"])
def slots(request):
    today = datetime.strptime(request.GET.get("date", date.today().strftime("%Y-%m-%d")), "%Y-%m-%d").date()
    current_datetime = get_current_datetime_with_offset()
    
    shop_worker = [
        {
            "worker": worker,
            "booking_slots": BookingSlot.objects.filter(worker=worker, date=today)
                .exclude(status="canceled")
                .annotate(
                    booking_datetime=ExpressionWrapper(
                        Cast(Concat(Cast(F("date"), CharField()), Value(" "), Cast(F("time"), CharField())), DateTimeField()),
                        output_field=DateTimeField()
                    ),
                    is_expired=Case(
                        When(booking_datetime__lt=current_datetime, then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField()
                    )
                )
        }
        for worker in ShopWorker.objects.filter(shop=get_shop_from_user(request.user))
    ]
    return render(request, "app/salon_dashboard/booking-slots.html", {"shop_worker": shop_worker, "today": current_datetime})

@csrf_protect
@login_required
@require_http_methods(["POST"])
def reject_booking(request):
    data = json.loads(request.body)
    booking_id = data.get("booking_id")
    try:
        booking = BookingSlot.objects.get(id=booking_id)
        #for user only
        shop=booking.shop
        booking_datetime = make_aware(datetime.combine(booking.date, booking.time))
        if booking_datetime - datetime.now().astimezone() < timedelta(hours=CANCEL_HOURS_LIMIT):
            return JsonResponse({"success": False, "message": "Cannot cancel within 24 hours."})
        booking.status = "canceled"
        booking.save()
        # Create a shop notification for the following cancellation
        notification_message = (
            f"Booking canceled!\n"
        )
        ShopNotification.objects.create(
            shop=shop,
            title="New Booking canceled",
            message=notification_message,
            notification_type="cancel"
        )
        return JsonResponse({"success": True, "message": "Booking canceled."})
    except BookingSlot.DoesNotExist:
        return JsonResponse({"success": False, "message": BOOKING_NOT_FOUND})

@csrf_protect
@login_required
@require_http_methods(["POST"])
def booking_details(request):
    data = json.loads(request.body)
    booking_id = data.get("booking_id")
    
    try:
        booking = BookingSlot.objects.get(id=booking_id)
        service = ShopService.objects.get(shop=booking.shop, item=booking.item)
        return JsonResponse({
            "success": True,
            "details": {
                "full_name": f"{booking.user.first_name} {booking.user.last_name}",
                "shop_name": booking.shop.shop_name,
                "worker": booking.worker.name,
                "item_name": booking.item.name,
                "item_price": str(service.price),
                "booked_time": booking.time.strftime("%I:%M %p"),
                "booked_date": booking.date.strftime("%d-%m-%Y"),
                "status": booking.status,
                "booking_time": booking.time.strftime("%I:%M %p")
            }
        })
    except (BookingSlot.DoesNotExist, ShopService.DoesNotExist):
        return JsonResponse({"success": False, "message": BOOKING_NOT_FOUND})

@csrf_protect
@login_required
@require_http_methods(["POST"])
def update_status(request):
    data = json.loads(request.body)
    booking_id = data.get("booking_id")
    
    try:
        booking = BookingSlot.objects.get(id=booking_id)
        booking_datetime = make_aware(datetime.combine(booking.date, booking.time))
        if get_current_datetime_with_offset() > booking_datetime:
            booking.shop_end = True
            booking.save()
            return JsonResponse({"success": True, "details": {"message": "Marked as completed!"}})
        return JsonResponse({"success": False, "message": "Booking time has not yet arrived."})
    except BookingSlot.DoesNotExist:
        return JsonResponse({"success": False, "message": BOOKING_NOT_FOUND})

@csrf_protect
@login_required
@require_http_methods(["GET"])
def message(request):
    return render(request, "app/salon_dashboard/message.html")

@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def staffs(request):
    shop = get_shop_from_user(request.user)
    
    if request.method == "POST":
        try:
            worker = ShopWorker.objects.get(id=request.POST.get("id"))
            worker.name = request.POST.get("name")
            worker.email = request.POST.get("email")
            worker.phone = request.POST.get("phone")
            worker.experience = float(request.POST.get("experience")) 
            expertise_ids = request.POST.getlist("expertise")
            if expertise_ids:
                worker.expertise.set(Item.objects.filter(id__in=expertise_ids))
            if profile_pic := request.FILES.get("profile_pic"):
                if worker.profile_pic:
                    worker.profile_pic.delete(save=False)
                worker.profile_pic = profile_pic
            
            worker.save()
            messages.success(request, "Worker details updated successfully.")
        except (ValueError, TypeError):
            messages.error(request, "Invalid input for experience.")
        except ShopWorker.DoesNotExist:
            messages.error(request, "Worker does not exist.")
    
    return render(request, "app/salon_dashboard/staffs.html", {
        "shop_worker": ShopWorker.objects.filter(shop=shop),
        "items": ShopService.objects.filter(shop=shop)
    })

@csrf_protect
@login_required
@require_http_methods(["POST"])
def add_worker(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        experience = request.POST.get("experience", "0").strip()
        expertise = request.POST.getlist("expertise")
        profile_pic = request.FILES.get("profile_pic")
        
        if not all([name, phone, expertise]):
            messages.error(request, "Name, Mobile, and Expertise are required.")
            return redirect(SHOP_STAFFS)
        
        if email:
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, "Invalid email format.")
                return redirect(SHOP_STAFFS)
        
        try:
            experience = float(experience)
        except ValueError:
            messages.error(request, "Experience must be a number.")
            return redirect(SHOP_STAFFS)
        
        worker = ShopWorker.objects.create(
            name=name, email=email, phone=phone, experience=experience,
            profile_pic=profile_pic, shop=get_shop_from_user(request.user)
        )
        worker.expertise.add(*expertise)
        messages.success(request, "Worker added successfully!")
        return redirect(SHOP_STAFFS)
    
    return render(request, "app/salon_dashboard/staffs.html")

@csrf_protect
@login_required
@require_http_methods(["POST"])
def delete_worker(request):
    if request.method == "POST":
        data = json.loads(request.body)
        worker_id = data.get('id')
        try:
            worker = ShopWorker.objects.get(id=worker_id)
            worker.delete()
            return JsonResponse({'success': True})
        except ShopWorker.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Worker not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@csrf_protect
@login_required
@require_http_methods(["GET"])
def customers(request):
    bookings = BookingSlot.objects.filter(
        shop=get_shop_from_user(request.user)
    ).order_by("-date", "-time")

    paginator = Paginator(bookings, 10)  # Show 10 bookings per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "app/salon_dashboard/customers.html", {
        "bookings": page_obj,
        "page_obj": page_obj,
    })
    
@csrf_protect
@login_required
@require_http_methods(["GET"])
def review(request):
    reviews, _, _, _ = get_review_data(get_shop_from_user(request.user))

    paginator = Paginator(reviews, 10)  # Show 10 reviews per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "app/salon_dashboard/reviews.html", {
        'reviews': page_obj,  # paginated reviews
        'page_obj': page_obj,  # page object for pagination controls
    })

@csrf_protect
@login_required
@require_http_methods(["GET"])
def notification(request):
    notifications = ShopNotification.objects.filter(shop=get_shop_from_user(request.user)).order_by("-created_at")
    return render(request, "app/salon_dashboard/notifications.html", {"notifications": notifications})

@csrf_protect
@login_required
@require_http_methods(["GET"])
def setting(request):
    return render(request, "app/salon_dashboard/settings.html")

@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def basic_update(request):
    shop = get_shop_from_user(request.user)
    user = request.user
    
    if request.method == "POST":
        try:
            for field in ['shop_name', 'shop_title', 'shop_info', 'shop_owner', 'mobile_number', 
                         'shop_website', 'gender', 'shop_state', 'shop_city', 'shop_area']:
                setattr(shop, field, request.POST.get(field, getattr(shop, field)))
            
            for i in range(1, 6):
                setattr(shop, f'shop_landmark_{i}', request.POST.get(f'landmark_{i}', getattr(shop, f'shop_landmark_{i}')))
            
            shop.status = request.POST.get('status', str(shop.status)) == 'true'
            if shop_picture := request.FILES.get('shop_picture'):
                shop.shop_picture = shop_picture
            
            shop.save()
            messages.success(request, "Shop profile updated successfully.")
        except Exception as e:
            messages.error(request, f"Failed to update shop: {str(e)}")
    
    return render(request, "app/salon_dashboard/update_basic.html", {
        'user': user,
        'shop': shop,
        'district': list(District.objects.values('id', 'name')),
        'Upazilla': list(Upazilla.objects.values('district__name').annotate(upazilla_names=ArrayAgg('name')))
    })

@csrf_protect
@login_required
@require_http_methods(["GET"])
def services_update(request):
    return render(request, "app/salon_dashboard/update-services.html", {
        'services': Service.objects.values('id', 'name')
    })

@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def schedule_update(request):
    shop = get_shop_from_user(request.user)
    
    if request.method == "POST":
        for day in ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            start_time = request.POST.get(f"schedule[{day}][start]", "").strip()
            end_time = request.POST.get(f"schedule[{day}][end]", "").strip()
            
            if start_time and end_time and start_time < end_time:
                shop_schedule, _ = ShopSchedule.objects.get_or_create(shop=shop, day_of_week=day)
                shop_schedule.start = start_time
                shop_schedule.end = end_time
                shop_schedule.save()
    
    schedule_dict = {
        s.day_of_week: {'start': s.start.strftime('%H:%M'), 'end': s.end.strftime('%H:%M')}
        for s in ShopSchedule.objects.filter(shop=shop)
    }
    return render(request, 'app/salon_dashboard/update_schedule.html', {
        'days_of_week': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        'schedule_dict': schedule_dict
    })