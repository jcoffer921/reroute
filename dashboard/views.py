# dashboard/views.py

from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.contrib import messages



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
    """Render matched jobs with optional ZIP/radius filters and overlap badges."""
    origin_zip = (request.GET.get('zip') or '').strip() or None
    try:
        radius = int(request.GET.get('radius') or 25)
    except ValueError:
        radius = 25

    matched_jobs = match_jobs_for_user(request.user, origin_zip=origin_zip, radius=radius)

    # Compute skill-overlap badges per job
    resume = Resume.objects.filter(user=request.user).order_by('-created_at').first()
    overlap_by_job: dict[int, list[str]] = {}
    if resume and resume.skills.exists():
        user_skills = {s.name.strip().lower(): s.name for s in resume.skills.all()}
        for job in matched_jobs:
            job_skills = {s.name.strip().lower(): s.name for s in job.skills_required.all()}
            overlap_keys = set(user_skills.keys()) & set(job_skills.keys())
            overlap_by_job[job.id] = [job_skills[k] for k in overlap_keys]

    items = [
        {"job": job, "overlap": overlap_by_job.get(job.id, [])}
        for job in matched_jobs
    ]

    return render(request, 'dashboard/matched_jobs.html', {
        'items': items,
        'selected_zip': origin_zip or '',
        'selected_radius': radius,
    })


# =========================
# Employer Dashboard & Analytics
# =========================
@login_required
def employer_dashboard(request):
    """
    MVP employer dashboard.
    Job.employer is a ForeignKey to User, so filter directly with request.user.
    """
    employer_user = request.user

    # Jobs "owned" by this employer
    jobs = Job.objects.filter(employer=employer_user).order_by('-id')

    # Match candidates to this employer's jobs (top few per job)
    from job_list.matching import match_seekers_for_employer
    matched_seekers = match_seekers_for_employer(employer_user, limit_per_job=3)[:9]
    notifications = []
    interviews = []

    # Basic analytics (safe to run with current schema)
    analytics = {
        "jobs_posted": Job.objects.filter(employer=employer_user).count(),
        "active_jobs": Job.objects.filter(employer=employer_user, is_active=True).count(),
        "total_applicants": Application.objects.filter(job__employer=employer_user).count(),
        # Interpret "filled" as accepted offers in current schema
        "jobs_filled": Application.objects.filter(job__employer=employer_user, status__iexact="accepted").count(),
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
    # Job.employer is a FK to User, so filter by the user object
    jobs = Job.objects.filter(employer=request.user).order_by('-id')

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
@staff_member_required
def admin_dashboard(request):
    """
    Custom admin dashboard (separate from Django /admin/).
    Flesh out with KPIs as you go.
    """
    # Import models
    from django.contrib.auth.models import User
    from job_list.models import Job, Application
    from resumes.models import Resume
    from profiles.models import UserProfile, EmployerProfile

    # Stats
    user_count = User.objects.count()
    # Count employers by EmployerProfile presence (authoritative when table exists)
    try:
        employer_count = EmployerProfile.objects.count()
    except Exception:
        # Fallback: count users in Employer group(s) if EmployerProfile table is missing
        try:
            employer_count = User.objects.filter(groups__name__in=["Employer", "Employers"]).distinct().count()
        except Exception:
            employer_count = 0
    job_count = Job.objects.count()
    application_count = Application.objects.count()
    resume_count = Resume.objects.count()

    # Last 30 days activity for charts
    today = now().date()
    last_30 = [today - timedelta(days=i) for i in range(29, -1, -1)]

    users_by_day = [
        User.objects.filter(date_joined__date=day).count() for day in last_30
    ]
    jobs_by_day = [
        Job.objects.filter(created_at__date=day).count() for day in last_30
    ]

    # Recent activity (last 7 days)
    seven_days_ago = now() - timedelta(days=7)
    new_users = User.objects.filter(date_joined__gte=seven_days_ago).count()
    new_jobs = Job.objects.filter(created_at__gte=seven_days_ago).count()
    new_applications = Application.objects.filter(submitted_at__gte=seven_days_ago).count()

    # Flagged jobs queue
    flagged_jobs = Job.objects.filter(is_flagged=True)

    context = {
        "user_count": user_count,
        "employer_count": employer_count,
        "job_count": job_count,
        "application_count": application_count,
        "resume_count": resume_count,
        "dates": [d.strftime("%b %d") for d in last_30],
        "users_by_day": users_by_day,
        "jobs_by_day": jobs_by_day,
        "flagged_jobs": flagged_jobs,
        "new_users": new_users,
        "new_jobs": new_jobs,
        "new_applications": new_applications,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
@staff_member_required
@require_POST
def approve_flagged_job(request, job_id: int):
    from job_list.models import Job
    job = Job.objects.filter(id=job_id).first()
    if not job:
        messages.error(request, "Job not found.")
        return redirect('dashboard:admin')

    job.is_flagged = False
    job.flagged_reason = None
    job.is_active = True
    job.save(update_fields=['is_flagged', 'flagged_reason', 'is_active'])

    messages.success(request, f"Approved and unflagged: {job.title}")
    return redirect('dashboard:admin')


@login_required
@staff_member_required
@require_POST
def remove_flagged_job(request, job_id: int):
    from job_list.models import Job
    job = Job.objects.filter(id=job_id).first()
    if not job:
        messages.error(request, "Job not found.")
        return redirect('dashboard:admin')

    # Soft-remove: deactivate the job and clear flag
    job.is_active = False
    job.is_flagged = False
    if not job.flagged_reason:
        job.flagged_reason = "Removed by admin"
    job.save(update_fields=['is_active', 'is_flagged', 'flagged_reason'])

    messages.success(request, f"Removed (deactivated): {job.title}")
    return redirect('dashboard:admin')
