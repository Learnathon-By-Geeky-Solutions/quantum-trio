from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed

def profile(request):
    return render(request,'app/customer_profile/my-profile.html')
def address(request):
    return render(request,'app/customer_profile/address.html')

def reviews(request):
    return render(request,'app/customer_profile/reviews.html')