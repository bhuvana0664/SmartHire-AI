from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from jobs import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('applied-jobs/', views.applied_jobs, name='applied_jobs'),

    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path(
        'recruiter/register/',
        views.recruiter_register,
        name='recruiter_register'
    ),
    path(
        'recruiter/login/',
        views.recruiter_login,
        name='recruiter_login'
    ),
    path(
        'recruiter/dashboard/',
        views.recruiter_dashboard,
        name='recruiter_dashboard'
    ),
    path(
        'recruiter/post-job/',
        views.post_job,
        name='post_job'
    ),

    path(
        'recruiter/application/<int:application_id>/status/',
        views.update_application_status,
        name='update_application_status'
    ),

    path(
        'recruiter/application/<int:application_id>/analyze/',
        views.analyze_resume,
        name='analyze_resume'
    ),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )