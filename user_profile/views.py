from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed

def profile(request):
    return HttpResponse('From user Profile')