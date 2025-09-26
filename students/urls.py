    # urls.py
from django.urls import path
from .views import StudentBulkUploadAPI

urlpatterns = [
    path("upload/", StudentBulkUploadAPI.as_view(), name="student-bulk-upload"),
]
