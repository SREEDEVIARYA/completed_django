from django.urls import path
from . import views

urlpatterns = [

    # Home
    path("", views.home, name="home"),

    # Authentication
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),

    # Consultant Registration
    path("register/", views.register, name="register"),

    # Admin Registration
    path("register_admin/", views.register_admin, name="register_admin"),

    # Dashboards
    path("dashboard/", views.dashboard, name="dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # Student
    path("student-register/", views.student_register, name="student_register"),
    path("student/login/", views.student_login, name="student_login"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),

    # Feedback
    path("student/feedback/", views.student_feedback, name="student_feedback"),
    path("admin/feedbacks/", views.admin_feedback_list, name="admin_feedback_list"),
    path("admin-feedback/", views.admin_view_feedback, name="admin_view_feedback"),

    # Admin Sheet Management
    path("admin/all-sheets/", views.admin_all_sheets, name="admin_all_sheets"),
]