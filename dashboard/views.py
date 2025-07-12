from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from main.models import Job
from profiles.models import UserProfile
from resumes.models import Resume
# Update the import path below to the correct location of your Application model
# Example: from myapp.models import Application
from resumes.models import Application  # Change 'resumes' to the correct app name if needed

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_redirect(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    elif hasattr(request.user, 'employerprofile'):
        return redirect('employer_dashboard')
    else:
        return redirect('user_dashboard')


@login_required
def user_dashboard(request):
    # Get or create user profile
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Resume & applications
    resume = Resume.objects.filter(user=request.user).first()
    applications = Application.objects.filter(applicant=request.user)

    # Simple 3-step profile completion
    steps = {
        "has_resume": bool(resume),
        "has_picture": bool(user_profile.profile_picture),
        "has_bio": bool(user_profile.bio),
    }
    steps_completed = sum(steps.values())
    completion_percentage = int((steps_completed / 3) * 100)

    # Suggested jobs (based on resume skills or fallback to empty)
    suggested_jobs = []
    if resume and resume.skill_summary:
        user_skills = [skill_summary.strip().lower() for skill_summary in resume.skill_summary.split(",")]
        suggested_jobs = Job.objects.none()
        for skill in user_skills:
            suggested_jobs |= Job.objects.filter(tags__icontains=skill)
        suggested_jobs = suggested_jobs.distinct()[:10]

    # Format join date
    formatted_joined_date = request.user.date_joined.strftime("%b %d, %Y") if request.user.date_joined else None

    return render(request, 'dashboard/user_dashboard.html', {
        'profile': user_profile,
        'resume': resume,
        'applications': applications,
        'completion_percentage': completion_percentage,
        'steps_completed': steps_completed,
        'joined_date': formatted_joined_date,
        'suggested_jobs': suggested_jobs,
    })

@login_required
def employer_dashboard(request):
    return render(request, 'dashboard/employer_dashboard.html')

@login_required
def admin_dashboard(request):
    return render(request, 'dashboard/admin_dashboard.html')
