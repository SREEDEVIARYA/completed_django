from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import ConsultantRegisterForm, StudentRegisterForm, FeedbackForm,AdminRegisterForm
from .models import CustomUser, Feedback

# IMPORTANT: Import models from excelapp (NOT accounts)
from excelapp.models import ConsultantSheet, SheetRow


# ==========================================================
# HOME PAGE
# ==========================================================
def home(request):
    return render(request, "home.html")


# ==========================================================
# CONSULTANT / ADMIN REGISTRATION
# ==========================================================
def register(request):
    form = ConsultantRegisterForm()

    if request.method == "POST":
        form = ConsultantRegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            # Only admin or consultant can register here
            if user.role not in ["admin", "consultant"]:
                user.role = "consultant"

            user.save()
            messages.success(request, "Registration Successful! Please Login.")
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Registration Failed! Please check the details.")

    return render(request, "register.html", {"form": form})

def register_admin(request):
    form = AdminRegisterForm()

    if request.method == "POST":
        form = AdminRegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            # Only admin or consultant can register here
            if user.role not in ["admin", "consultant"]:
                user.role = "consultant"

            user.save()
            messages.success(request, "Registration Successful! Please Login.")
            return redirect("login")
        else:
            messages.error(request, "Registration Failed! Please check the details.")

    return render(request, "register_admin.html", {"form": form})


# ==========================================================
# CONSULTANT / ADMIN LOGIN
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user_obj = CustomUser.objects.filter(
            company_email=email,
            role__in=["admin", "consultant"]
        ).first()

        if user_obj is None:
            messages.error(request, "Email not registered as Admin/Consultant!")
            return render(request, "login.html")

        # authenticate using emp_id (USERNAME_FIELD)
        user = authenticate(request, username=user_obj.emp_id, password=password)

        if user is not None:
            login(request, user)

            if user.role == "admin":
                return redirect("admin_dashboard")
            else:
                return redirect("consultant_dashboard")

        messages.error(request, "Invalid Password!")

    return render(request, "login.html")

# ==========================================================
# STUDENT REGISTRATION
# ==========================================================
def student_register(request):
    form = StudentRegisterForm()

    if request.method == "POST":
        form = StudentRegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Student Registration Successful! Please Login.")
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Student Registration Failed!")

    return render(request, "student_register.html", {"form": form})


# ==========================================================
# STUDENT LOGIN
# ==========================================================
def student_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # find student by email
        student_obj = CustomUser.objects.filter(
            student_email=email,
            role="student"
        ).first()

        if student_obj is None:
            messages.error(request, "Email is not registered!")
            return render(request, "student_login.html")

        # authenticate using emp_id because USERNAME_FIELD = emp_id
        user = authenticate(request, username=student_obj.emp_id, password=password)

        if user is not None:
            login(request, user)
            return redirect("student_dashboard")
        else:
            messages.error(request, "Invalid Password!")

    return render(request, "student_login.html")
# ==========================================================
# LOGOUT
# ==========================================================
def user_logout(request):
    logout(request)
    return redirect("home")


# ==========================================================
# DASHBOARD REDIRECT BASED ON ROLE
# ==========================================================
@login_required
def dashboard(request):
    if request.user.role == "admin":
        return redirect("admin_dashboard")
    elif request.user.role == "consultant":
        return redirect("consultant_dashboard")
    else:
        return redirect("student_dashboard")


# ==========================================================
# STUDENT DASHBOARD (Course Details + Attendance)
# ==========================================================
@login_required
def student_dashboard(request):

    if request.user.role != "student":
        return redirect("login")

    student_rows = None
    attendance_rows = None

    # -------------------------------
    # COURSE DETAILS FETCH BY EMAIL
    # -------------------------------
    if request.method == "POST" and "view_course" in request.POST:

        student_email = request.POST.get("student_email")

        if student_email:
            student_email = student_email.strip()

            student_rows = SheetRow.objects.filter(
                sheet__sheet_type="STUDENT",      # ✅ correct sheet type
                col4__iexact=student_email        # ✅ col4 = Email
            )

            if not student_rows.exists():
                student_rows = None
                messages.error(request, "No Course Details Found for this Email ID!")

        else:
            messages.error(request, "Please enter your Email ID!")

    # -------------------------------
    # ATTENDANCE FETCH BY NAME + BATCH
    # -------------------------------
    elif request.method == "POST" and "view_attendance" in request.POST:

        student_name = request.POST.get("student_name")
        batch_time = request.POST.get("batch_time")

        if student_name and batch_time:

            student_name = student_name.strip()
            batch_time = batch_time.strip()

            attendance_rows = SheetRow.objects.filter(
                sheet__sheet_type="ATTENDANCE",
                col1__iexact=student_name,     # col1 = Student Name
                col2__iexact=batch_time        # col2 = Batch Time
            )

            if not attendance_rows.exists():
                attendance_rows = None
                messages.error(request, "No Attendance Found for this Name and Batch Time!")

        else:
            messages.error(request, "Please enter Student Name and Batch Time!")

    context = {
        "student_rows": student_rows,
        "attendance_rows": attendance_rows,
    }

    return render(request, "student_dashboard.html", context)
