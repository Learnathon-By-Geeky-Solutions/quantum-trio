from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from registration.forms import Step1Form, Step2Form, Step3Form
from shop_profile.models import MyUser, ShopProfile
from user_profile.models import UserProfile
from my_app.models import District, Upazilla
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib import messages

def select_user_type(request):
    return render(request, 'app/login_signup/sign-up.html')

def customer_register_step1(request):
    message = ''
    if request.method == 'POST':
        form = Step1Form(request.POST)
        if form.is_valid():
            request.session['step1_data'] = form.cleaned_data
            return redirect('customer_register_step2')
    else:
        form = Step1Form()
    
    return render(request, 'app/login_signup/register/customer/step1.html', {
        'form': form,
        'message': message
    })

def customer_register_step2(request):
    if 'step1_data' not in request.session:
        return redirect('customer_register_step1')

    district = District.objects.all().values('id', 'name')
    upazilla = Upazilla.objects.values('district__name').annotate(upazilla_names=ArrayAgg('name'))
    upazilla_names = []
    for u in upazilla:
        upazilla_names.extend(u['upazilla_names'])
    
    if request.method == 'POST':
        form = Step3Form(request.POST,user_type='customer', districts=district, upazillas=upazilla_names)
        if form.is_valid():
            print('valid')
            user_details = request.session['step1_data']
            try:
                user = MyUser.objects.create_user(
                    email=user_details['email'],
                    password=user_details['password'],
                    user_type='user'
                )
                user.save()
                
                UserProfile.objects.create(
                    user=user,
                    first_name=user_details.get('first_name', ''),
                    last_name=user_details.get('last_name', ''),
                    gender=user_details.get('gender', ''),
                    phone_number=f"+880{user_details.get('mobile_number', '')}",
                    user_state=form.cleaned_data['district'],
                    user_city=form.cleaned_data['upazilla'],
                    user_area=form.cleaned_data['area'],
                    latitude=form.cleaned_data['latitude'],
                    longitude=form.cleaned_data['longitude']
                )
                messages.success(request,"You have successfully created account.")
                request.session.flush()
                return redirect('login')  # Adjust if LOGIN_URL is different
            except Exception as e:
                print(f"Error creating user or profile: {e}")
                return HttpResponse("Failed")
    else:
        form = Step3Form(user_type='customer',districts=district, upazillas=upazilla_names)
    
    return render(request, 'app/login_signup/register/customer/step2.html', {
        'form': form,
        'district': list(district),
        'Upazilla': list(upazilla)
    })

@require_POST
def customer_submit(request):
    return customer_register_step2(request)

# Business registration views (unchanged)
def business_register_step1(request):
    if request.method == 'POST':
        print('check')
        form = Step1Form(request.POST)
        if form.is_valid():
            print('check')
            request.session['step1_data'] = form.cleaned_data
            return redirect('business_register_step2')
    else:
        form = Step1Form()
    
    return render(request, 'app/login_signup/register/business/step1.html', {'form': form})

def business_register_step2(request):
    if 'step1_data' not in request.session:
        return redirect('business_register_step1')
    
    if request.method == 'POST':
        form = Step2Form(request.POST)
        if form.is_valid():
            request.session['step2_data'] = form.cleaned_data
            return redirect('business_register_step3')
    else:
        form = Step2Form()
    
    return render(request, 'app/login_signup/register/business/step2.html', {'form': form})

def business_register_step3(request):
    if 'step1_data' not in request.session or 'step2_data' not in request.session:
        return redirect('business_register_step1')
    
    district = District.objects.all().values('id', 'name')
    upazilla = Upazilla.objects.values('district__name').annotate(upazilla_names=ArrayAgg('name'))
    upazilla_names = []
    for u in upazilla:
        upazilla_names.extend(u['upazilla_names'])
    
    if request.method == 'POST':
        form = Step3Form(request.POST, districts=district, upazillas=upazilla_names)
        if form.is_valid():
            step1_data = request.session['step1_data']
            step2_data = request.session['step2_data']
            step3_data = form.cleaned_data
            
            user = MyUser.objects.create_user(
                email=step1_data['email'],
                password=step1_data['password'],
                user_type='shop'
            )
            user.save()
            
            shop_profile = ShopProfile(
                user=user,
                shop_name=step2_data['business_name'],
                shop_title=step2_data['business_title'],
                shop_info=step2_data['business_info'],
                shop_owner=f"{step1_data['first_name']} {step1_data['last_name']}",
                gender=step2_data['gender'],
                mobile_number=f"+880{step1_data['mobile_number']}",
                shop_website=step2_data['website'],
                shop_state=step3_data['district'],
                shop_city=step3_data['upazilla'],
                shop_area=step3_data['area'],
                latitude=step3_data['latitude'],
                longitude=step3_data['longitude'],
                shop_landmark_1=step3_data['shop_landmark_1'],
                shop_landmark_2=step3_data['shop_landmark_2'],
                shop_landmark_3=step3_data['shop_landmark_3'],
                shop_landmark_4=step3_data['shop_landmark_4'],
                shop_landmark_5=step3_data['shop_landmark_5'],
            )
            shop_profile.save()
            
            del request.session['step1_data']
            del request.session['step2_data']
            
            messages.success(request,"You have successfully created account.")
            request.session.flush()
            return redirect('login')
    else:
        form = Step3Form(user_type='shop',districts=district, upazillas=upazilla_names)
    
    return render(request, 'app/login_signup/register/business/step3.html', {
        'form': form,
        'district': list(district),
        'Upazilla': list(upazilla)
    })