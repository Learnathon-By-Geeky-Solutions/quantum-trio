from datetime import datetime, time, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from booking.models import BookingSlot
from shop_profile.models import ShopProfile, ShopSchedule, ShopWorker, ShopService,ShopNotification
from my_app.models import Item
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
# Create your views here.


@csrf_protect
@require_http_methods(["GET", "POST"])
def booking_step_1(request):
    shop = service = workers = None

    if request.method == 'POST':
        # Retrieve form data
        item_id = request.POST.get('item_id')
        shop_id = request.POST.get('shop_id')
        
        shop = ShopProfile.objects.filter(id=shop_id).first()
        service = Item.objects.filter(id=item_id).first()
        if shop and service:
            workers = ShopWorker.objects.filter(shop=shop_id, expertise=item_id)
              
    return render(request, 'app/booking/book-step-1.html',{
        "shop": shop, 
         "service": service,
         "workers": workers, 

    })

@csrf_protect
@require_http_methods(["GET", "POST"])
def booking_step_2(request):
    shop = service = worker = None  # Default values for GET request

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        shop_id = request.POST.get('shop_id')
        worker_id = request.POST.get('worker_id')

        print("item_id:", item_id)
        print("shop_id:", shop_id)
        print("worker_id:", worker_id)

        if item_id and shop_id and worker_id:
            shop = ShopProfile.objects.filter(id=shop_id).first()
            service = Item.objects.filter(id=item_id).first()
            worker = ShopWorker.objects.filter(id=worker_id).first()

    return render(request, 'app/booking/book-step-2.html', {
        "shop": shop,
        "service": service,
        "worker": worker,
    })
 
@require_http_methods(["GET", "POST"])
def available_slots(request):
    shop_id = request.GET.get('shop_id')
    worker_id = request.GET.get('worker_id')
    item_id = request.GET.get('item_id')
    date_str = request.GET.get('date')

    if not (shop_id and worker_id and item_id and date_str):
        return JsonResponse({"error": "Missing parameters"}, status=400)

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    day_name = date_obj.strftime("%A")
    schedule = ShopSchedule.objects.filter(shop=shop_id, day_of_week=day_name)

    time_slots = []
    for day in schedule:
        start_time = day.start
        end_time = day.end

        # If the selected date is today, skip past hours
        if date_obj == datetime.today().date():
            now = datetime.now().time()
            if now > start_time:
                # Round current time to the next hour
                rounded_hour = (datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)).time()
                start_time = max(start_time, rounded_hour)

        # Generate time slots (1-hour intervals)
        current_time = datetime.combine(date_obj, start_time)
        end_datetime = datetime.combine(date_obj, end_time)
        while current_time + timedelta(hours=1) <= end_datetime:
            time_slots.append(current_time.time())
            current_time += timedelta(hours=1)

    # Get already booked slots
    booked_times = BookingSlot.objects.filter(
        shop=shop_id,
        worker=worker_id,
        date=date_obj
    ).values_list('time', flat=True)

    # Filter out booked times
    free_slots = [slot.strftime("%H:%M") for slot in time_slots if slot not in booked_times]

    return JsonResponse(free_slots, safe=False)

@login_required
def success(request):
    item_id = shop_id = worker_id = time = date = None

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        shop_id = request.POST.get('shop_id')
        worker_id = request.POST.get('worker_id')
        time = request.POST.get('selected_time_id')
        date = request.POST.get('selected_date_id')
        print(item_id, shop_id, worker_id, date, time)

    user = getattr(request.user, 'user_profile', None)
    shop = ShopProfile.objects.filter(id=shop_id).first() if shop_id else None
    service = ShopService.objects.filter(shop=shop_id, item=item_id).first() if shop_id and item_id else None
    worker = ShopWorker.objects.filter(id=worker_id).first() if worker_id else None

    if all([user, shop, worker, service, date, time]):
        booking = BookingSlot.objects.create(
            user=user,
            shop=shop,
            worker=worker,
            item=service.item,
            date=date,
            time=time
        )
        print("Booking created:", booking)

        # Create a shop notification
        notification_message = (
            f"New booking received!\n"
            f"Customer: {user}\n"
            f"Service: {service.item.name}\n"
            f"Worker: {worker}\n"
            f"Date: {date}\n"
            f"Time: {time}\n"
            f"Status: Pending"
        )
        ShopNotification.objects.create(
            shop=shop,
            title="New Booking Alert",
            message=notification_message,
            notification_type="booking"
        )
        print("Notification sent.")
    else:
        print("Ensure all related objects exist before creating a BookingSlot.")

    return render(request, 'app/booking/success.html', {
        "shop": shop,
        "service": service,
        "worker": worker,
        "time": time,
        "date": date,
    })