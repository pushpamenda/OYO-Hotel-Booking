from django.shortcuts import render
from accounts.models import Hotel

# Create your views here.

def index(request):
    hotels = Hotel.objects.all()[:50]

    return render(request,'index.html',context ={'hotels':hotels} )

