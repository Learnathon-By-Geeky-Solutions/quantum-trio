from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed
# Create your views here.

def shop_profile(request):
    if request.method=='GET':
        sid=1
        sid=request.GET.get('shop_id')
        return render(sid)
    return HttpResponseNotAllowed('Not allowed')