# ==========================================================
# STUDENT FEEDBACK FORM
# ==========================================================
@login_required
def student_feedback(request):

    if request.user.role != "student":
        return redirect("login")

    if request.method == "POST":
        form = FeedbackForm(request.POST)

        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user
            feedback.save()

            messages.success(request, "Feedback Submitted Successfully!")
            return redirect("student_dashboard")

    else:
        form = FeedbackForm()

    return render(request, "student_feedback.html", {"form": form})


# ==========================================================
# ADMIN VIEW ALL FEEDBACKS
# ==========================================================
@login_required
def admin_feedback_list(request):

    if request.user.role != "admin":
        return redirect("login")

    feedbacks = Feedback.objects.select_related("student").order_by("-submitted_at")

    return render(request, "admin_feedback_list.html", {"feedbacks": feedbacks})


# ==========================================================
# ADMIN DASHBOARD
# ==========================================================
@login_required
def admin_dashboard(request):

    if request.user.role != "admin":
        return render(request, "unauthorized.html")

    total_consultants = CustomUser.objects.filter(role="consultant").count()
    total_sheets = ConsultantSheet.objects.count()
    total_feedbacks = Feedback.objects.count()

    sheets = ConsultantSheet.objects.select_related("consultant").order_by("-created_at")

    context = {
        "total_consultants": total_consultants,
        "total_sheets": total_sheets,
        "total_feedbacks": total_feedbacks,
        "sheets": sheets,
    }

    return render(request, "admin_dashboard.html", context)


# ==========================================================
# ADMIN VIEW ALL SHEETS LIST
# ==========================================================
@login_required
def admin_all_sheets(request):

    if request.user.role != "admin":
        return redirect("login")

    sheets = ConsultantSheet.objects.select_related("consultant").order_by("-created_at")

    return render(request, "admin_all_sheets.html", {"sheets": sheets})


# ==========================================================
# ADMIN VIEW SINGLE SHEET DATA (ROWS)
# ==========================================================
@login_required
def admin_view_sheet(request, sheet_id):

    if request.user.role != "admin":
        return redirect("login")

    sheet = get_object_or_404(ConsultantSheet, id=sheet_id)
    rows = SheetRow.objects.filter(sheet=sheet).order_by("id")

    return render(request, "admin_view_sheet.html", {"sheet": sheet, "rows": rows})



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import Feedback

@login_required
def admin_view_feedback(request):

    # only admin can access
    if request.user.role != "admin":
        return redirect("login")

    feedbacks = Feedback.objects.all().order_by("-submitted_at")

    return render(request, "admin_view_feedback.html", {"feedbacks": feedbacks})

from .forms import ConsultantRegisterForm, StudentRegisterForm
from django.contrib import messages


@login_required
def add_consultant(request):

    if request.user.role != "admin":
        return redirect("login")

    if request.method == "POST":
        form = ConsultantRegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = "consultant"
            user.save()

            messages.success(request, "Consultant added successfully.")
            return redirect("admin_dashboard")

    else:
        form = ConsultantRegisterForm()

    return render(request, "add_consultant.html", {"form": form})


@login_required
def add_student(request):

    if request.user.role != "admin":
        return redirect("login")

    if request.method == "POST":
        form = StudentRegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Student added successfully.")
            return redirect("admin_dashboard")

    else:
        form = StudentRegisterForm()

    return render(request, "add_student.html", {"form": form})