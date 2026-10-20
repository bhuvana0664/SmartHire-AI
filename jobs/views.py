from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from pypdf import PdfReader
from .models import Job, JobApplication, RecruiterProfile
from .models import JobApplication


# 1. Home Page and Job Search
def home(request):
    query = request.GET.get('search', '')

    jobs = Job.objects.all().order_by('-posted_date')

    if query:
        jobs = jobs.filter(title__icontains=query) | jobs.filter(
            company__icontains=query
        ) | jobs.filter(location__icontains=query)

    return render(
        request,
        'jobs/home.html',
        {'jobs': jobs, 'query': query}
    )


# 2. Job Details
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'jobs/job_detail.html', {'job': job})


# 3. Apply for a Job
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        resume = request.FILES.get('resume')
        cover_letter = request.POST.get('cover_letter', '')

        if not all([full_name, email, phone, resume]):
            messages.error(
                request,
                'Please fill in all required fields and upload your resume.'
            )
            return render(request, 'jobs/apply_job.html', {'job': job})

        JobApplication.objects.create(
            job=job,
            full_name=full_name,
            email=email,
            phone=phone,
            resume=resume,
            cover_letter=cover_letter
        )

        return render(request, 'jobs/application_success.html')

    return render(request, 'jobs/apply_job.html', {'job': job})


# 4. Applied Jobs Page
def applied_jobs(request):
    if not request.user.is_authenticated:
        return redirect('login')

    applications = JobApplication.objects.filter(
        email=request.user.email
    ).order_by('-applied_date')

    return render(
        request,
        'jobs/applied_jobs.html',
        {'applications': applications}
    )


# 5. Job Seeker Registration
def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password:
            messages.error(request, 'Please fill in all required fields.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif len(password) < 8:
            messages.error(request, 'Password must contain at least 8 characters.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')

    return render(request, 'jobs/register.html')


# 6. User Login
def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'jobs/login.html')


# 7. User Logout
def user_logout(request):
    if request.method == 'POST':
        logout(request)
    return redirect('home')


# 8. Job Seeker Dashboard
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    applications = JobApplication.objects.filter(
        email=request.user.email
    ).order_by('-applied_date')

    return render(
        request,
        'jobs/dashboard.html',
        {'applications': applications}
    )


# 9. Recruiter Registration
def recruiter_register(request):
    if request.user.is_authenticated:
        return redirect('recruiter_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        company_name = request.POST.get('company_name', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not all([username, email, password, company_name]):
            messages.error(request, 'Please fill in all required fields.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif len(password) < 8:
            messages.error(request, 'Password must contain at least 8 characters.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            RecruiterProfile.objects.create(
                user=user,
                company_name=company_name,
                phone=phone
            )

            messages.success(
                request,
                'Recruiter registration successful! Please log in.'
            )
            return redirect('recruiter_login')

    return render(request, 'jobs/recruiter_register.html')


# 10. Recruiter Login
def recruiter_login(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'recruiter_profile'):
            return redirect('recruiter_dashboard')
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and hasattr(user, 'recruiter_profile'):
            login(request, user)
            return redirect('recruiter_dashboard')

        messages.error(
            request,
            'Invalid recruiter username or password.'
        )

    return render(request, 'jobs/recruiter_login.html')


# 11. Recruiter Dashboard
def recruiter_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('recruiter_login')

    if not hasattr(request.user, 'recruiter_profile'):
        logout(request)
        messages.error(request, 'Please log in with a recruiter account.')
        return redirect('recruiter_login')

    jobs = Job.objects.filter(
        company=request.user.recruiter_profile.company_name
    ).order_by('-posted_date')

    applications = JobApplication.objects.filter(
        job__in=jobs
    ).order_by('-applied_date')

    return render(
        request,
        'jobs/recruiter_dashboard.html',
        {
            'jobs': jobs,
            'applications': applications
        }
    )
# Update Application Status
def update_application_status(request, application_id):
    if not request.user.is_authenticated:
        return redirect('recruiter_login')

    if request.method != 'POST':
        return redirect('recruiter_dashboard')

    application = get_object_or_404(
        JobApplication,
        id=application_id
    )

    # Confirm that this recruiter owns the job
    if not Job.objects.filter(
        id=application.job_id,
        company=request.user.recruiter_profile.company_name
    ).exists():
        messages.error(request, 'You cannot update this application.')
        return redirect('recruiter_dashboard')

    status = request.POST.get('status', '')

    if status in ['Pending', 'Shortlisted', 'Rejected']:
        application.status = status
        application.save(update_fields=['status'])
        messages.success(request, 'Application status updated!')
    else:
        messages.error(request, 'Invalid application status.')

    return redirect('recruiter_dashboard')
# 12. Post a Job
def post_job(request):
    if not request.user.is_authenticated:
        return redirect('recruiter_login')

    if not hasattr(request.user, 'recruiter_profile'):
        messages.error(request, 'Please log in with a recruiter account.')
        return redirect('recruiter_login')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        location = request.POST.get('location', '').strip()
        salary = request.POST.get('salary', '').strip()
        description = request.POST.get('description', '').strip()
        requirements = request.POST.get('requirements', '').strip()

        company = request.user.recruiter_profile.company_name

        if not all([title, location, salary, description, requirements]):
            messages.error(request, 'Please fill in all required fields.')
        else:
            Job.objects.create(
                title=title,
                company=company,
                location=location,
                salary=salary,
                description=description,
                requirements=requirements
            )

            messages.success(request, 'Job posted successfully!')
            return redirect('recruiter_dashboard')

    return render(request, 'jobs/post_job.html')
# AI Resume Analysis - Basic Version
def analyze_resume(request, application_id):
    if not request.user.is_authenticated:
        return redirect('recruiter_login')

    try:
        recruiter = request.user.recruiter_profile
    except Exception:
        messages.error(request, 'Recruiter account required.')
        return redirect('recruiter_login')

    application = get_object_or_404(
        JobApplication,
        id=application_id,
        job__company=recruiter.company_name
    )

    try:
        reader = PdfReader(application.resume.path)

        resume_text = " ".join(
            page.extract_text() or ""
            for page in reader.pages
        ).lower()

        required_skills = [
            skill.strip().lower()
            for skill in application.job.requirements.replace(
                ",", "\n"
            ).splitlines()
            if skill.strip()
        ]

        matched_skills = [
            skill for skill in required_skills
            if skill in resume_text
        ]

        total_skills = len(required_skills)

        score = round(
            len(matched_skills) / total_skills * 100
        ) if total_skills else 0

        return render(request, 'jobs/resume_analysis.html', {
            'application': application,
            'matched_skills': matched_skills,
            'required_skills': required_skills,
            'missing_skills': [
                skill for skill in required_skills
                if skill not in matched_skills
            ],
            'score': score,
        })

    except Exception:
        messages.error(
            request,
            'Could not analyze this PDF. Please check the resume file.'
        )
        return redirect('recruiter_dashboard')