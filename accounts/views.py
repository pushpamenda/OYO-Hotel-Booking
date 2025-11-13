from django.shortcuts import render,redirect,HttpResponse
from .models import HotelUser
from django.db.models import Q
from django.contrib import messages
from .utils import generateRandomToken,sendEmailToken
from django.contrib.auth import authenticate, login, logout


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
    try:
        hotel_user = HotelUser.objects.get(email_token=token)
        hotel_user.is_verified = True
        hotel_user.save()
        messages.success(request, "Email verified")
        return redirect('login_page')
    except HotelUser.DoesNotExist:
        return HttpResponse("Invalid Token")