from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import csv
from students.models import Student
from io import TextIOWrapper
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Student
from .serializers import StudentSerializer
from django.urls import path
from rest_framework.permissions import IsAuthenticated




class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['username', 'email']  # fields to allow filtering

class StudentBulkUploadAPI(APIView):
    def post(self, request):
        # 1️⃣ Get the uploaded file
        file = request.FILES.get("file")  # Must match 'file' key in form-data
        if not file:
            return Response(
                {"error": "No file uploaded"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 2️⃣ Decode and read CSV using Python's built-in csv module
            decoded_file = TextIOWrapper(file.file, encoding="utf-8")
            reader = csv.DictReader(decoded_file)  # Reads CSV rows as dicts

            # 3️⃣ Check required columns
            required_columns = ["name", "roll_no"]
            if not all(col in reader.fieldnames for col in required_columns):
                return Response(
                    {"error": f"Missing required columns. Expected: {required_columns}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 4️⃣ Build Student objects
            students = []
            for row in reader:
                students.append(Student(
                    name=row["name"],
                    roll_no=row.get("roll_no") or None  # handle empty roll_no
                ))

            # 5️⃣ Bulk insert into DB
            Student.objects.bulk_create(students)

            return Response(
                {"message": f"{len(students)} students uploaded successfully"},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    class StudentBulkUploadAPI(APIView):
      permission_classes = [IsAuthenticated]  # ✅ Require JWT token

    def post(self, request):
        file = request.FILES.get("file")
        