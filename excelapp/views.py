from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import now
import json
import openpyxl

from accounts.models import CustomUser
from .models import ConsultantSheet, SheetRow


# =========================================================
# CONSULTANT DASHBOARD
# =========================================================
from .models import ConsultantSheet, Notification

@login_required
def consultant_dashboard(request):
    if request.user.role != "consultant":
        return redirect("admin_dashboard")

    consultant = request.user

    sheets = ConsultantSheet.objects.filter(consultant=consultant)

    student_sheet = sheets.filter(sheet_type="STUDENT").first()
    attendance_sheet = sheets.filter(sheet_type="ATTENDANCE").first()
    completed_sheet = sheets.filter(sheet_type="COMPLETED").first()

    unread_count = Notification.objects.filter(
        consultant=consultant,
        is_read=False
    ).count()

    context = {
        "user": consultant,
        "sheets": sheets,
        "student_sheet": student_sheet,
        "attendance_sheet": attendance_sheet,
        "completed_sheet": completed_sheet,
        "unread_count": unread_count,
    }

    return render(request, "consultant_dashboard.html", context)


# =========================================================
# ADMIN DASHBOARD
# =========================================================
@login_required
def admin_dashboard(request):
    if request.user.role != "admin":
        return redirect("consultant_dashboard")

    consultants = CustomUser.objects.filter(role="consultant")
    total_consultants = consultants.count()

    total_sheets = ConsultantSheet.objects.count()
    total_rows = SheetRow.objects.count()

    sheets = ConsultantSheet.objects.all().order_by("-created_at")

    context = {
        "consultants": consultants,
        "total_consultants": total_consultants,
        "total_sheets": total_sheets,
        "total_rows": total_rows,
        "sheets": sheets,
    }

    return render(request, "admin_dashboard.html", context)


# =========================================================
# CREATE STUDENT SHEET
# =========================================================
@login_required
def create_student_sheet(request):
    if request.user.role != "consultant":
        return redirect("consultant_dashboard")

    consultant = request.user

    exists = ConsultantSheet.objects.filter(
        consultant=consultant,
        sheet_type="STUDENT"
    ).exists()

    if exists:
        messages.warning(request, "Student Sheet already exists!")
        return redirect("consultant_dashboard")

    ConsultantSheet.objects.create(
        consultant=consultant,
        sheet_name="Student Details",
        sheet_type="STUDENT"
    )

    messages.success(request, "Student Sheet Created Successfully!")
    return redirect("consultant_dashboard")


# =========================================================
# CREATE ATTENDANCE SHEET
# =========================================================
@login_required
def create_attendance_sheet(request):
    if request.user.role != "consultant":
        return redirect("consultant_dashboard")

    consultant = request.user

    exists = ConsultantSheet.objects.filter(
        consultant=consultant,
        sheet_type="ATTENDANCE"
    ).exists()

    if exists:
        messages.warning(request, "Attendance Sheet already exists!")
        return redirect("consultant_dashboard")

    ConsultantSheet.objects.create(
        consultant=consultant,
        sheet_name="Attendance Sheet",
        sheet_type="ATTENDANCE"
    )

    messages.success(request, "Attendance Sheet Created Successfully!")
    return redirect("consultant_dashboard")


# =========================================================
# CREATE COMPLETED SHEET
# =========================================================
@login_required
def create_completed_sheet(request):
    if request.user.role != "consultant":
        return redirect("consultant_dashboard")

    consultant = request.user

    exists = ConsultantSheet.objects.filter(
        consultant=consultant,
        sheet_type="COMPLETED"
    ).exists()

    if exists:
        messages.warning(request, "Completed Batch Sheet already exists!")
        return redirect("consultant_dashboard")

    ConsultantSheet.objects.create(
        consultant=consultant,
        sheet_name="Completed Batch Sheet",
        sheet_type="COMPLETED"
    )

    messages.success(request, "Completed Batch Sheet Created Successfully!")
    return redirect("consultant_dashboard")


