from django.shortcuts import render,redirect
from .models import HotelUser,HotelVendor,Hotel,Ameneties,HotelImages
from django.db.models import Q
from django.contrib import messages
from .utils import generateRandomToken,sendEmailToken ,sendOTPtoEmail ,generateSlug
from django.contrib.auth import authenticate, login
import random
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required



# Create your views here.
def login_page(request):    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        hotel_user = HotelUser.objects.filter(email = email)

        if not hotel_user.exists():
            messages.warning(request, "No Account Found.")
            return redirect('login_page')

        if not hotel_user[0].is_verified:
            messages.warning(request, "Account not verified")
            return redirect('login_page')

        hotel_user = authenticate(username = hotel_user[0].username , password=password)

        if hotel_user:
            messages.success(request, "Login Success")
            login(request , hotel_user)
            return redirect('login_page')

        messages.warning(request, "Invalid credentials")
        return redirect('login_page')
    return render(request, 'login.html')

def register_page(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')

        hotel_user = HotelUser.objects.filter(
            Q(email = email ) | Q(phone_number = phone_number)
        )

        if hotel_user.exists():
           messages.error(request,"Accounts exists with Email or phone number")
           return redirect('register_page')
        
        hotel_user = HotelUser.objects.create(
            username = phone_number,
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone_number = phone_number,
            email_token = generateRandomToken()
        )
        hotel_user.set_password(password)
        hotel_user.save()

        sendEmailToken(email , hotel_user.email_token)

        messages.success(request, "An email Sent to your Email")
        return redirect('register_page')
                  
    return render(request,'register.html')


def verify_email_token(request, token):
    from .models import HotelUser, HotelVendor

    user = None
    user_type = None

    # Check in HotelUser
    try:
        user = HotelUser.objects.get(email_token=token)
        user_type = "user"
    except HotelUser.DoesNotExist:
        pass

    # Check in HotelVendor if not found
    if user is None:
        try:
            user = HotelVendor.objects.get(email_token=token)
            user_type = "vendor"
        except HotelVendor.DoesNotExist:
            user = None

    # Verify the user if found
    if user is not None:
        user.is_verified = True
        user.save()

        messages.success(request, "Email verified successfully!")

        # Redirect based on user type
        if user_type == "vendor":
            return redirect('login_vendor')  # vendor login page
        else:
            return redirect('login_page')  # normal user login page

    return HttpResponse("Invalid Token")

    
def send_otp(request, email):
    hotel_user = HotelUser.objects.filter(email = email)
    if not hotel_user.exists():
        messages.warning(request,"No Accounts found")
        return redirect('/accounts/login/')
    
    otp = random.randint(1000,9999)
    hotel_user.update(otp = otp)  
    sendOTPtoEmail(email,otp)

    return redirect(f'/accounts/verify_otp/{email}/')

def verify_otp(request, email):
    if request.method == "POST":
        otp = request.POST.get('otp')
        hotel_user = HotelUser.objects.get(email = email)

        if otp == hotel_user.otp:
            messages.success(request, "Login Success")
            login(request , hotel_user)
            return redirect('/accounts/login/')
            
        
        messages.warning(request, "Wrong OTP")
        return redirect(f'/accounts/verify_otp/{email}/')
    
    return render(request, 'verify_otp.html')


def login_vendor(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')

        #  Find vendor by email (case-insensitive)
        hotel_user = HotelVendor.objects.filter(email__iexact=email).first()

        if not hotel_user:
            messages.warning(request, "No Account Found.")
            return redirect('/accounts/login_vendor/')
        
        #  Check if account is verified
        if not hotel_user.is_verified:
            messages.warning(request, "Your account is not verified yet. Please check your email.")
            return redirect('/accounts/login_vendor/')

        #  Authenticate using username, not email
        user = authenticate(username=hotel_user.username, password=password)

        if user:
            login(request, user)
            messages.success(request, "Login Successful!")
            return redirect('/accounts/vendor_dashboard/')
        else:
            messages.warning(request, "Invalid Password.")
            return redirect('/accounts/login_vendor/')

    #  GET request → render login page
    return render(request, 'vendor/login_vendor.html')


def register_vendor(request):
    if request.method == "POST":

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        business_name = request.POST.get('business_name')

        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        hotel_user = HotelUser.objects.filter(Q(email = email) | Q(phone_number  = phone_number))

        if hotel_user.exists():
            messages.warning(request, "Account exists with Email or Phone Number.")
            return redirect('/accounts/register_vendor/')
        
        hotel_user = HotelVendor.objects.create(
            username = phone_number,
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone_number = phone_number,
            business_name = business_name,
            email_token = generateRandomToken()
        )
        hotel_user.set_password(password)
        hotel_user.save()

        sendEmailToken(email , hotel_user.email_token)

        messages.success(request, "An email Sent to your Email")
        return redirect('/accounts/register_vendor/')


    return render(request, 'vendor/register_vendor.html')

@login_required(login_url='login_vendor')
def vendor_dashboard(request):
    # Retrieve hotels owned by the current vendor
    hotels = Hotel.objects.filter(hotel_owner=request.user)
    context = {'hotels': hotels}
    return render(request, 'vendor/vendor_dashboard.html', context)

@login_required(login_url='login_vendor')
def add_hotels(request):
    if request.method == "POST":
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        ameneties= request.POST.getlist('ameneties')
        hotel_price= request.POST.get('hotel_price')
        hotel_offer_price= request.POST.get('hotel_offer_price')
        hotel_location= request.POST.get('hotel_location')
        hotel_slug = generateSlug(hotel_name)

        hotel_vendor = HotelVendor.objects.get(id = request.user.id)
        
        hotel_obj = Hotel.objects.create(
            hotel_name = hotel_name,
            hotel_description = hotel_description,
            hotel_price = hotel_price,
            hotel_offer_price = hotel_offer_price,
            hotel_location = hotel_location,
            hotel_slug = hotel_slug,
            hotel_owner = hotel_vendor
        )

        for ameneti in ameneties:
            ameneti = Ameneties.objects.get(id = ameneti)
            hotel_obj.ameneties.add(ameneti)
            hotel_obj.save()

        messages.success(request, "Hotel Created")
        return redirect('/accounts/add_hotels')


    ameneties = Ameneties.objects.all()

    return render(request, 'vendor/add_hotels.html', context = {'ameneties' : ameneties})

@login_required(login_url='login_vendor')
def upload_images(request, slug):
    hotel_obj = Hotel.objects.get(hotel_slug = slug)
    if request.method == "POST":
        image = request.FILES['image']
        print(image)
        HotelImages.objects.create(
        hotel = hotel_obj,
        image = image
        )
        return HttpResponseRedirect(request.path_info)

    return render(request, 'vendor/upload_images.html', context = {'images' : hotel_obj.hotel_images.all()})

@login_required(login_url='login_vendor')
def delete_image(request, id):
    print(id)
    print("#######")
    hotel_image = HotelImages.objects.get(id = id)
    hotel_image.delete()
    messages.success(request, "Hotel Image deleted")
    return redirect('/accounts/vendor_dashboard/')