from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from booking.models import BookingSlot
from shop_profile.models import ShopProfile, ShopSchedule, ShopWorker, ShopService, ShopNotification
from my_app.models import Item
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

# --- Helper Functions ---

def get_object_or_none(model, **kwargs):
    return model.objects.filter(**kwargs).first()

def validate_post_params(request, params):
    return all(request.POST.get(param) for param in params)

def validate_get_params(request, params):
    return all(request.GET.get(param) for param in params)

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date(), None
    except ValueError:
        return None, JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

def adjust_start_time(start_time, date_obj):
    if date_obj == datetime.today().date():
        now = datetime.now().time()
        if now > start_time:
            rounded_hour = (datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)).time()
            return max(start_time, rounded_hour)
    return start_time

def generate_time_slots(start_time, end_time, date_obj):
    slots = []
    current_time = datetime.combine(date_obj, start_time)
    end_datetime = datetime.combine(date_obj, end_time)
    while current_time + timedelta(hours=1) <= end_datetime:
        slots.append(current_time.time())
        current_time += timedelta(hours=1)
    return slots

def get_available_time_slots(shop_id, worker_id, date_obj):
    day_name = date_obj.strftime("%A")
    schedule = ShopSchedule.objects.filter(shop=shop_id, day_of_week=day_name)

    time_slots = []
    for day in schedule:
        adjusted_start = adjust_start_time(day.start, date_obj)
        time_slots.extend(generate_time_slots(adjusted_start, day.end, date_obj))

    booked = BookingSlot.objects.filter(
        shop=shop_id, worker=worker_id, date=date_obj, status="pending"
    ).values_list('time', flat=True)

    return [slot.strftime("%H:%M") for slot in time_slots if slot not in booked]

def create_booking_and_notify(user, shop, service, worker, date, time):
    booking = BookingSlot.objects.create(
        user=user, shop=shop, worker=worker, item=service.item, date=date, time=time
    )
    ShopNotification.objects.create(
        shop=shop,
        title="New Booking Alert",
        message=(
            f"New booking received!\nCustomer: {user}\nService: {service.item.name}\n"
            f"Worker: {worker}\nDate: {date}\nTime: {time}\nStatus: Pending"
        ),
        notification_type="booking"
    )
    return booking

# --- Views ---

@csrf_protect
@require_http_methods(["GET", "POST"])
def booking_step_1(request):
    context = {"shop": None, "service": None, "workers": None}

    if request.method == 'POST' and validate_post_params(request, ['item_id', 'shop_id']):
        shop_id = request.POST['shop_id']
        item_id = request.POST['item_id']

        context["shop"] = get_object_or_none(ShopProfile, id=shop_id)
        context["service"] = get_object_or_none(Item, id=item_id)

        if context["shop"] and context["service"]:
            context["workers"] = ShopWorker.objects.filter(shop=shop_id, expertise=item_id)

    return render(request, 'app/booking/book-step-1.html', context)

@csrf_protect
@require_http_methods(["GET", "POST"])
def booking_step_2(request):
    context = {"shop": None, "service": None, "worker": None}

    if request.method == 'POST' and validate_post_params(request, ['item_id', 'shop_id', 'worker_id']):
        context["shop"] = get_object_or_none(ShopProfile, id=request.POST['shop_id'])
        context["service"] = get_object_or_none(Item, id=request.POST['item_id'])
        context["worker"] = get_object_or_none(ShopWorker, id=request.POST['worker_id'])

    return render(request, 'app/booking/book-step-2.html', context)

@require_http_methods(["GET", "POST"])
def available_slots(request):
    required_params = ['shop_id', 'worker_id', 'item_id', 'date']
    if not validate_get_params(request, required_params):
        return JsonResponse({"error": "Missing parameters"}, status=400)

    date_obj, error = parse_date(request.GET['date'])
    if error:
        return error

    slots = get_available_time_slots(
        request.GET['shop_id'], request.GET['worker_id'], date_obj
    )
    return JsonResponse(slots, safe=False)

@login_required
def success(request):
    context = {"shop": None, "service": None, "worker": None, "time": None, "date": None}

    if request.method == 'POST' and validate_post_params(request, ['item_id', 'shop_id', 'worker_id', 'selected_time_id', 'selected_date_id']):
        item_id = request.POST['item_id']
        shop_id = request.POST['shop_id']
        worker_id = request.POST['worker_id']
        time = request.POST['selected_time_id']
        date = request.POST['selected_date_id']

        user = getattr(request.user, 'user_profile', None)
        shop = get_object_or_none(ShopProfile, id=shop_id)
        service = get_object_or_none(ShopService, shop=shop_id, item=item_id)
        worker = get_object_or_none(ShopWorker, id=worker_id)

        if all([user, shop, service, worker, date, time]):
            create_booking_and_notify(user, shop, service, worker, date, time)

        context.update({
            "shop": shop,
            "service": service,
            "worker": worker,
            "time": time,
            "date": date,
        })

    return render(request, 'app/booking/success.html', context)
