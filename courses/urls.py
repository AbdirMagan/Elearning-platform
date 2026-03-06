from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('course/<slug:course_slug>/lesson/<slug:lesson_slug>/', views.lesson_detail, name='lesson_detail'),
    path('course/<slug:course_slug>/lesson/<slug:lesson_slug>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('course/<slug:slug>/review/', views.add_review, name='add_review'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    
    # Enrollment requests
    path('course/<slug:slug>/request-enrollment/', views.request_enrollment, name='request_enrollment'),
    path('my-enrollment-requests/', views.my_enrollment_requests, name='my_enrollment_requests'),
]
