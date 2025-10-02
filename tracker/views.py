from django.shortcuts import render, get_object_or_404, redirect
from .models import Task
from .forms import TaskForm, CommentForm
from django.db.models import Q
from .email_to_ticket import fetch_emails
from .models import Task, Ticket  # Add Ticket here

# Dashboard
def dashboard(request):
    tasks = Task.objects.all().order_by('created_at')

    tickets = Ticket.objects.all().order_by('-created_at')  # fetch all tickets

    query = request.GET.get('q')
    status = request.GET.get('status')
    priority = request.GET.get('priority')

    if query:
        tickets = tickets.filter(title__icontains=query)  # or description__icontains=query
    if status:
        tickets = tickets.filter(status=status)
    if priority:
        tickets = tickets.filter(priority=priority)

    return render(request, 'tracker/dashboard.html', {'tasks': tasks, 'tickets': tickets})




# Task Detail
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

# Create Task
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TaskForm()
    return render(request, 'tracker/task_form.html', {'form': form, 'title': 'Create Task'})

# Edit Task
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'tracker/task_form.html', {'form': form, 'title': 'Edit Task'})

# Delete Task
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('dashboard')
    return render(request, 'tracker/task_delete.html', {'task': task})
