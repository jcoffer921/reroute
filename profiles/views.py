# ============================
# views.py (drop-in replacement)
# ============================
from __future__ import annotations

import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST

from PIL import Image, UnidentifiedImageError

# Local imports
from .constants import US_STATES, ETHNICITY_CHOICES
from .models import UserProfile, EmployerProfile
from resumes.models import Resume
from core.models import Skill


# --------------------------------------------
# Centralized helper — single source of truth
# --------------------------------------------
def is_employer(user) -> bool:
    """Robust employer check used by views (mirrors model property)."""
    if not getattr(user, "is_authenticated", False):
        return False
    # 1) EmployerProfile present?
    if hasattr(user, 'employerprofile'):
        try:
            if user.employerprofile:  # may raise if not created yet
                return True
        except Exception:
            pass
    # 2) Group membership fallback
    try:
        return user.groups.filter(name__in=["Employer", "Employers"]).exists()
    except Exception:
        return False


@login_required
def public_profile_view(request, username):
    """
    Public-facing profile page. Only employers should access other users' profiles.
    PREVIOUS BUG: used profile.account_status == 'employer' — that field is NOT a role.
    """
    if not is_employer(request.user):
        messages.error(request, "Only employers can view applicant profiles.")
        return redirect('home')

    target_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=target_user)
    resume = Resume.objects.filter(user=target_user).first()

    return render(request, 'profiles/public_profile.html', {
        'user': target_user,
        'profile': profile,
        'resume': resume,
        'is_owner': False,
        'US_STATES': US_STATES,
        'ETHNICITY_CHOICES': ETHNICITY_CHOICES,
    })


@login_required
def user_profile_view(request):
    """Owner's own profile page."""
    profile = get_object_or_404(UserProfile, user=request.user)

    # Get most recent resume + skills as list (works with M2M)
    resume = Resume.objects.filter(user=request.user).order_by('-created_at').first()
    skill_list = [s.name for s in resume.skills.all()] if resume else []

    return render(request, 'profiles/user_profile.html', {
        'user': request.user,
        'profile': profile,
        'resume': resume,
        'skills_json': json.dumps(skill_list),
        'is_owner': True,
    })


@login_required
@csrf_protect
def multi_step_form_view(request, step=1):
    """Legacy redirect. Route to your own profile edit or view as desired."""
    return redirect('user_profile', username=request.user.username)


@csrf_exempt
@login_required
def update_profile(request):
    """AJAX endpoint to update basic profile fields safely."""
    if request.method != "POST":
        return JsonResponse({'success': False}, status=400)

    profile = get_object_or_404(UserProfile, user=request.user)

    # Birthdate parse — tolerate empty
    raw_birthdate = request.POST.get("birthdate", "").strip()
    if raw_birthdate:
        try:
            profile.birthdate = datetime.strptime(raw_birthdate, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"success": False, "error": "Invalid birthdate format"}, status=400)
    else:
        profile.birthdate = None

    # Simple scalar fields (keep existing if not present)
    for field in [
        "firstname", "lastname", "phone_number", "personal_email",
        "bio", "status", "gender",
    ]:
        if field in request.POST:
            setattr(profile, field, request.POST.get(field, getattr(profile, field)))

    profile.save()
    return JsonResponse({'success': True})


