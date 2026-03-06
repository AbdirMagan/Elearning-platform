from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify-email/<int:user_id>/', views.verify_email, name='verify_email'),
    path('resend-verification/<int:user_id>/', views.resend_verification, name='resend_verification'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Student dashboard
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # Instructor dashboard and management
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/course/<slug:course_slug>/students/', views.instructor_students, name='instructor_students'),
    
    # Admin dashboard and management
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users_list, name='admin_users_list'),
    path('admin/courses/', views.admin_courses, name='admin_courses'),
    path('admin/transactions/', views.admin_transactions, name='admin_transactions'),
    path('admin/enrollment-requests/', views.admin_enrollment_requests, name='admin_enrollment_requests'),
    path('admin/enrollment-request/<int:request_id>/process/', views.process_enrollment_request, name='process_enrollment_request'),
    path('admin/course/<int:course_id>/approve/', views.admin_approve_course, name='admin_approve_course'),
]
