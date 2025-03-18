from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed

def profile(request):
    return render(request,'app/user_profile/my_profile.html')
def address(request):
    return render(request,'app/user_profile/address.html')

def reviews(request):
    return render(request,'app/user_profile/reviews.html')
    