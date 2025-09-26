from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # root of boards app
]
