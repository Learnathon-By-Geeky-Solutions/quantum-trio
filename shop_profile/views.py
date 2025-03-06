from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed,JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from shop_profile.models import *
import calendar
from datetime import datetime
from django.utils.safestring import mark_safe
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
class CustomHTMLCalendar(calendar.HTMLCalendar):

    def formatday(self, day, weekday, month, year):
        if day == 0:
            return '<td class="bg-gray-200">&nbsp;</td>'  # Empty cell for padding
        
        # Generate the date string
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        
        # Create a link for each date
        return f'''
        <td class="border p-2 text-center">
            <a href="?date={date_str}" class="text-blue-600 hover:text-blue-800">{day}</a>
        </td>
        '''

    def formatmonth(self, year, month):
        cal_html = super().formatmonth(year, month)
        return mark_safe(f'<table class="w-full border-collapse border border-gray-300">{cal_html}</table>')

def calender(request):
    # Get current date
    today = datetime.now()
    
    # Get month and year from GET request, otherwise use current month & year
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    # Create the calendar with clickable dates
    # cal = CustomHTMLCalendar().formatmonth(year, month)
    cal = CustomHTMLCalendar().formatmonth(year, month)
    # Get the selected date from the GET request
    selected_date = request.GET.get('date', None)

    return render(request, 'app/salon_dashboard/salon_calendar.html', {
        'calendar': cal,
        'month': month,
        'year': year,
        'selected_date': selected_date,  # Send the selected date to the template
    })
def slots(request):
    return render(request,'app/salon_dashboard/booking-slots.html')

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

def customers(request):
    return render(request,'app/salon_dashboard/customers.html')

def review(request):
    return render(request,'app/salon_dashboard/reviews.html')

def notification(request):
    return render(request,'app/salon_dashboard/notifications.html')

def setting(request):
    return render(request,'app/salon_dashboard/settings.html')
