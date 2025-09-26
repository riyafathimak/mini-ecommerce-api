from django.http import HttpResponse

def home(request):
    return HttpResponse("Hello, World!")
from django.shortcuts import render
from django.contrib.auth.models import User

def user_list(request):
    # Example: filter users whose username contains "riya"
    users = User.objects.filter(username__icontains="riya")
    
    # Example: filter users with a specific email
    # users = User.objects.filter(email="admin1234@gmail.com")
    
    return render(request, 'user_list.html', {'users': users})
