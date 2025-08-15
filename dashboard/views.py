from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from job_list.models import Job
from profiles.models import UserProfile
from resumes.models import Education, Experience, Resume
from job_list.matching import match_jobs_for_user
from resumes.models import Application  # Change 'resumes' to the correct app name if needed
from job_list.models import SavedJob  # assuming you track saved jobs
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone


def is_employer(user):
    """Return True if the user is in the Employer group."""
    return user.is_authenticated and user.groups.filter(name='Employer').exists()

@login_required
def dashboard_redirect(request):
    """
    Small helper so any legacy links to /dashboard/ still work.
    Sends users to the correct dashboard based on role.
    """
    if is_employer(request.user):
        return redirect('employer_dashboard')
    return redirect('user_dashboard')


@login_required
def user_dashboard(request):
    # Get or create user profile
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    imported_resume = Resume.objects.filter(user=request.user, is_imported=True).order_by("-created_at").first()

    # Get user's resume and applications
    resume = Resume.objects.filter(user=request.user).first()
    education_entries = Education.objects.filter(resume=resume) if resume else []
    experience_entries = Experience.objects.filter(resume=resume) if resume else []
    applications = Application.objects.filter(applicant=request.user)

    # Track progress for profile completion (3 key steps)
    steps = {
        "has_resume": bool(resume),
        "has_picture": bool(user_profile.profile_picture),
        "has_bio": bool(user_profile.bio),
    }
    steps_completed = sum(steps.values())
    completion_percentage = int((steps_completed / 3) * 100)

    # Suggested jobs — only if resume + skills exist
    if resume and resume.skills.exists():
        suggested_jobs = match_jobs_for_user(request.user)[:10]
    else:
        suggested_jobs = []

    # Format user join date
    formatted_joined_date = (
        request.user.date_joined.strftime("%b %d, %Y") if request.user.date_joined else None
    )

    # Render the dashboard template
    return render(request, 'dashboard/user_dashboard.html', {
        'profile': user_profile,
        'resume': resume,
        'applications': applications,
        'completion_percentage': completion_percentage,
        'steps_completed': steps_completed,
        'joined_date': formatted_joined_date,
        'suggested_jobs': suggested_jobs,
        'imported_resume': imported_resume,
        'education_entries': education_entries,   
        'experience_entries': experience_entries
    })

@login_required
def saved_jobs_view(request):
    saved_jobs = SavedJob.objects.filter(user=request.user).select_related('job')
    return render(request, 'dashboard/saved_jobs.html', {'saved_jobs': saved_jobs})

@login_required
def matched_jobs_view(request):
    matched_jobs = match_jobs_for_user(request.user)
    return render(request, 'dashboard/matched_jobs.html', {
        'matches': matched_jobs
    })


@login_required
def employer_dashboard(request):
    jobs = Job.objects.filter(employer=request.user.username)
    matched_seekers = UserProfile.objects.all()[:3]  # Replace with real logic
    notifications = []  # Optional logic later
    interviews = []     # Optional logic later

    # --- Analytics Logic ---
    one_week_ago = timezone.now() - timedelta(days=7)
    recent_applications = Application.objects.filter(job__in=jobs, created_at__gte=one_week_ago)

    latest_job = jobs.order_by('-id').first()  # Or use created_at if available

    analytics = {
        "total_applicants": Application.objects.filter(job__employer=request.user).count(),
        "jobs_posted": Job.objects.filter(employer=request.user).count(),
        "active_jobs": Job.objects.filter(employer=request.user, is_active=True).count(),
        "jobs_filled": Application.objects.filter(job__employer=request.user, status="filled").count(),
    }

    return render(request, 'dashboard/employer_dashboard.html', {
        'jobs': jobs,
        'matched_seekers': matched_seekers,
        'notifications': notifications,
        'interviews': interviews,
        'analytics': analytics,
    })

@login_required
def employer_analytics(request):
    # Assume employer's username is used as the job.employer field for now
    jobs = Job.objects.filter(employer=request.user.username)

    job_data = []
    for job in jobs:
        applications = Application.objects.filter(job=job)
        job_data.append({
            'title': job.title,
            'location': job.location,
            'num_applicants': applications.count(),
        })

    return render(request, 'dashboard/employer_analytics.html', {
        'jobs': jobs,
        'job_data': job_data
    })

@login_required
def admin_dashboard(request):
    return render(request, 'dashboard/admin_dashboard.html')
