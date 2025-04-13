from PIL import Image
from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_POST
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from io import BytesIO
from django.conf import settings


# use this to import any data from database
# -----------------------------------------
from my_app.models import District, Division, Service, Item, Upazilla, Area, Landmark
from shop_profile.models import MyUser, ShopProfile, ShopWorker, ShopService, ShopSchedule
from user_profile.models import UserProfile    
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.auth import get_user_model
temp_user=get_user_model()


# Create your views here.
def select_user_type(request):
    return render(request, 'app/login_signup/sign-up.html')

# Customer A/c registration steps starts here
# -------------------------------------------
def customer_register_step1(request):
    message = ''
    return render(request, 'app/login_signup/register/customer/step1.html',{'message':message})

def customer_register_step2(request):
    district = District.objects.all().values('id', 'name')
    upazilla = Upazilla.objects.values('district__name').annotate(upazilla_names=ArrayAgg('name'))
    
    if request.method == "POST":
        
        """email check logic 
        since password will be validate in frontend so we just need to check does the email exist or not"""
        if temp_user.objects.filter(email__iexact=request.POST.get("email")).exists():
            message='The email exist.'
            return render(request, 'app/login_signup/register/business/step1.html',{'message':message})
        request.session["user"] = {
            'first-name': request.POST.get("first-name", ""),
            'last-name': request.POST.get("last-name", ""),
            'email': request.POST.get("email", ""),
            'password': make_password(request.POST.get("password", "")),
            'mobile-number': request.POST.get("mobile-number", ""),
            'gender':request.POST.get("gender", "Male"),
        }
        
    return render(request, 'app/login_signup/register/customer/step2.html',{'district':list(district),'Upazilla':list(upazilla)})

@require_POST
def customer_submit(request):
    if request.method == 'POST':
        try:
            user_details = request.session.get('user')  # Use `.get()` to avoid KeyError
            if not user_details:
                raise ValueError("User session details are missing.")
            
            user = MyUser(
                email=user_details['email'],
                password=user_details['password'],
                user_type='user',
            )
            # user.set_password(user_details['password'])  # Hash password
            user.save()

            try:
                user_profile = UserProfile.objects.create(
                    user=user,
                    first_name=user_details.get('first-name', ''),  # Use `.get()` for safety
                    last_name=user_details.get('last-name', ''),
                    gender=user_details.get('gender', ''),
                    phone_number=user_details.get('mobile-number', ''),
                    user_state=request.POST.get('district', ''),
                    user_city=request.POST.get('upazilla', ''),
                    user_area=request.POST.get('area', ''),
                    latitude=request.POST.get('latitude', None),
                    longitude=request.POST.get('longitude', None),
                )
                user_profile.save()
                request.session.flush()   #pbkdf2_sha256$870000$P6dgX7e0bRUMDUFZbpcEtH$J7fMWHJjEOJ6GeOaORDNiTNVFr7vcii7upyF22QNSQc=
                return redirect("/login") #pbkdf2_sha256$870000$35UjOIAoGl9Krej9H8I2o3$2H9QJSJakSofxjA2ZomkBZwr3QdRaO9QTxXBnvGMXfU=
            except Exception as e:        #pbkdf2_sha256$870000$rWApXZtm7Pm9phSO05hkP9$0huOR0W/qmiUQJE/lWnLer1cJ4NILqMLuP2imScBRng=
                print(f"Error creating user profile: {e}")
        except Exception as e:
            print(f"Error creating user: {e}")
    return HttpResponse("Failed")
# Business A/c registration steps starts here
# -------------------------------------------
@csrf_protect
@require_http_methods(["GET", "POST"])
def business_register_step1(request):
    message=''
    return render(request, 'app/login_signup/register/business/step1.html',{'message':message})

@csrf_protect
@require_http_methods(["GET", "POST"])
def business_register_step2(request):
    
    if request.method == "POST":
        
        """email check logic 
        since password will be validate in frontend so we just need to check does the email exist or not"""
        if temp_user.objects.filter(email__iexact=request.POST.get("email")).exists():
            message='The email exist.'
            return render(request, 'app/login_signup/register/business/step1.html',{'message':message})
        request.session["user"] = {
            'first-name': request.POST.get("first-name", ""),
            'last-name': request.POST.get("last-name", ""),
            'email': request.POST.get("email", ""),
            'password': make_password(request.POST.get("password", "")),
            'mobile-number': request.POST.get("mobile-number", ""),
        }
    return render(request, 'app/login_signup/register/business/step2.html')

