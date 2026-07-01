
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):

    def create_user(self, emp_id, password=None, **extra_fields):
        if not emp_id:
            raise ValueError("Employee ID / Register Number is required")

        user = self.model(emp_id=emp_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, emp_id, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")

        return self.create_user(emp_id, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("consultant", "Consultant"),
        ("student", "Student"),
    )

    emp_id = models.CharField(max_length=50, unique=True)

    consultant_name = models.CharField(max_length=150, blank=True, null=True)
    company_email = models.EmailField(unique=True, blank=True, null=True)

    student_name = models.CharField(max_length=150, blank=True, null=True)
    student_email = models.EmailField(unique=True, blank=True, null=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "emp_id"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.emp_id} - {self.role}"
class Sheet(models.Model):
    SHEET_TYPE_CHOICES = (
        ("STUDENT", "Student Sheet"),
        ("ATTENDANCE", "Attendance Sheet"),
        ("COMPLETED", "Completed Sheet"),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sheet_name = models.CharField(max_length=200)
    sheet_type = models.CharField(max_length=20, choices=SHEET_TYPE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sheet_name} - {self.user.emp_id}"


class SheetRow(models.Model):
    sheet = models.ForeignKey(Sheet, on_delete=models.CASCADE, related_name="rows")

    col1 = models.CharField(max_length=255, blank=True, null=True)
    col2 = models.CharField(max_length=255, blank=True, null=True)
    col3 = models.CharField(max_length=255, blank=True, null=True)
    col4 = models.CharField(max_length=255, blank=True, null=True)
    col5 = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Row in {self.sheet.sheet_name}"
    
class Feedback(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    date_of_join = models.DateField()
    program_name = models.CharField(max_length=200)
    consultant_name = models.CharField(max_length=200)

    RATING_4 = [
        ("Excellent", "Excellent"),
        ("Good", "Good"),
        ("Average", "Average"),
        ("Poor", "Poor"),
    ]

    CONTENT = [
        ("Very Relevant", "Very Relevant"),
        ("Somewhat Relevant", "Somewhat Relevant"),
        ("Not Relevant", "Not Relevant"),
    ]

    TRAINER = [
        ("Always", "Always"),
        ("Sometimes", "Sometimes"),
        ("Rarely", "Rarely"),
        ("Never", "Never"),
    ]

    DELIVERY = [
        ("Very Satisfied", "Very Satisfied"),
        ("Satisfied", "Satisfied"),
        ("Neutral", "Neutral"),
        ("Dissatisfied", "Dissatisfied"),
    ]

    YESNO = [
        ("Yes", "Yes"),
        ("No", "No"),
    ]

    SKILL = [
        ("Yes, Significantly", "Yes, Significantly"),
        ("Yes, to some extent", "Yes, to some extent"),
        ("No", "No"),
    ]

    TOOLS = [
        ("Very Helpful", "Very Helpful"),
        ("Somewhat Helpful", "Somewhat Helpful"),
        ("Not Helpful", "Not Helpful"),
    ]

    PACE = [
        ("Too Fast", "Too Fast"),
        ("Just Right", "Just Right"),
        ("Too Slow", "Too Slow"),
    ]

    STARS = [
        ("5", "⭐⭐⭐⭐⭐"),
        ("4", "⭐⭐⭐⭐"),
        ("3", "⭐⭐⭐"),
        ("2", "⭐⭐"),
        ("1", "⭐"),
    ]

    overall_experience = models.CharField(max_length=50, choices=RATING_4)
    content_relevance = models.CharField(max_length=50, choices=CONTENT)
    quality_materials = models.CharField(max_length=50, choices=RATING_4)
    trainer_encouragement = models.CharField(max_length=50, choices=TRAINER)
    mode_of_delivery = models.CharField(max_length=50, choices=DELIVERY)

    class_started_on_time = models.CharField(max_length=10, choices=YESNO)
    skill_enhancement = models.CharField(max_length=50, choices=SKILL)
    confident_apply_skills = models.CharField(max_length=10, choices=YESNO)
    recording_uploaded = models.CharField(max_length=10, choices=YESNO)

    tools_helpful = models.CharField(max_length=50, choices=TOOLS)
    duration_sufficient = models.CharField(max_length=10, choices=YESNO)
    program_pace = models.CharField(max_length=50, choices=PACE)

    improvement_suggestion = models.TextField()
    future_topics = models.TextField()

    recommend_program = models.CharField(max_length=10, choices=YESNO)
    program_rating = models.CharField(max_length=5, choices=STARS)

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.emp_id} - Feedback"
    

from django.db import models

class Student(models.Model):
    full_name = models.CharField(max_length=200)
    dob = models.DateField()

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)

    profile_photo = models.ImageField(upload_to='students/', blank=True, null=True)

    nationality = models.CharField(max_length=100)

    aadhaar_number = models.CharField(max_length=20, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)

    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15)

    alternate_mobile = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    address1 = models.TextField()
    address2 = models.TextField(blank=True, null=True)

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name