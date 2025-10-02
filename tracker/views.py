from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from .models import Task, Ticket, Email, Message, Notification
from .forms import TaskForm, CommentForm

# -----------------------------
# Dashboard with filters
# -----------------------------
def dashboard(request):
    tasks = Task.objects.all().order_by('created_at')
    tickets = Ticket.objects.all().order_by('-created_at')
    emails = Email.objects.all().order_by('-received_at')

    # Filters
    query = request.GET.get('q')
    status = request.GET.get('status')
    priority = request.GET.get('priority')
    category = request.GET.get('category')

    if query:
        tickets = tickets.filter(title__icontains=query)
    if status:
        tickets = tickets.filter(status=status)
    if priority:
        tickets = tickets.filter(priority=priority)
    if category:
        tickets = tickets.filter(category=category)

    context = {
        'tasks': tasks,
        'tickets': tickets,
        'emails': emails
    }
    return render(request, 'tracker/dashboard.html', context)

# -----------------------------
# Task Detail & Comment
# -----------------------------
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user.tracker_employee
            comment.save()
            return redirect('task_detail', pk=task.pk)
    else:
        form = CommentForm()
    return render(request, 'tracker/task_detail.html', {'task': task, 'form': form})

# -----------------------------
# Create Task
# -----------------------------
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            messages.success(request, "Task created successfully!")
            return redirect('dashboard')
    else:
        form = TaskForm()
    return render(request, 'tracker/task_form.html', {'form': form, 'title': 'Create Task'})

# -----------------------------
# Edit Task
# -----------------------------
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully!")
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'tracker/task_form.html', {'form': form, 'title': 'Edit Task'})

# -----------------------------
# Delete Task
# -----------------------------
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        messages.success(request, "Task deleted successfully!")
        return redirect('dashboard')
    return render(request, 'tracker/task_delete.html', {'task': task})

# -----------------------------
# Create Task from Message
# -----------------------------
def create_task_from_message(request, message_id):
    message_obj = get_object_or_404(Message, id=message_id)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.message = message_obj
            task.client_email = message_obj.client.email
            task.save()
            messages.success(request, 'Task created successfully from client message!')
            return redirect('dashboard')
    else:
        form = TaskForm(initial={
            'title': message_obj.subject,
            'description': message_obj.message,
        })

    return render(request, 'tracker/create_task_from_message.html', {
        'form': form,
        'message': message_obj,
    })

# -----------------------------
# Send Task Email
# -----------------------------
def send_task_email(task):
    if task.assigned_to and task.assigned_to.email:
        subject = f'New Task: {task.title}'
        message = f'Hello, you have a new task: {task.description}'
        recipient_list = [task.assigned_to.email]
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

# -----------------------------
# Update Task Status
# -----------------------------
def task_update_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(task._meta.get_field('status').choices):
            task.status = new_status
            task.save()
            messages.success(request, f"Task status updated to {new_status}!")
        else:
            messages.error(request, "Invalid status selected.")
    return redirect('task_detail', pk=task.pk)

# -----------------------------
# Get Notifications (JSON)
# -----------------------------
def get_notifications(request):
    if request.user.is_authenticated:
        notifs = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        return JsonResponse({
            'unread_count': notifs.count(),
            'messages': [n.message for n in notifs]
        })
    return JsonResponse({'unread_count': 0, 'messages': []})

# -----------------------------
# TaskForm (if not in forms.py)
# -----------------------------
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'priority', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
