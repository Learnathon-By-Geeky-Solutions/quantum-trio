from datetime import datetime, time, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from booking.models import BookingSlot
from shop_profile.models import ShopProfile, ShopSchedule, ShopWorker, ShopService
from django.views.decorators.csrf import csrf_protect

# Create your views here.
@csrf_protect
@require_http_methods(["GET", "POST"])
def booking_step_1(request):
    if request.method == 'POST':
        # Retrieve form data
        item_id = request.POST.get('item_id')
        shop_id = request.POST.get('shop_id')

        shop = ShopProfile.objects.filter(id=shop_id).first()
        service = ShopService.objects.filter(shop=shop_id, id=item_id).first()

        workers = ShopWorker.objects.filter(shop=shop_id)
        expertise_worker = []
        for worker in workers:
            
            #if worker.expertise.filter(name=service.item.name).exists():
            for expertise in worker.expertise.all():
                if expertise.name == service.item.name:
                    expertise_worker.append(worker)

    return render(request, 'app/booking/book-step-1.html',{
        "shop": shop, 
         "service": service,
         "workers": expertise_worker, 

    })

@csrf_protect
@require_http_methods(["GET", "POST"])
def booking_step_2(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        shop_id = request.POST.get('shop_id')
        worker_id = request.POST.get('worker_id')

        shop = ShopProfile.objects.filter(id=shop_id).first()
        service = ShopService.objects.filter(shop=shop_id, id=item_id).first()
        worker = ShopWorker.objects.filter(shop=shop_id,id=worker_id).first()

    
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



def success(request):
    item_id = request.POST.get('item_id')
    shop_id = request.POST.get('shop_id')
    worker_id = request.POST.get('worker_id')
    time = request.POST.get('selected_time_id')
    date = request.POST.get('selected_date_id')

    print(item_id, shop_id, worker_id, date,time)

    shop = ShopProfile.objects.filter(id=shop_id).first()
    service = ShopService.objects.filter(shop=shop_id, id=item_id).first()
    worker = ShopWorker.objects.filter(shop=shop_id,id=worker_id).first()

    print(service.item)

    return render(request, 'app/booking/success.html',{
        "shop": shop, 
         "service": service,
         "worker": worker, 
            "time": time,
            "date": date,

    })