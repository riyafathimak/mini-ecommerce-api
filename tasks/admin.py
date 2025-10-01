from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Employee

admin.site.register(Employee)


if not admin.site.is_registered(Employee):
    @admin.register(Employee)
    class EmployeeAdmin(admin.ModelAdmin):
        list_display = ('user', 'position', 'department', 'salary')
        search_fields = ('user__username', 'position', 'department')
        list_filter = ('department', 'position')
