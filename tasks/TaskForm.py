# tasks/forms.py
from django import forms
from .models import Task, Employee

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'duration', 'score', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
            'duration': forms.NumberInput(attrs={'class': 'w-full border rounded p-2'}),
            'score': forms.NumberInput(attrs={'class': 'w-full border rounded p-2'}),
            'assigned_to': forms.Select(attrs={'class': 'w-full border rounded p-2'}),
        }