@csrf_protect
@require_http_methods(["GET", "POST"])
def business_register_step3(request):
    district=District.objects.all().values('id', 'name')
    upazilla=Upazilla.objects.values('district__name').annotate(upazilla_names=ArrayAgg('name'))
    
    if request.method == "POST":
        request.session["user"].update({
            'business_name': request.POST.get("business_name", ""),
            'business_title': request.POST.get("business_title", ""),
            'website': request.POST.get("website", ""),
            'business_info': request.POST.get("business_info", ""),
            'gender': request.POST.get("gender", ""),
        })
        request.session.modified = True #update the session variable
    return render(request, 'app/login_signup/register/business/step3.html',{'district':list(district),'Upazilla':list(upazilla)})

@csrf_protect
@require_http_methods(["GET", "POST"])
def business_register_step4(request):
    if request.method == "POST":
        
        """Retrieves all landmarks as a list"""
        landmarks = request.POST.getlist("landmarks[]") 

        """Now process"""
        landmark1= landmarks[0] if len(landmarks[0]) > 0 else ""
        landmark2= landmarks[1] if len(landmarks[1]) > 0 else ""
        landmark3= landmarks[2] if len(landmarks[2]) > 0 else ""
        landmark4= landmarks[3] if len(landmarks[3]) > 0 else ""
        landmark5= landmarks[4] if len(landmarks[4]) > 0 else ""
        request.session["user"].update({
                'district': request.POST.get("district", ""),
                'upazilla': request.POST.get("upazilla", ""),
                'area': request.POST.get("area", ""),
                'landmark1':landmark1,
                'landmark2':landmark2,
                'landmark3':landmark3,
                'landmark4':landmark4,
                'landmark5':landmark5,
                'latitude':request.POST.get("latitude", ""),
                'longitude':request.POST.get("longitude",""),
        })
        request.session.modified = True  #update the session variable
    service=Service.objects.all().values('id', 'name')
    return render(request, 'app/login_signup/register/business/step4.html',{'services':service})

@csrf_protect
@require_http_methods(["POST"])
def business_register_step5(request):
    """Ensure session key exists to avoid KeyError"""
    user_data = request.session.get("user", {})
    
    """Retrieve services from session if available, else set an empty list"""
    services = user_data.get("services", [])

    if request.method == 'POST':
        services = request.POST.getlist("services[]", [])  # Posts only the IDs of services
        user_data["services"] = services  # Update session data
        request.session["user"] = user_data
        request.session.modified = True

    """Fetch available services"""
    available_services = Item.objects.values('service__id', 'service__name').annotate(service_names=ArrayAgg('name'))

    """Convert IDs to strings for comparison and filter matching services"""
    matching_services = []
    if len(services) > 0:  # Correct way to check non-empty list
        matching_services = [
            service for service in available_services if str(service['service__id']) in services
        ]

    # Debugging (optional)
    """print("Matching Services:", matching_services)
    print("Session Data:", request.session.get("user"))"""
    return render(request, 'app/login_signup/register/business/step5.html', {'services': matching_services})

@csrf_protect
@require_POST
def business_register_step6(request):
    if request.method == "POST":
        items = {key: request.POST.getlist(key) for key in request.POST if key.startswith("items")}
        print(items)
        request.session["user"].update({
                'items':items,
        })
        request.session.modified = True
    return render(request, 'app/login_signup/register/business/step6.html')

@csrf_protect
@require_POST
def business_register_step7(request):
    try:
        user_data = request.session.get("user", {})
        
        """Retrieve members from session if available, else set an empty list"""
        members = user_data.get("members", 1)

        """first get all the details of selected items """
        items=request.session['user']['items']
        item = [name for key, name_list in items.items() if 'name' in key for name in name_list]
    except KeyError as e:
        print(f"KeyError: Missing key in session data - {e}")
        user_data = {}  # Reset user_data if corrupted

    print(item)

    if request.method == 'POST':
        try:
            members_input = request.POST.get('members', '1')
            members = int(members_input)

            # Set a reasonable limit to prevent excessive values
            if members < 1:
                members = 1
            elif members > 10:  # Set max limit (adjust as needed)
                members = 10

            # Update session
            request.session["user"].update({'member': members})
            request.session.modified = True
            print("Updated Members:", members)
        except ValueError as e:
            print(f"ValueError: Invalid members input - {e}")
            members = 1  # Fallback to 1 if invalid input
    print(members,item)
    return render(request, 'app/login_signup/register/business/step7.html', {
        'members': range(int(members)),
        'items': item
    })

