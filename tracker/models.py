from django.db import models
from django.contrib.auth.models import User

# -------------------
# Employee linked to User
# -------------------
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tracker_employee')
    role = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


# -------------------
# Client / Requester
# -------------------
class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.company})" if self.company else self.name


# -------------------
# Status & Priority Choices (global)
# -------------------
STATUS_CHOICES = [
    ('New', 'New'),
    ('In Progress', 'In Progress'),
    ('Completed', 'Completed'),
    ('Pending', 'Pending'),
]

PRIORITY_CHOICES = [
    ('High', 'High'),
    ('Medium', 'Medium'),
    ('Low', 'Low'),
]


# -------------------
# Email Model (for fetching emails)
# -------------------
class Email(models.Model):
    sender = models.EmailField()
    subject = models.CharField(max_length=200)
    body = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)
    message_id = models.CharField(max_length=200, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.subject} from {self.sender}"


# -------------------
# Message Model (from clients)
# -------------------
class Message(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject


# -------------------
# Task Model
# -------------------
class Task(models.Model):
    message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    client_email = models.EmailField(blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# -------------------
# Ticket Model
# -------------------
class Ticket(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)
    assigned_to = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    category = models.CharField(
        max_length=50,
        choices=[
            ('Backend', 'Backend'),
            ('Frontend', 'Frontend'),
            ('App Development', 'App Development'),
            ('Meetings', 'Meetings'),
        ],
        default='General'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# -------------------
# Comment Model
# -------------------
class Comment(models.Model):
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(Employee, null=True, on_delete=models.SET_NULL)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"


# -------------------
# Notification Model
# -------------------
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
