from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed
# Create your views here.

<<<<<<< HEAD
def profile(request): 
    return render(request,'app/salon_dashboard/index.html')

def gallery(request):
    return render(request,'app/salon_dashboard/saloon-gallery.html')

def calender(request):
    return render(request,'app/salon_dashboard/saloon-calender.html')

def slots(request):
    return render(request,'app/salon_dashboard/booking-slots.html')

def message(request):
    return render(request,'app/salon_dashboard/message.html')

def staffs(request):
    return render(request,'app/salon_dashboard/staffs.html')

def customers(request):
    return render(request,'app/salon_dashboard/customers.html')

def review(request):
    return render(request,'app/salon_dashboard/reviews.html')

def notification(request):
    return render(request,'app/salon_dashboard/notifications.html')

def setting(request):
    return render(request,'app/salon_dashboard/settings.html')
=======
def shop_profile(request):
    if request.method=='GET':
        sid=1
        sid=request.GET.get('shop_id')
        return render(sid)
    return HttpResponseNotAllowed('Not allowed')
>>>>>>> 5084102af61e549db1c6eab32416096d9ea2ac2a
