from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed
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
    worker=ShopWorker.objects.filter(shop=request.user.shop_profile)
    shop_worker=list(worker.all())
    for worker in shop_worker:
        print(worker.name)
        print(worker.email)
    return render(request,'app/salon_dashboard/staffs.html',{'shop_worker':shop_worker})

def customers(request):
    return render(request,'app/salon_dashboard/customers.html')

def review(request):
    return render(request,'app/salon_dashboard/reviews.html')

def notification(request):
    return render(request,'app/salon_dashboard/notifications.html')

def setting(request):
    return render(request,'app/salon_dashboard/settings.html')