# =========================================================
# VIEW SHEET (CONSULTANT)
# =========================================================
@login_required
def view_sheet(request, sheet_id):
    sheet = get_object_or_404(ConsultantSheet, id=sheet_id)

    # Consultant can view only their own sheet
    if request.user.role == "consultant" and sheet.consultant != request.user:
        messages.error(request, "Access Denied!")
        return redirect("consultant_dashboard")

    rows = SheetRow.objects.filter(sheet=sheet).order_by("id")

    return render(request, "view_sheet.html", {"sheet": sheet, "rows": rows})

@login_required
def view_attendancesheet(request, sheet_id):
    sheet = get_object_or_404(ConsultantSheet, id=sheet_id)

    if request.user.role == "consultant" and sheet.consultant != request.user:
        messages.error(request, "Access Denied!")
        return redirect("consultant_dashboard")

    rows = SheetRow.objects.filter(sheet=sheet).order_by("id")

    context = {
        "sheet": sheet,
        "rows": rows,
        "days": range(1, 32),   # Add this
    }

    return render(request, "attendance_sheet.html", context)


# =========================================================
# DELETE SHEET (CONSULTANT)
# =========================================================
@login_required
def delete_sheet(request, sheet_id):
    sheet = get_object_or_404(ConsultantSheet, id=sheet_id)

    if request.user.role == "consultant" and sheet.consultant != request.user:
        messages.error(request, "Access Denied!")
        return redirect("consultant_dashboard")

    sheet.delete()
    messages.success(request, "Sheet deleted successfully!")
    return redirect("consultant_dashboard")


# =========================================================
# SAVE SHEET DATA (AJAX)
# =========================================================
@login_required
def save_sheet_data(request, sheet_id):
    sheet = get_object_or_404(ConsultantSheet, id=sheet_id)

    # Consultant can edit only their own sheet
    if request.user.role == "consultant" and sheet.consultant != request.user:
        return JsonResponse({"error": "Access Denied"}, status=403)

    if request.method == "POST":
        data = json.loads(request.body).get("data", [])

        # delete old rows
        SheetRow.objects.filter(sheet=sheet).delete()

        # save new rows
        for row in data:
            SheetRow.objects.create(
                sheet=sheet,
                col1=row[0] if len(row) > 0 else "",
                col2=row[1] if len(row) > 1 else "",
                col3=row[2] if len(row) > 2 else "",
                col4=row[3] if len(row) > 3 else "",
                col5=row[4] if len(row) > 4 else "",
                col6=row[5] if len(row) > 5 else "",
                col7=row[6] if len(row) > 6 else "",
                col8=row[7] if len(row) > 7 else "",
                col9=row[8] if len(row) > 8 else "",
                col10=row[9] if len(row) > 9 else "",
                col11=row[10] if len(row) > 10 else "",
                col12=row[11] if len(row) > 11 else "",
            )

        return JsonResponse({"message": "Sheet Saved Successfully!"})

    return JsonResponse({"error": "Invalid Request"}, status=400)


