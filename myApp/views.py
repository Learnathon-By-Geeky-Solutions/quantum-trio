from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request, 'app\home.html')


def contact_us(request):
    return render(request, 'app\contact_us.html')


def Service(request):
    return render(request, 'app\service.html')


def bookNow(request):
    return render(request, 'app\book_now.html')


def Location(request):
    return render(request, 'app\location.html')


def exploreByItem(request):
    return render(request, 'app\explore_by_items.html')

#For Salon Profile
def viewSalonProfile(request):
    return render(request, 'app\saloon_profile\dashboard.html')

#For Salon Deshboard
def viewDashBoard(request):
    return render(request, 'app\salon_dashboard\index.html')
