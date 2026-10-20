from django.contrib import admin
from django.urls import path
from jobs import views

urlpatterns = [
    # Admin

    # Home Page and Job Search
    path('', views.home, name='home'),

    # Job Details
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),

    # Apply for a Job
    path(
        'job/<int:job_id>/apply/',
        views.apply_job,
        name='apply_job'
    ),

    # Applied Jobs
    path(
        'applied-jobs/',
        views.applied_jobs,
        name='applied_jobs'
    ),

    # Registration
    path('register/', views.register, name='register'),

    # Login
    path('login/', views.user_login, name='login'),

    # Logout
    path('logout/', views.user_logout, name='logout'),

    # Job Seeker Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
]