# dashboard/views.py

from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

# ===== Domain imports (align to your actual apps) =====
# Jobs live in job_list; bring Job, SavedJob, Application from there for consistency.
from job_list.models import Job, SavedJob, Application
from job_list.matching import match_jobs_for_user

# Profiles & resumes
from profiles.models import UserProfile
from resumes.models import Education, Experience, Resume  # your resumes app owns these


# =========================
# Role helpers
# =========================
def is_employer(user):
    """Return True if the user is in the Employer group."""
    return user.is_authenticated and user.groups.filter(name='Employer').exists()

def is_admin(user):
    """True if user is staff or superuser (your choice to treat both as admin)."""
    return user.is_authenticated and (user.is_superuser or user.is_staff)


# =========================
# Utilities
# =========================
def extract_resume_skills(resume):
    """
    Return a list of skill strings from a resume, regardless of storage:
    - If ManyToMany: map objects → .name (or str())
    - If TextField: split by commas
    - If nothing present: []
    """
    if not resume:
        return []

    # Case A: ManyToMany-like (has .all attr)
    if hasattr(resume, "skills") and hasattr(getattr(resume, "skills"), "all"):
        return [
            (getattr(s, "name", str(s)) or "").strip()
            for s in resume.skills.all()
            if (getattr(s, "name", str(s)) or "").strip()
        ]

    # Case B: Text field
    raw = getattr(resume, "skills", "") or ""
    return [s.strip() for s in raw.split(",") if s.strip()]


# =========================
# Router / Redirect
# =========================
@login_required
def dashboard_redirect(request):
    """
    Legacy-safe: send /dashboard/ hits to the correct destination.
    Priority: Admin > Employer > User.
    """
    if is_admin(request.user):
        return redirect('dashboard:admin')      # namespaced dashboard app
    if is_employer(request.user):
        return redirect('dashboard:employer')
    return redirect('dashboard:user')


# =========================
# User Dashboard
# =========================
@login_required
def user_dashboard(request):
    """
    Loads the user's profile, resume, applications, and suggested jobs
    (only if we can detect at least one skill).
    """
    # Ensure a profile exists to avoid template conditionals blowing up
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Latest imported resume (guard in case 'is_imported' doesn't exist)
    try:
        imported_resume = (
            Resume.objects.filter(user=request.user, is_imported=True)
            .order_by("-created_at")
            .first()
        )
    except Exception:
        imported_resume = None

    # Canonical "latest" resume for other sections
    resume = Resume.objects.filter(user=request.user).order_by("-created_at").first()

    # Children of resume (OK if resume is None)
    education_entries = Education.objects.filter(resume=resume) if resume else []
    experience_entries = Experience.objects.filter(resume=resume) if resume else []

    # User's job applications
    applications = Application.objects.filter(applicant=request.user)

    # Profile completeness (MVP: 3 signals)
    steps = {
        "has_resume": bool(resume),
        "has_picture": bool(user_profile.profile_picture),
        "has_bio": bool(user_profile.bio),
    }
    steps_completed = sum(steps.values())
    completion_percentage = int((steps_completed / 3) * 100)

    # Suggested jobs: only attempt if we detect skills
    skills_list = extract_resume_skills(resume)
    suggested_jobs = match_jobs_for_user(request.user)[:10] if skills_list else []

    # Friendly join date string
    joined_date = request.user.date_joined.strftime("%b %d, %Y") if request.user.date_joined else None

    return render(request, 'dashboard/user_dashboard.html', {
        'profile': user_profile,
        'resume': resume,
        'imported_resume': imported_resume,
        'education_entries': education_entries,
        'experience_entries': experience_entries,
        'applications': applications,
        'completion_percentage': completion_percentage,
        'steps_completed': steps_completed,
        'joined_date': joined_date,
        'suggested_jobs': suggested_jobs,
    })


# =========================
# Saved & Matched Jobs
# =========================
@login_required
def saved_jobs_view(request):
    """Simple list of saved jobs for the current user."""
    saved_jobs = SavedJob.objects.filter(user=request.user).select_related('job')
    return render(request, 'dashboard/saved_jobs.html', {'saved_jobs': saved_jobs})

@login_required
def matched_jobs_view(request):
    """Render matched jobs (uses your current matching module)."""
    matched_jobs = match_jobs_for_user(request.user)
    return render(request, 'dashboard/matched_jobs.html', {'matches': matched_jobs})


# =========================
# Employer Dashboard & Analytics
# =========================
@login_required
def employer_dashboard(request):
    """
    MVP employer dashboard.
    NOTE: Your Job.employer is currently a string (username), not a FK(User).
    Until you migrate, always filter with request.user.username.
    """
    employer_username = request.user.username

    # Jobs "owned" by this employer (by username)
    jobs = Job.objects.filter(employer=employer_username).order_by('-id')

    # (Placeholder) You can replace with real seeker matching logic later
    matched_seekers = UserProfile.objects.all()[:3]
    notifications = []
    interviews = []

    # Basic analytics (safe to run with current schema)
    analytics = {
        "jobs_posted": Job.objects.filter(employer=employer_username).count(),
        "active_jobs": Job.objects.filter(employer=employer_username, is_active=True).count(),
        "total_applicants": Application.objects.filter(job__employer=employer_username).count(),
        "jobs_filled": Application.objects.filter(job__employer=employer_username, status__iexact="filled").count(),
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
    """
    Simple employer analytics page.
    """
    employer_username = request.user.username
    jobs = Job.objects.filter(employer=employer_username).order_by('-id')

    job_data = []
    for job in jobs:
        num_apps = Application.objects.filter(job=job).count()
        job_data.append({
            'title': job.title,
            'location': job.location,
            'num_applicants': num_apps,
        })

    return render(request, 'dashboard/employer_analytics.html', {
        'jobs': jobs,
        'job_data': job_data
    })


# =========================
# Admin Dashboard (custom)
# =========================
@login_required
def admin_dashboard(request):
    """
    Custom admin dashboard (separate from Django /admin/).
    Flesh out with KPIs as you go.
    """
    return render(request, 'dashboard/admin_dashboard.html')
