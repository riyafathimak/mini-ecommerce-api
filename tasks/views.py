from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from .models import Task, Employee, Comment
from .forms import EmployeeForm, EmployeeSignupForm
from tasks.TaskForm import TaskForm
import json
from .utils import send_task_completion_email
from django.conf import settings
import google.generativeai as genai  # ✅ Gemini import

# =======================
# Authentication
# =======================
def login_page(request):
    error = ''
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            error = 'Invalid username or password'
    return render(request, 'tasks/login.html', {'error': error})


def employee_signup(request):
    if request.method == 'POST':
        form = EmployeeSignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = User.objects.create_user(username=username, password=password)
            employee = form.save(commit=False)
            employee.user = user
            employee.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = EmployeeSignupForm()
    return render(request, 'tasks/employee_signup.html', {'form': form})

# =======================
# Employee Management
# =======================
@login_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'tasks/employee_list.html', {'employees': employees})

@login_required
def employee_add(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'tasks/employee_form.html', {'form': form})

@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'tasks/employee_form.html', {'form': form})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')
    return render(request, 'tasks/employee_confirm_delete.html', {'employee': employee})

# =======================
# Dashboard
# =======================
@login_required
def dashboard_page(request):
    tasks = Task.objects.all()
    status_filter = request.GET.get("status")
    employee_filter = request.GET.get("employee")

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if employee_filter:
        tasks = tasks.filter(assigned_to__user__username__icontains=employee_filter)

    status_list = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ]
    employees = Employee.objects.all()

    return render(request, 'tasks/dashboard.html', {
        'tasks': tasks,
        'status_list': status_list,
        'employees': employees
    })

# =======================
# Task Management
# =======================
@login_required
def task_add(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('dashboard')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

# =======================
# Assign Task
# =======================
@login_required
def assign_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == "POST":
        employee_ids = request.POST.getlist("employees")
        employees = Employee.objects.filter(id__in=employee_ids)
        task.assigned_to.set(employees)
        task.save()
        return redirect("dashboard")

    employees = Employee.objects.all()
    return render(request, 'tasks/assign_task_modal.html', {'task': task, 'employees': employees})

# =======================
# AJAX: Update Status
# =======================
@csrf_exempt
def update_status(request, task_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            status = data.get('status')
            task = Task.objects.get(id=task_id)
            previous_status = task.status

            if status in ['todo', 'in_progress', 'completed']:
                task.status = status
                task.save()
                if previous_status != 'completed' and status == 'completed':
                    send_task_completion_email(task)
                return JsonResponse({'success': True})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# =======================
# Add Comment (AJAX)
# =======================
@csrf_exempt
@login_required
def add_comment(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        content = request.POST.get('content')

        if not task_id or not content:
            return JsonResponse({'success': False, 'error': 'Missing task or content'})

        try:
            task = Task.objects.get(id=task_id)
            comment = Comment.objects.create(task=task, user=request.user, content=content)
            return JsonResponse({
                'success': True,
                'comment': {
                    'user': comment.user.username,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

# =======================
# Task List
# =======================
def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

@login_required
def employee_dashboard(request):
    tasks = Task.objects.filter(assigned_to__user=request.user)
    return render(request, 'tasks/employee_dashboard.html', {'tasks': tasks})

# =======================
# Send Email (Gemini + Django)
# =======================
@login_required
def send_email(request):
    if request.method == "POST":
        # Get selected employees
        employee_ids = request.POST.getlist('employees')
        selected_employees = Employee.objects.filter(id__in=employee_ids)
        recipient_list = [emp.user.email for emp in selected_employees if emp.user.email]

        if not recipient_list:
            messages.error(request, "No valid recipient emails found.")
            return redirect('dashboard')

        # Prepare completed tasks text
        completed_tasks = Task.objects.filter(status='completed')



        # -------------------------------
        # <-- Insert the snippet here -->
        if completed_tasks.exists():
            task_list = ", ".join([task.title for task in completed_tasks])
            employee_names = ", ".join([emp.user.username for emp in selected_employees if emp.user.username])
            message = f"""
Hello Team,

I hope you are all doing well. I am pleased to share that the following tasks have been successfully completed: {task_list}.

Special recognition goes to {employee_names} for their outstanding contributions. Your dedication, teamwork, and attention to detail are truly appreciated and have contributed significantly to our progress.

These accomplishments demonstrate our team’s ability to collaborate effectively and achieve our goals together. Let’s continue maintaining this momentum, supporting each other, and striving for excellence in all upcoming tasks.

Thank you all for your hard work and commitment — together, we are building a stronger, more successful team!

Best regards,
{request.user.username}
"""
        else:
            message = f"""
Hello Team,

Currently, no tasks have been completed. Let's continue to work together to achieve our goals and maintain steady progress.

Best regards,
{request.user.username}
"""
        # -------------------------------

        # Debug prints (optional)
        print("Sending to:", recipient_list)
        print("Email from:", settings.EMAIL_HOST_USER)
        print("Message:", message)

        # Send email
        try:
            send_mail(
                subject="Task Completion Update",
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            messages.success(request, "Email sent successfully!")
        except Exception as e:
            messages.error(request, f"Error sending email: {str(e)}")

    return redirect('dashboard')


# =======================
# Board
# =======================
@login_required
def board(request):
    tasks = Task.objects.all()
    context = {
        'todo_tasks': tasks.filter(status='todo'),
        'in_progress_tasks': tasks.filter(status='in_progress'),
        'completed_tasks': tasks.filter(status='completed'),
        'employees': Employee.objects.all(),
    }
    return render(request, 'tasks/board.html', context)

# =======================
# Test Email
# =======================
def test_email(request):
    try:
        send_mail(
            subject="Test Email",
            message="This is a test email from Django.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        return HttpResponse("Test email sent!")
    except Exception as e:
        return HttpResponse(f"Error sending test email: {str(e)}")
# Inside your send_email view, after generating 'task_list' and 'employee_names':

