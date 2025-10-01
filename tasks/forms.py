from django import forms
from django.contrib.auth.models import User
from .models import Employee, Task, Comment
from django.core.exceptions import ValidationError


# Employee Form
class EmployeeForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Employee
        fields = []  # Employee only has "user" now

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists.")
        return username

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )
        employee = Employee(user=user)
        if commit:
            employee.save()
        return employee


# Task Form
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'assigned_to', 'due_date', 'priority']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'assigned_to': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


# Comment Form
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }


# Employee Signup Form (optional, can reuse EmployeeForm)
class EmployeeSignupForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Employee
        fields = []

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )
        employee = Employee(user=user)
        if commit:
            employee.save()
        return employee