@require_POST
@login_required
def update_bio(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    profile.bio = request.POST.get('bio', '')
    profile.save()
    return redirect('user_profile', username=request.user.username)


@require_POST
@login_required
def update_personal_info(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    profile.firstname = request.POST.get('firstname', '')
    profile.lastname = request.POST.get('lastname', '')
    profile.personal_email = request.POST.get('personal_email', '')
    profile.phone_number = request.POST.get('phone_number', '')
    profile.state = request.POST.get('state', '')
    profile.city = request.POST.get('city', '')

    dob_str = request.POST.get('birthdate', '')
    try:
        profile.birthdate = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid birthdate format'}, status=400)

    profile.save()
    return JsonResponse({'success': True})


@require_POST
@login_required
def update_employment_info(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    profile.work_in_us = request.POST.get('authorized_us')
    profile.sponsorship_needed = request.POST.get('sponsorship_needed')
    profile.disability = request.POST.get('disability')
    profile.lgbtq = request.POST.get('lgbtq')
    profile.gender = request.POST.get('gender')
    profile.veteran_status = request.POST.get('veteran_status')
    profile.save()
    return JsonResponse({'success': True})


@require_POST
@login_required
def update_emergency_contact(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    profile.emergency_contact_firstname = request.POST.get("emergency_contact_firstname", "")
    profile.emergency_contact_lastname = request.POST.get("emergency_contact_lastname", "")
    profile.emergency_contact_relationship = request.POST.get("emergency_contact_relationship", "")
    profile.emergency_contact_phone = request.POST.get("emergency_contact_phone", "")
    profile.emergency_contact_email = request.POST.get("emergency_contact_email", "")
    profile.save()
    return redirect('user_profile', username=request.user.username)


@require_POST
@login_required
def update_demographics(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    profile.gender = request.POST.get("gender", "")
    profile.ethnicity = request.POST.get("ethnicity", "")
    profile.disability_explanation = request.POST.get("disability_explanation", "")
    profile.veteran_explanation = request.POST.get("veteran_explanation", "")
    profile.save()
    return redirect('user_profile', username=request.user.username)


@login_required
@require_POST
def update_skills(request):
    """Add/remove skills on the most recent resume (M2M)."""
    resume = Resume.objects.filter(user=request.user).order_by('-created_at').first()
    if not resume:
        return JsonResponse({'error': 'No resume found for this user.'}, status=404)

    # Current skills → case-insensitive dict
    existing = {s.name.lower(): s for s in resume.skills.all()}

    # Additions
    for raw in request.POST.get('add_skills', '').split(','):
        sk = raw.strip()
        if not sk:
            continue
        key = sk.lower()
        if key not in existing:
            obj, _ = Skill.objects.get_or_create(name=sk)
            existing[key] = obj

    # Removals
    for raw in request.POST.get('remove_skills', '').split(','):
        sk = raw.strip()
        if not sk:
            continue
        existing.pop(sk.lower(), None)

    # Persist as list of IDs
    resume.skills.set([s.id for s in existing.values()])
    resume.save()
    return JsonResponse({'success': True})


@login_required
def update_profile_picture(request):
    if request.method == 'POST' and 'profile_picture' in request.FILES:
        image_file = request.FILES['profile_picture']
        # Validate basic image integrity
        try:
            img = Image.open(image_file)
            img.verify()
            if img.format.lower() not in ['jpeg', 'png', 'gif', 'jpg']:
                messages.error(request, "Unsupported image format. Use JPEG, PNG, or GIF.")
                return redirect('my_profile')
        except UnidentifiedImageError:
            messages.error(request, "Invalid image file. Please upload a real image.")
            return redirect('my_profile')

        profile = request.user.profile
        profile.profile_picture = image_file
        profile.save()
        messages.success(request, "Profile picture updated successfully.")

    return redirect('my_profile')


@login_required
@require_POST
def remove_profile_picture(request):
    """
    Remove the current user's profile picture.
    - Requires POST (prevents accidental deletes via link crawlers)
    - Deletes the file from storage and clears the field
    - Shows a success/info message
    - Redirects to the correct dashboard based on role
    """
    profile = request.user.profile

    if profile.profile_picture:
        # Delete the file from storage without saving yet
        profile.profile_picture.delete(save=False)
        # Clear the field and persist to DB
        profile.profile_picture = None
        profile.save(update_fields=["profile_picture"])
        messages.success(request, "Your profile picture has been removed.")
    else:
        messages.info(request, "You don't have a profile picture set.")

    # Role-aware redirect
    return redirect('employer_dashboard' if is_employer(request.user) else 'dashboard:user_dashboard')


@login_required
def edit_personal_info(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'profiles/user_profile.html', {
        'profile': profile,
        'US_STATES': US_STATES,
    })


@login_required
def edit_emergency_contact(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'profiles/user_profile.html', {
        'profile': profile,
    })


@login_required
def edit_employment(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'profiles/user_profile.html', {
        'profile': profile,
    })


@login_required
def edit_demographics(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'profiles/user_profile.html', {
        'profile': profile,
        'ETHNICITY_CHOICES': ETHNICITY_CHOICES,
    })


@login_required
def edit_skills(request):
    """Render skills editor with M2M list (no string splitting)."""
    resume = Resume.objects.filter(user=request.user).order_by('-created_at').first()
    skills_json = json.dumps([s.name for s in resume.skills.all()]) if resume else json.dumps([])

    return render(request, 'profiles/user_profile.html', {
        'resume': resume,
        'skills_json': skills_json,
    })
