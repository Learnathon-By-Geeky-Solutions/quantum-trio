import json
from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from datetime import datetime,date
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
# import calendar
from calendar import HTMLCalendar
from booking.models import BookingSlot
from my_app.models import Item
from shop_profile.models import ShopGallery, ShopWorker, ShopService,ShopNotification
user=get_user_model()
def profile(request): 
    return render(request,'app/salon_dashboard/index.html')

def gallery(request):
    message=''
    if request.method =="POST":
        if(request.FILES):
            img=request.FILES.get('image')
            shop=request.user.shop_profile
            gallery=ShopGallery.objects.create(
                shop=shop,
                image=img
            )
            gallery.save()
            message='success'
        if "delete_image" in request.POST:
            img_id = request.POST.get("img_id")
            image = get_object_or_404(ShopGallery, id=img_id, shop=request.user.shop_profile)
            image.image.delete() 
            image.delete() 

    img=ShopGallery.objects.all()
    return render(request,'app/salon_dashboard/saloon-gallery.html',{'image':img,'message':message})

def calender(request):
    month=datetime.now().month
    year=datetime.now().year
    # print(cal)
    if request.method=="GET" and request.GET.get('month') is not None and request.GET.get('year') is not None:
        month=int(request.GET.get('month'))
        year=int(request.GET.get('year'))
    print(month,type(int(year)))
    cal=HTMLCalendar().formatmonth(year,month)
    # print(cal)
    return render(request, 'app/salon_dashboard/saloon-calender.html',{'cal':cal,'month':month,'year':year})
def appointments(request):
    worker=ShopWorker.objects.filter(shop=request.user.shop_profile)
    shop_worker=[]
    for i in worker:
        temp = {
            'worker': i,
            'booking_slots': BookingSlot.objects.filter(worker=i, status="pending").order_by("-created_at")
        }
        shop_worker.append(temp)

    for i in shop_worker:
        print(i['worker'])
        print(i['booking_slots'])
    print(worker)
    return render(request,'app/salon_dashboard/appointments.html',{'shop_worker':shop_worker})

def slots(request):
    today=date.today()
    if request.method=="GET" and request.GET.get('date') is not None:
        today=datetime.strptime(request.GET.get('date'),"%Y-%m-%d")
        # print(type(today))
    print(today)
    worker=ShopWorker.objects.filter(shop=request.user.shop_profile)
    shop_worker=[]
    for i in worker:
        temp = {
            'worker': i,
            'booking_slots': BookingSlot.objects.filter(worker=i, date=today).exclude(Q(status='pending') | Q(status='canceled'))
        }
        shop_worker.append(temp)

    for i in shop_worker:
        print(i['worker'])
        print(i['booking_slots'])
    print(worker)
    return render(request,'app/salon_dashboard/booking-slots.html',{'shop_worker':shop_worker})
"""Accept the booking"""
@csrf_exempt
def accept_booking(request):
    if request.method == "POST":
        data = json.loads(request.body)
        booking_id = data.get("booking_id")
        try:
            booking = BookingSlot.objects.get(id=booking_id)
            booking.status = "confirmed"
            booking.save()
            return JsonResponse({"success": True, "message": "Booking accepted."})
        except BookingSlot.DoesNotExist:
            return JsonResponse({"success": False, "message": "Booking not found."})

"""Reject booking"""
@csrf_exempt
def reject_booking(request):
    if request.method == "POST":
        data = json.loads(request.body)
        booking_id = data.get("booking_id")
        try:
            booking = BookingSlot.objects.get(id=booking_id)
            booking.status = "rejected"
            booking.save()
            return JsonResponse({"success": True, "message": "Booking rejected."})
        except BookingSlot.DoesNotExist:
            return JsonResponse({"success": False, "message": "Booking not found."})

"""retrieval of booking-details of a booking"""
@csrf_exempt 
def booking_details(request):
    if request.method == "POST":
        data = json.loads(request.body)
        booking_id = data.get("booking_id")
        try:
            booking = BookingSlot.objects.get(id=booking_id)
            price=ShopService.objects.get(shop=booking.shop,item=booking.item)
            return JsonResponse({
                "success": True,
                "details": {
                    "full_name": booking.user.first_name,
                    "item_name": booking.item.name,
                    "item_price": str(price),
                    "booked_time": booking.time.strftime("%I:%M %p"),
                    "booked_date": booking.date.strftime("%d-%m-%Y"),
                    "status": booking.status,
                    "booking_time": booking.time.strftime("%I:%M %p")
                }
            })
        except BookingSlot.DoesNotExist:
            return JsonResponse({"success": False, "message": "Booking not found."})

def message(request):
    return render(request,'app/salon_dashboard/message.html')

def staffs(request):
    if request.method == "POST":
        worker_id = request.POST.get('id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        experience = request.POST.get('experience')
        expertise_ids = request.POST.getlist('expertise') 
        profile_pic = request.FILES.get('profile_pic')
        """ Fetch expertise items in one query """
        expertise_items = Item.objects.filter(id__in=expertise_ids) 
        try:
            worker = ShopWorker.objects.get(id=worker_id)
            worker.name = name
            worker.email = email
            worker.phone = phone
            worker.experience = experience
            if expertise_items.exists():  # Only update if there are valid expertise items
                worker.expertise.set(expertise_items)
            if profile_pic:  # Only update profile_pic if a new file is uploaded delete first then upload
                if worker.profile_pic:  
                    worker.profile_pic.delete(save=False)
                worker.profile_pic = profile_pic
            worker.save()
            return JsonResponse({"message": "Worker updated successfully"}, status=200)

        except ShopWorker.DoesNotExist:
            return JsonResponse({"error": "Worker not found"}, status=404)

    workers = ShopWorker.objects.filter(shop=request.user.shop_profile)
    items = ShopService.objects.filter(shop=request.user.shop_profile)

    return render(request, 'app/salon_dashboard/staffs.html', {
        'shop_worker': workers,
        'items': items
    })
def add_worker(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        experience = request.POST.get("experience", "0").strip()
        expertise = request.POST.getlist("expertise")  # Multiple selections
        profile_pic = request.FILES.get("profile_pic")

        # Validate inputs
        if not name or not phone or not expertise:
            messages.error(request, "Name, Mobile, and Expertise are required.")
            return redirect("add_worker")
        if email:
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, "Invalid email format.")
                return redirect("add_worker")

        # Convert experience to an integer safely
        try:
            experience = int(float(experience))  # Handles decimal input
        except ValueError:
            messages.error(request, "Experience must be a number.")
            return redirect("add_worker")
        worker = ShopWorker.objects.create(
            name=name,
            email=email,
            phone=phone,
            experience=experience,
            profile_pic=profile_pic,
            shop= request.user.shop_profile
        )
        worker.expertise.add(*expertise)
        messages.success(request, "Worker added successfully!")
        return redirect("shop_staffs") 
    return render(request, "staffs")

def customers(request):
    return render(request,'app/salon_dashboard/customers.html')

def review(request):
    return render(request,'app/salon_dashboard/reviews.html')

def notification(request):
    notification=ShopNotification.objects.filter(shop=request.user.shop_profile).order_by('-created_at')
    return render(request,'app/salon_dashboard/notifications.html',{'notifications':notification})

def setting(request):
    return render(request,'app/salon_dashboard/settings.html') 

def basic_update(request):
    return render(request, 'app/salon_dashboard/update_basic.html')

def schedule_update(request):
    days_of_week = ['Saturday', 'Sunday','Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    return render(request, 'app/salon_dashboard/update_schedule.html',{'days_of_week':days_of_week})
