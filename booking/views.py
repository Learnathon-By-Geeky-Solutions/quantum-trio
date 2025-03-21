from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from booking.models import BookingSlot
from shop_profile.models import ShopProfile, ShopWorker, ShopService
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
        service = ShopService.objects.filter(shop=shop_id, item_id=item_id).first()

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
        service = ShopService.objects.filter(shop=shop_id, item_id=item_id).first()

        worker = ShopWorker.objects.filter(shop=shop_id).first()

        print("worker name : ", worker.name)

    
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

    if not (shop_id and worker_id and item_id and date):
        return JsonResponse({"error": "Missing parameters"}, status=400)

    slots = BookingSlot.objects.filter(shop_id=shop_id, worker_id=worker_id, item_id=item_id, date=date).values_list('time', flat=True)
    
    return JsonResponse(list(slots), safe=False)