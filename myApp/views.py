from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request, 'app\home.html')


def contact_us(request):
    return render(request, 'app\contact_us.html')

def search(request):
    if request.method == 'POST':
        query = request.POST.get('search', '')  # Retrieve the 'search' parameter from POST data
        if query:
            # Perform your search logic here (e.g., filter database records)
            # For demonstration purposes, let's return the query
            return HttpResponse(f"Search results for: {query}")
        else:
            return HttpResponse("No search query provided.")
    else:
        # If the request is not POST, return a form or an error message
        return HttpResponse("Invalid request method. Please use the search form.")

def service(request):
    return render(request, 'app\service.html')


def book_now(request):
    if request.method == 'GET':
        return render(request, 'app/book_now.html')
    else:
        return HttpResponseNotAllowed(['GET'])


def location(request):
    return render(request, 'app\location.html')


def explore_by_item(request):
    return render(request, 'app\explore_by_items.html')

#For Salon Profile
def view_salon_profile(request):
    return render(request, 'app\saloon_profile\dashboard.html')

#For Salon Deshboard
def view_dash_board(request):
    return render(request, 'app\salon_dashboard\index.html')