@csrf_protect
@require_POST
def business_register_step8(request):
    if request.method=="POST":
        members = {key: request.POST.getlist(key) for key in request.POST if key.startswith("member")}
        worker_image=[]
        for key in request.FILES:
            if key.startswith("member"):
                uploaded_files = request.FILES.getlist(key)  # Get all images for this key
                
                saved_paths = []
                for uploaded_file in uploaded_files:
                    # Define the file path where it will be saved
                    file_path = f"temp/{uploaded_file.name}"
                    full_path = os.path.join(settings.MEDIA_ROOT, file_path)  # Adjust based on MEDIA settings
                    # Save the file
                    default_storage.save(full_path, ContentFile(uploaded_file.read()))

                    # Append the saved file path instead of the file object
                    saved_paths.append(file_path)
                worker_image.append(saved_paths)  # Store the list of file paths

        print(worker_image)
        request.session["user"].update({
                'members':members,
                'worker_image':worker_image,
        })
        request.session.modified = True
    days_of_week = ['Saturday', 'Sunday','Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    return render(request, 'app/login_signup/register/business/step8.html',{'days_of_week':days_of_week})

@csrf_protect
@require_POST
def business_submit(request):
    if(request.method=='POST'):

        """process the schedule first"""
        schedule_data = request.POST  # QueryDict
        schedule = {}
        for day in ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            start_time = schedule_data.get(f"schedule[{day}][start]", "").strip()
            end_time = schedule_data.get(f"schedule[{day}][end]", "").strip()
            # Only save the day if it has valid start or end time
            if start_time or end_time:
                schedule[day] = {"start": start_time, "end": end_time}
        # print("Filtered Schedule:", schedule)  # Debugging output
        
        try:
            user_details=request.session['user']
            try:
                user=temp_user.objects.create(
                    email=user_details['email'],
                    password=user_details['password'],
                    user_type='shop',
                )
                user.save()
                """creating shop profile"""
                shop = ShopProfile.objects.create(
                    user=user,
                    shop_name = user_details['business_name'],
                    shop_title = user_details['business_title'],
                    shop_info = user_details['business_info'],
                    shop_owner = user_details['first-name']+' '+user_details['last-name'],
                    
                    # Contact Information
                    mobile_number = user_details['mobile-number'],
                    shop_website = user_details['website'],
                    # Location Fields (For geolocation)
                    shop_state = user_details['district'],
                    shop_city = user_details['upazilla'],
                    shop_area = user_details['area'],
                    latitude = user_details['latitude'],
                    longitude = user_details['longitude'],
                    shop_landmark_1 = user_details['landmark1'],
                    shop_landmark_2 = user_details['landmark2'],
                    shop_landmark_3 = user_details['landmark3'],
                    shop_landmark_4 = user_details['landmark4'],
                    shop_landmark_5 = user_details['landmark5'],
                )
                """creating worker profile under the shop"""
                try:
                    member_details=user_details['members']
                    worker_image=user_details['worker_image']
                    
                    for index in range(user_details['member']):
                        img_path = os.path.join(settings.BASE_DIR,"media", worker_image[index][0])
                        img=Image.open(img_path)
                        print(img)
                        image_name = img_path.split("/")[-1] 
                        print(image_name)
                        img_io = BytesIO()
                        img.save(img_io, format=img.format)  # Preserve original format (JPEG, PNG, etc.)
                        img_bytes = img_io.getvalue()
                        worker = ShopWorker.objects.create(
                            name = member_details.get(f'member[{index}][name]', [''])[0],
                            email = member_details.get(f'member[{index}][email]', [''])[0],
                            phone = member_details.get(f'member[{index}][contact]', [''])[0],
                            experience = round(float(member_details.get(f'member[{index}][experience]', ['0'])[0])),
                            shop = shop
                        )
                        
                        worker.profile_pic.save(image_name, ContentFile(img_bytes))
                        # # Assign ManyToManyField expertise
                        expertise_values = member_details.get(f'member[{index}][expertise][]', [])
                        selected_expertise = Item.objects.filter(name__in=expertise_values)  # Assuming 'name' is unique
                        worker.expertise.set(selected_expertise)  # Set ManyToMany relationship
                        worker.save()
                except Exception as e:
                    print(f"❌ Error: {e}")

                """inserting the services provided by the shop in ShopService table along with prices"""
                try:
                    items=user_details['items']
                    """How many items the shop provides"""
                    
                    item = [name for key, name_list in items.items() if 'name' in key for name in name_list]
                    print(item)
                    price = [price for key, price_list in items.items() if 'price' in key for price in price_list]
                    print(price)
                    for index in range(len(item)):
                        service=ShopService.objects.create(
                            shop=shop,
                            item=Item.objects.get(name=item[index]),
                            price=price[index]
                        )
                        service.save()
                    
                except Exception as e:
                    print(f"❌ Error: {e}")

                """inserting the shop schedule into the ShopSchedule table"""
                try:
                    print("Filtered Schedule:", schedule)
                    for day, time in schedule.items():
                        print(f"{day}: Start - {time['start']}, End - {time['end']}")
                        shop_schedule=ShopSchedule.objects.create(
                            shop=shop,
                            day_of_week=day,
                            start=time['start'],
                            end=time['end']
                        )
                        shop_schedule.save()

                except Exception as e:
                    print(f"❌ Error: {e}")

            except Exception as e:
                print(f"❌ Error: {e}")

        except KeyError as e:
            HttpResponse("Registered")
    return redirect("/login")