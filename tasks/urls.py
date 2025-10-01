from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', lambda request: redirect('dashboard')),  # 👈 redirect /tasks/ to dashboard
    path('login/', views.login_page, name='login'),
    path('signup/', views.employee_signup, name='employee_signup'),
    path('dashboard/', views.dashboard_page, name='dashboard'),
    path('employees/list/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_add, name='employee_add'),
    path('employees/edit/<int:pk>/', views.employee_edit, name='employee_edit'),
    path('employees/delete/<int:pk>/', views.employee_delete, name='employee_delete'),
    path('tasks/list/', views.task_list, name='task_list'),
    path('tasks/add/', views.task_add, name='task_add'),
    path('tasks/edit/<int:pk>/', views.task_edit, name='task_edit'),
    path('tasks/delete/<int:pk>/', views.task_delete, name='task_delete'),
    path('employees/', views.employee_list, name='employee_list'),
    path('board/', views.board, name='board'),
    path('update_status/<int:task_id>/', views.update_status, name='update_status'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('add_comment/', views.add_comment, name='add_comment'),
    path('tasks/assign/<int:task_id>/', views.assign_task, name='assign_task'),
    path('board/', views.board, name='board'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('send-email/', views.send_email, name='send_email'),
    path('test-email/', views.test_email, name='test_email'),





]
