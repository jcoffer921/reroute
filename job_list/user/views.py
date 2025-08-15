# job_list/user/views.py

from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse

from job_list.models import Job, Application, SavedJob
from job_list.utils.geo import is_within_radius  # expects (origin_zip, target_zip, radius_mi)
from resumes.models import Resume
from django.contrib.auth.models import User

from core.models import Skill


import logging
logger = logging.getLogger(__name__)  # Set up logger for this module

# ---------- Browse jobs with real filters ----------
def opportunities_view(request):
    """
    Filters:
      - q: keyword search in title/description/requirements
      - type=full_time|part_time|... (repeats allowed)
      - zip=19104 (optional) + radius=25 (miles, optional; default 25)
    """
    jobs_qs = Job.objects.filter(is_active=True).select_related('employer').prefetch_related('skills_required')

    # --- Keyword search across key fields ---
    q = (request.GET.get('q') or "").strip()
    if q:
        tokens = [t for t in q.split() if t]
        for t in tokens:
            jobs_qs = jobs_qs.filter(
                Q(title__icontains=t) |
                Q(description__icontains=t) |
                Q(requirements__icontains=t)
            )

    # --- Job type filter (use the job_type field, not tags regex) ---
    job_types = request.GET.getlist('type')
    if job_types:
        jobs_qs = jobs_qs.filter(job_type__in=job_types)

    # --- Optional radius filter by ZIP ---
    user_zip = (request.GET.get('zip') or "").strip()
    radius = request.GET.get('radius')
    try:
        radius = int(radius) if radius not in (None, "") else 25
    except ValueError:
        radius = 25

    # If using distance, filter in Python; otherwise keep queryset for DB ordering
    if user_zip:
        jobs_in_radius = []
        for job in jobs_qs:
            if job.zip_code and is_within_radius(user_zip, job.zip_code, radius):
                jobs_in_radius.append(job)
        jobs = jobs_in_radius
    else:
        jobs = list(jobs_qs.order_by('-created_at'))

    # --- Saved flags for the current user ---
    saved_job_ids = set()
    if request.user.is_authenticated:
        saved_job_ids = set(
            SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True)
        )

    return render(request, 'job_list/user/opportunities.html', {
        'jobs': jobs,
        'saved_job_ids': saved_job_ids,
        'request': request,
    })

@require_POST
@login_required
def toggle_saved_job(request):
    job_id = request.POST.get('job_id')
    job = Job.objects.filter(id=job_id).first()

    if not job:
        logger.warning(f"[❌] Job ID {job_id} not found. User: {request.user}")
        return JsonResponse({'error': 'Job not found'}, status=404)

    logger.info(f"[🔁] Toggle save called for job {job_id} by user {request.user}")

    # Try to get or create the saved job entry
    saved, created = SavedJob.objects.get_or_create(user=request.user, job=job)

    if not created:
        saved.delete()
        logger.info(f"[🗑️] Job {job_id} unsaved by user {request.user}")
        return JsonResponse({'status': 'unsaved'})

    logger.info(f"[✅] Job {job_id} saved by user {request.user}")
    return JsonResponse({'status': 'saved'})

# View details for a specific job
def job_detail_view(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'job_list/user/job_detail.html', {'job': job})

# Apply to a job
@require_POST
@login_required
def apply_to_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    profile_url = request.build_absolute_uri(
        reverse('public_profile', kwargs={'username': request.user.username})
    )

    # 🔒 Resume required
    resume = Resume.objects.filter(user=request.user).first()
    if not resume or not resume.file:
        messages.warning(request, "🚫 You need to upload a resume before applying. Please go to your dashboard and upload one.")
        return redirect('dashboard')  # Or to resume upload page

    # ✅ Prevent duplicate applications
    if Application.objects.filter(applicant=request.user, job=job).exists():
        messages.warning(request, "You already applied.")
        return redirect('job_detail', job_id=job.id)

    # ✅ Create application
    Application.objects.create(applicant=request.user, job=job)

    # 📧 Notify employer by email
    send_mail(
        subject=f"New Application: {job.title}",
        message=(
            f"{request.user.username} just applied to your job listing: {job.title}.\n\n"
            f"📄 View their profile: {profile_url}\n\n"
            "You can review their resume, background, and application status from your dashboard."
        ),
        from_email="noreply@reroutejobs.com",
        recipient_list=[job.employer.email],
        fail_silently=True,
    )

    messages.success(request, "Your application was submitted successfully!")
    return redirect('job_detail', job_id=job.id)

# ---------- Scored matching ----------
def match_jobs(request, seeker_id):
    """
    Score = (skill overlap %) * 70
            + distance bonus (within 25mi: +20, 25-50: +10)
            + recency bonus (last 14d: +10)
    Returns jobs ordered by score desc.
    """
    user = get_object_or_404(User, id=seeker_id)
    resume = Resume.objects.filter(user=user).order_by('-created_at').first()

    if not resume:
        return render(request, 'job_list/user/match_jobs.html', {'matches': []})

    # Use the M2M from Resume -> Skill
    seeker_skills = {s.name.strip().lower() for s in resume.skills.all()}
    if not seeker_skills:
        return render(request, 'job_list/user/match_jobs.html', {'matches': []})

    # Optional location filter
    origin_zip = (request.GET.get('zip') or "").strip()
    radius = request.GET.get('radius')
    try:
        radius = int(radius) if radius not in (None, "") else 25
    except ValueError:
        radius = 25

    matches = []
    for job in Job.objects.filter(is_active=True).prefetch_related('skills_required').select_related('employer'):
        job_skills = {s.name.strip().lower() for s in job.skills_required.all()}
        if not job_skills:
            continue

        # --- Skill overlap (dominant factor) ---
        overlap = seeker_skills & job_skills
        if not overlap:
            continue
        overlap_pct = len(overlap) / max(len(job_skills), 1)  # % of job needs covered
        score = overlap_pct * 70

        # --- Distance bonus (if zip provided) ---
        if origin_zip and job.zip_code:
            try:
                if is_within_radius(origin_zip, job.zip_code, 25):
                    score += 20
                elif is_within_radius(origin_zip, job.zip_code, 50):
                    score += 10
            except Exception:
                # If geocoder fails, just skip distance bonus
                pass

        # --- Recency bonus ---
        try:
            from django.utils import timezone
            if (timezone.now() - job.created_at).days <= 14:
                score += 10
        except Exception:
            pass

        matches.append((score, job, list(overlap)))

    # Order by score desc and pass overlap to template if needed
    matches.sort(key=lambda t: t[0], reverse=True)
    ordered_jobs = [m[1] for m in matches]

    return render(request, 'job_list/user/match_jobs.html', {
        'matches': ordered_jobs,
        'debug_scores': matches[:10],  # optional: remove in prod
    })