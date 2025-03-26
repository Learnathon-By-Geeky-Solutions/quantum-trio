from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseNotAllowed

from user_profile.models import UserProfile
from django.contrib.auth import get_user_model

@login_required
def profile(request):
    user = request.user  # Get the logged-in user
    
    # Get or create UserProfile
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        retype_password = request.POST.get("retype_password")
        phone_number = request.POST.get("mobile_number")  # Corrected field name
        image = request.FILES.get("image")

        # Update user fields
        user.first_name = first_name
        user.last_name = last_name

        User = get_user_model()
        # Validate email uniqueness
        if User.objects.filter(email=email).exclude(pk=user.pk).exists():
            messages.error(request, "This email is already in use.")
            return render(request, "app/customer_profile/my-profile.html")

        user.email = email

        # Check if passwords match and update
        if password:
            if password == retype_password:
                user.set_password(password)  # Hash and save password
            else:
                messages.error(request, "Passwords do not match.")
                return render(request, "app/customer_profile/my-profile.html")

        user.save()

        # Update profile fields
        profile.phone_number = phone_number
        if image:
            profile.profile_picture = image  # Save uploaded image

        profile.save()

        messages.success(request, "Profile updated successfully. Please log in again if you changed your password.")
        render(request, "app/customer_profile/my-profile.html")
    context = {"user": user, "profile": profile}
    return render(request, "app/customer_profile/my-profile.html", context)





def address(request):
    return render(request,'app/customer_profile/address.html')

# def reviews(request):
#     return render(request,'app/customer_profile/reviews.html')

def addressofbooking(request):
    return render(request,'app/customer_profile/addressofbooking.html')

def myreviews(request):
    return render(request,'app/customer_profile/myreviews.html')

def mybooking(request):
    return render(request,'app/customer_profile/mybooking.html')

def mycancellations(request):
    return render(request,'app/customer_profile/mycancellations.html')

def mynotifications(request):
    return render(request,'app/customer_profile/mynotifications.html')