# =========================================================
# ADMIN DOWNLOAD EXCEL
# =========================================================
@login_required
def download_sheet_excel(request, sheet_id):
    if request.user.role != "admin":
        return redirect("consultant_dashboard")

    sheet = get_object_or_404(ConsultantSheet, id=sheet_id)
    rows = SheetRow.objects.filter(sheet=sheet).order_by("id")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet.sheet_name

    ws.append([
        "Col1", "Col2", "Col3", "Col4", "Col5", "Col6",
        "Col7", "Col8", "Col9", "Col10", "Col11", "Col12"
    ])

    for row in rows:
        ws.append([
            row.col1, row.col2, row.col3, row.col4, row.col5, row.col6,
            row.col7, row.col8, row.col9, row.col10, row.col11, row.col12
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{sheet.sheet_name}.xlsx"'

    wb.save(response)
    return response

@login_required
def view_sheet_redirect(request, sheet_id):
    sheet = get_object_or_404(ConsultantSheet, id=sheet_id)

    # Admin can view all
    # Consultant can view only their sheets
    if request.user.role != "admin" and sheet.consultant != request.user:
        messages.error(request, "You are not allowed to view this sheet!")
        return redirect("consultant_dashboard")

    if sheet.sheet_type == "STUDENT":
        return redirect("student_sheet_view", sheet_id=sheet.id)

    elif sheet.sheet_type == "ATTENDANCE":
        return redirect("attendance_sheet_view", sheet_id=sheet.id)

    elif sheet.sheet_type == "COMPLETED":
        return redirect("completed_sheet_view", sheet_id=sheet.id)

    else:
        messages.error(request, "Invalid Sheet Type!")
        return redirect("admin_dashboard")


# ======================================================
# STUDENT SHEET VIEW
# ======================================================
@login_required
def student_sheet_view(request, sheet_id):
    sheet = get_object_or_404(ConsultantSheet, id=sheet_id)

    if request.user.role != "admin" and sheet.consultant != request.user:
        messages.error(request, "You are not allowed to view this sheet!")
        return redirect("consultant_dashboard")

    rows = SheetRow.objects.filter(sheet=sheet).order_by("id")

    context = {
        "sheet": sheet,
        "rows": rows,
    }
    return render(request, "student_sheet.html", context)


# ======================================================
# ATTENDANCE SHEET VIEW
# ======================================================
@login_required
def attendance_sheet_view(request, sheet_id):
    sheet = get_object_or_404(ConsultantSheet, id=sheet_id)

    if request.user.role != "admin" and sheet.consultant != request.user:
        messages.error(request, "You are not allowed to view this sheet!")
        return redirect("consultant_dashboard")

    rows = SheetRow.objects.filter(sheet=sheet).order_by("id")

    context = {
        "sheet": sheet,
        "rows": rows,
        "days": range(1, 32)  # 1 to 31
    }
    return render(request, "attendance_sheet.html", context)


# ======================================================
# COMPLETED SHEET VIEW
# ======================================================
@login_required
def completed_sheet_view(request, sheet_id):
    sheet = get_object_or_404(ConsultantSheet, id=sheet_id)

    if request.user.role != "admin" and sheet.consultant != request.user:
        messages.error(request, "You are not allowed to view this sheet!")
        return redirect("consultant_dashboard")

    rows = SheetRow.objects.filter(sheet=sheet).order_by("id")

    context = {
        "sheet": sheet,
        "rows": rows,
    }
    return render(request, "completed_sheet.html", context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from excelapp.models import ConsultantSheet, SheetRow

@login_required
def attendance_sheet_view(request, sheet_id):
    sheet = get_object_or_404(ConsultantSheet, id=sheet_id)

    if request.user.role != "admin" and sheet.consultant != request.user:
        return redirect("consultant_dashboard")

    rows = SheetRow.objects.filter(sheet=sheet).order_by("id")

    return render(request, "attendance_sheet.html", {
        "sheet": sheet,
        "rows": rows,
        "days": range(1, 32)
    })

@login_required
def save_attendance_data(request, sheet_id):
    sheet = get_object_or_404(ConsultantSheet, id=sheet_id)

    if request.user.role != "admin" and sheet.consultant != request.user:
        return JsonResponse({"message": "Unauthorized"}, status=403)

    if request.method == "POST":
        data = json.loads(request.body).get("data", [])

        # Delete old rows
        SheetRow.objects.filter(sheet=sheet).delete()

        # Save new rows
        for row in data:
            SheetRow.objects.create(
                sheet=sheet,
                col1=row[0] if len(row) > 0 else "",   # student name
                col2=row[1] if len(row) > 1 else "",   # batch time
                col3=row[2] if len(row) > 2 else "",   # month
                col4=row[3] if len(row) > 3 else "",   # year
                col5=row[4] if len(row) > 4 else "",   # day1
                col6=row[5] if len(row) > 5 else "",
                col7=row[6] if len(row) > 6 else "",
                col8=row[7] if len(row) > 7 else "",
                col9=row[8] if len(row) > 8 else "",
                col10=row[9] if len(row) > 9 else "",
                col11=row[10] if len(row) > 10 else "",
                col12=row[11] if len(row) > 11 else "",
                col13=row[12] if len(row) > 12 else "",
                col14=row[13] if len(row) > 13 else "",
                col15=row[14] if len(row) > 14 else "",
                col16=row[15] if len(row) > 15 else "",
                col17=row[16] if len(row) > 16 else "",
                col18=row[17] if len(row) > 17 else "",
                col19=row[18] if len(row) > 18 else "",
                col20=row[19] if len(row) > 19 else "",
                col21=row[20] if len(row) > 20 else "",
                col22=row[21] if len(row) > 21 else "",
                col23=row[22] if len(row) > 22 else "",
                col24=row[23] if len(row) > 23 else "",
                col25=row[24] if len(row) > 24 else "",
                col26=row[25] if len(row) > 25 else "",
                col27=row[26] if len(row) > 26 else "",
                col28=row[27] if len(row) > 27 else "",
                col29=row[28] if len(row) > 28 else "",
                col30=row[29] if len(row) > 29 else "",
                col31=row[30] if len(row) > 30 else "",
                col32=row[31] if len(row) > 31 else "",
                col33=row[32] if len(row) > 32 else "",
                col34=row[33] if len(row) > 33 else "",
                col35=row[34] if len(row) > 34 else "",
            )

        return JsonResponse({"message": "Attendance Sheet Saved Successfully!"})

    return JsonResponse({"message": "Invalid Request"}, status=400)

from django.shortcuts import render, get_object_or_404, redirect
from .models import ConsultantSheet, SheetRow
from accounts.models import CustomUser


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ConsultantSheet, SheetRow

@login_required
def completed_sheet_view(request, sheet_id):

    sheet = get_object_or_404(ConsultantSheet, id=sheet_id)

    # Only allow admin OR same consultant
    if request.user.role != "admin" and sheet.consultant != request.user:
        return redirect("consultant_dashboard")

    rows = SheetRow.objects.filter(sheet=sheet).order_by("id")

    return render(request, "completed_sheet_view.html", {
        "sheet": sheet,
        "rows": rows
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ConsultantSheet, SheetRow


@login_required
def auto_transfer_completed(request):
    if request.user.role != "consultant":
        return redirect("consultant_dashboard")

    consultant = request.user

    # Get student sheet
    student_sheet = ConsultantSheet.objects.filter(
        consultant=consultant,
        sheet_type="STUDENT"
    ).first()

    # Get completed sheet
    completed_sheet = ConsultantSheet.objects.filter(
        consultant=consultant,
        sheet_type="COMPLETED"
    ).first()

    if not student_sheet:
        messages.error(request, "Student Sheet not found!")
        return redirect("consultant_dashboard")

    if not completed_sheet:
        messages.error(request, "Completed Sheet not found!")
        return redirect("consultant_dashboard")

    student_rows = SheetRow.objects.filter(sheet=student_sheet)

    transferred_count = 0

    for row in student_rows:
        try:
            percentage = int(row.col6)  # col6 = percentage (change if needed)
        except:
            percentage = 0

        if percentage == 100:
            # Transfer row data into completed sheet
            SheetRow.objects.create(
                sheet=completed_sheet,
                col1=row.col1,
                col2=row.col2,
                col3=row.col3,
                col4=row.col4,
                col5=row.col5,
                col6=row.col6,
                col7=row.col7,
                col8=row.col8,
                col9=row.col9,
                col10=row.col10,
                col11=row.col11,
                col12=row.col12,
            )

            # delete from student sheet
            row.delete()
            transferred_count += 1

    messages.success(request, f"{transferred_count} Students moved to Completed Sheet!")
    return redirect("consultant_dashboard")

@login_required
def save_attendance_data(request, sheet_id):
    sheet = get_object_or_404(ConsultantSheet, id=sheet_id)

    if request.user.role != "admin" and sheet.consultant != request.user:
        return JsonResponse({"message": "Unauthorized"}, status=403)

    if request.method == "POST":
        data = json.loads(request.body).get("data", [])

        SheetRow.objects.filter(sheet=sheet).delete()

        for row in data:
            SheetRow.objects.create(
                sheet=sheet,
                col1=row[0] if len(row) > 0 else "",   # student name
                col2=row[1] if len(row) > 1 else "",   # batch time
                col3=row[2] if len(row) > 2 else "",   # month
                col4=row[3] if len(row) > 3 else "",   # year

                col5=row[4] if len(row) > 4 else "",   # day1
                col6=row[5] if len(row) > 5 else "",
                col7=row[6] if len(row) > 6 else "",
                col8=row[7] if len(row) > 7 else "",
                col9=row[8] if len(row) > 8 else "",
                col10=row[9] if len(row) > 9 else "",
                col11=row[10] if len(row) > 10 else "",
                col12=row[11] if len(row) > 11 else "",
                col13=row[12] if len(row) > 12 else "",
                col14=row[13] if len(row) > 13 else "",
                col15=row[14] if len(row) > 14 else "",
                col16=row[15] if len(row) > 15 else "",
                col17=row[16] if len(row) > 16 else "",
                col18=row[17] if len(row) > 17 else "",
                col19=row[18] if len(row) > 18 else "",
                col20=row[19] if len(row) > 19 else "",
                col21=row[20] if len(row) > 20 else "",
                col22=row[21] if len(row) > 21 else "",
                col23=row[22] if len(row) > 22 else "",
                col24=row[23] if len(row) > 23 else "",
                col25=row[24] if len(row) > 24 else "",
                col26=row[25] if len(row) > 25 else "",
                col27=row[26] if len(row) > 26 else "",
                col28=row[27] if len(row) > 27 else "",
                col29=row[28] if len(row) > 28 else "",
                col30=row[29] if len(row) > 29 else "",
                col31=row[30] if len(row) > 30 else "",
                col32=row[31] if len(row) > 31 else "",
                col33=row[32] if len(row) > 32 else "",
                col34=row[33] if len(row) > 33 else "",
                col35=row[34] if len(row) > 34 else "",
            )

        return JsonResponse({"message": "Attendance Saved Successfully!"})

    return JsonResponse({"message": "Invalid Request"}, status=400)

from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

@login_required
def student_change_password(request):


    if request.method == "POST":

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Check old password
        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("student_change_password")

        # Match passwords
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("student_change_password")

        # Optional password length check
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return redirect("student_change_password")

        # Save new password
        request.user.set_password(new_password)
        request.user.save()

        # Keep user logged in
        update_session_auth_hash(request, request.user)

        messages.success(request, "Password updated successfully.")

        return redirect("student_dashboard")

    return render(request, "student_change_password.html")

from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

@login_required
def consultant_change_password(request):


    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("consultant_change_password")

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("consultant_change_password")

        request.user.set_password(new_password)
        request.user.save()

        # Keep consultant logged in
        update_session_auth_hash(request, request.user)

        messages.success(request, "Password changed successfully.")
        return redirect("consultant_dashboard")

    return render(request, "consultant_change_password.html")
from accounts.models import CustomUser
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Student, Notification
from .forms import StudentForm
from accounts.models import CustomUser

def add_student(request):

    if request.method == "POST":

        form = StudentForm(request.POST)

        if form.is_valid():

            student = form.save()

            try:
                consultant = CustomUser.objects.get(
    consultant_name=student.allocated_consultant,
    role="consultant"
)

                Notification.objects.create(
                    consultant=consultant,
                    student=student,
                    message=f"New Student Assigned : {student.student_name}"
                )

            except CustomUser.DoesNotExist:
                messages.warning(
                    request,
                    "Student added, but consultant username not found."
                )

            messages.success(request, "Student Added Successfully")
            return redirect("student_list")

    else:
        form = StudentForm()

    return render(request, "add_student.html", {"form": form})
def student_list(request):

    students=Student.objects.all().order_by("-id")

    return render(request,"student_list.html",{"students":students})

def edit_student(request,id):

    student=get_object_or_404(Student,id=id)

    if request.method=="POST":

        form=StudentForm(request.POST,instance=student)

        if form.is_valid():

            form.save()

            return redirect("student_list")

    else:

        form=StudentForm(instance=student)

    return render(request,"add_student.html",{"form":form})

def delete_student(request,id):

    student=get_object_or_404(Student,id=id)

    student.delete()

    return redirect("student_list")

from django.contrib.auth.decorators import login_required

@login_required
def consultant_notifications(request):

    notifications = Notification.objects.filter(
        consultant=request.user
    ).order_by('-created_at')

    return render(
        request,
        "consultant_notifications.html",
        {"notifications":notifications}
    )

@login_required
def student_detail(request,id):

    student=Student.objects.get(id=id)

    Notification.objects.filter(
        consultant=request.user,
        student=student
    ).update(is_read=True)

    return render(
        request,
        "student_detail.html",
        {"student":student}
    )