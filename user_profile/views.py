import json
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseNotAllowed
from my_app.models import District, Upazilla, Area
from booking.models import BookingSlot
from my_app.views import log_out
from user_profile.models import UserProfile
from django.contrib.auth import get_user_model
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.auth import authenticate,login, logout
from django.db.models import ExpressionWrapper, F, Value, CharField, DateTimeField, BooleanField, Case, When
from django.db.models.functions import Cast, Concat
from datetime import datetime
from datetime import datetime, date, timedelta, timezone as tz
from shop_profile.views import booking_details as imported_booking_details, reject_booking as imported_reject_booking
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.views.decorators.http import require_http_methods
MY_PROFILE_TEMPLATE = "app/customer_profile/my-profile.html"
booking_not_found = "Booking not found."

@login_required
@require_http_methods(["GET", "POST"])
def profile(request):
    user = request.user  # Get the logged-in user
    profile= UserProfile.objects.get(user=user)
    check=False
    if request.method == "POST":
        profile.first_name = request.POST.get("first_name")
        profile.last_name = request.POST.get("last_name")
        # update them later
        email = request.POST.get("email")
        password = request.POST.get("password")
        retype_password = request.POST.get("retype_password")
        profile.phone_number = request.POST.get("mobile_number")  # Corrected field name
        image = request.FILES.get("image")
        user_model = get_user_model()
        # Validate email uniqueness
        if user_model.objects.filter(email=email).exclude(pk=user.pk).exists():
            messages.error(request, "This email is already in use.")
            return render(request, MY_PROFILE_TEMPLATE)
        elif email!=user.email:
            user.email=email
            user.save()
            check=True
        # Check if passwords match and update
        if retype_password:
            if password == retype_password:
                user.set_password(password)  # Hash and save password
                user.save()
                check=True
            else:
                messages.error(request, "Passwords do not match.")
                return render(request, MY_PROFILE_TEMPLATE)

        # Update profile fields
        print(image)
        if image:
            profile.profile_picture = image  # Save uploaded image
        profile.save()
        messages.success(request, "Profile updated successfully. Please log in again if you changed your password.")
        render(request, MY_PROFILE_TEMPLATE)
    if check:
        return redirect('logout')
    context = {"user": user, "profile": profile}
    return render(request, MY_PROFILE_TEMPLATE, context)

@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def address(request):
    return render(request,'app/customer_profile/address.html')

@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def reviews(request):
    return render(request,'app/customer_profile/reviews.html')

@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def addressofbooking(request):
    district = District.objects.all().values('id', 'name')
    upazilla = Upazilla.objects.values('district__name').annotate(upazilla_names=ArrayAgg('name'))
    area = Area.objects.values('upazilla__name').annotate(area_names=ArrayAgg('name')) 

    if request.method == 'GET':
        return render(request, 'app/customer_profile/addressofbooking.html',{'district':list(district),'Upazilla':list(upazilla),'Area':area})
    else:
        return HttpResponseNotAllowed(['GET'])
    
@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def myreviews(request):
    return render(request,'app/customer_profile/myreviews.html')

@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def mybooking(request):
    current_datetime = datetime.now()
    booking = BookingSlot.objects.filter(
                    user=request.user.user_profile
                ).exclude(
                    status='canceled'
                ).order_by(
                    '-date', '-time'
                ).annotate(
                    booking_datetime=ExpressionWrapper(
                        Cast(
                            Concat(
                                Cast(F("date"), output_field=CharField()),
                                Value(" "),
                                Cast(F("time"), output_field=CharField())
                            ),
                            output_field=DateTimeField()
                        ),
                        output_field=DateTimeField()
                    ),
                    is_expired=Case(
                        When(booking_datetime__lt=current_datetime, then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField()
                    )
                )
    print(booking)
    return render(request,'app/customer_profile/mybooking.html',{'bookings':booking})

@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def booking_details(request):
    # This is imported from shop_profile view to reuse code
    return imported_booking_details(request)

@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def reject_booking(request):
    # This is imported from shop_profile view to reuse code
    return imported_reject_booking(request)

@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def update_status(request):
    if request.method == "POST":
        data = json.loads(request.body)
        booking_id = data.get("booking_id")
        try:
            booking = BookingSlot.objects.get(id=booking_id)  # Get the booking object
            # Combine the booking date and time
            booking_datetime = datetime.combine(booking.date, booking.time)

            # adding 6 hours for the difference of timezone
            updated_time = timezone.now() + timedelta(hours=6)
            current_time = datetime.strptime(
                updated_time.time().strftime("%H:%M:%S"), "%H:%M:%S"
            ).time()  # for removing the millisecond
            current_date = updated_time.date()
            today = datetime.combine(current_date, current_time)

            # Check if the current time is greater than the booking date and time
            if today > booking_datetime:
                # Only update the status if the current time is after the booked time
                booking.user_end = True
                booking.save()
                return JsonResponse(
                    {
                        "success": True,
                        "details": {
                            "message": "You have successfully marked as completed!"
                        },
                    }
                )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "The booking time has not yet arrived.",
                    }
                )

        except BookingSlot.DoesNotExist:
            return JsonResponse({"success": False, "message": booking_not_found})

@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def mycancellations(request):
    return render(request,'app/customer_profile/mycancellations.html')

@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def mynotifications(request):
    return render(request,'app/customer_profile/mynotifications.html')

@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def mymessage(request):
    return render(request,'app/customer_profile/mymessage.html')