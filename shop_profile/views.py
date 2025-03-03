from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed
from .views import *
# Create your views here.

def shop_profile(request):
    if request.method=='GET':
        id=1
        id=request.GET.get('shop_id')
        return render(id)
    return HttpResponseNotAllowed('Not allowed')