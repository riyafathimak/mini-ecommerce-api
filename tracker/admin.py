from django.contrib import admin

# Register your models here.
from .models import Employee, Task, Comment

admin.site.register(Employee)
admin.site.register(Task)
admin.site.register(Comment)
