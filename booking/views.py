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
    if request.method == 'POST':
        # Retrieve form data
        item_id = request.POST.get('item_id')
        shop_id = request.POST.get('shop_id')
        print("item_id:",item_id)
        shop = ShopProfile.objects.filter(id=shop_id).first()
        service = Item.objects.filter(id=item_id).first()
        print("service",service)
        workers = ShopWorker.objects.filter(shop=shop_id,expertise=item_id)
        print(workers)
        expertise_worker = []
        
    print(service.id)
    print(expertise_worker)
    return render(request, 'app/booking/book-step-1.html',{
        "shop": shop, 
         "service": service,
         "workers": workers, 

    })

@csrf_protect
@require_http_methods(["GET", "POST"])
def booking_step_2(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        shop_id = request.POST.get('shop_id')
        worker_id = request.POST.get('worker_id')
        print("item id",item_id)
        shop = ShopProfile.objects.filter(id=shop_id).first()
        service = Item.objects.filter(id=item_id).first()
        worker = ShopWorker.objects.filter(id=worker_id).first()

    return render(request, 'app/booking/book-step-2.html',{
        "shop": shop, 
         "service": service,
         "worker": worker, 

    })

def available_slots(request):
    
    shop_id = request.GET.get('shop_id')
    worker_id = request.GET.get('worker_id')
    item_id = request.GET.get('item_id')
    date = request.GET.get('date')   

    date_obj = datetime.strptime(date, "%Y-%m-%d")
    day_name = date_obj.strftime("%A")  

    schedule = ShopSchedule.objects.filter(shop=shop_id,day_of_week=day_name)

    time_slot = []
    for day in schedule:
        start_time = day.start
        end_time = day.end

        if date == datetime.today().date():
            now = datetime.now().time()
            if now > start_time:
                # Round up current time to next hour
                rounded_hour = (datetime.now().hour + 1) % 24
                start_time = time(rounded_hour, 0, 0)

        current_time = start_time
        while current_time < end_time:
            time_slot.append(current_time)
            total_seconds = (current_time.hour * 3600 + current_time.minute * 60 + current_time.second) + 3600
            current_time = time(total_seconds // 3600, (total_seconds % 3600) // 60, total_seconds % 60)

    booked = BookingSlot.objects.filter(shop=shop_id, worker=worker_id, date=date).values_list('time', flat=True)
    
    free_slots = [slot for slot in time_slot if slot not in booked]
    
    if not (shop_id and worker_id and item_id and date):
        return JsonResponse({"error": "Missing parameters"}, status=400)
    
    return JsonResponse(list(free_slots), safe=False)

@login_required
def success(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        shop_id = request.POST.get('shop_id')
        worker_id = request.POST.get('worker_id')
        time = request.POST.get('selected_time_id')
        date = request.POST.get('selected_date_id')
        print(item_id, shop_id, worker_id, date,time)
    user=request.user.user_profile
    shop = ShopProfile.objects.filter(id=shop_id).first()
    service=ShopService.objects.filter(shop=shop_id,item=item_id).first()
    worker = ShopWorker.objects.filter(id=worker_id).first()
    if not all([user, shop, worker, service]):
        print("Ensure all related objects exist before creating a BookingSlot.")
    else:
        booking = BookingSlot.objects.create(
            user=user,
            shop=shop,
            worker=worker,
            item=service.item,
            date = date,
            time = time
        )
        print(booking)
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
        print(f"Booking created: {notification_message}")
        print(service.item.id)
    return render(request, 'app/booking/success.html',{
        "shop": shop, 
        "service": service,
        "worker": worker, 
        "time": time,
        "date": date,

    })