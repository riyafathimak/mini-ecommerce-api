from django.db import models

class ClassModel(models.Model):
    name = models.CharField(max_length=50)   # Example: "10th", "+1"
    section = models.CharField(max_length=5) # Example: "A", "B"

    class Meta:
        db_table = "class"

    def __str__(self):
        return f"{self.name} - {self.section}"


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_no = models.IntegerField(null=True, blank=True)   # keep as required

    def __str__(self):
        return self.name


class StudentClass(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    classes = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name="class_students", null=True, blank=True)

    def __str__(self):
        return f"{self.student} → {self.classes}"
