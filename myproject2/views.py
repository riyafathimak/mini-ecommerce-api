from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from tasks.models import Employee

# Get existing user
u = User.objects.get(username="admin")

# Create employee profile linked to that user
Employee.objects.create(user=u, name="Admin", role="Manager")
from .models import Employee

@login_required
def dashboard_page(request):
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        employee = None

    return render(request, 'tasks/dashboard.html', {
        "user": request.user,
        "employee": employee
    })
