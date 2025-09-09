# profiles/views.py — slide-in friendly, JSON-first
from __future__ import annotations

import json
from datetime import datetime
from PIL import Image, UnidentifiedImageError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.safestring import mark_safe

from PIL import Image, UnidentifiedImageError

from .models import UserProfile

# Optional integrations — guarded to avoid hard crashes if app not installed
try:
    from resumes.models import Resume
except Exception:
    Resume = None

try:
    from core.models import Skill
except Exception:
    Skill = None

# Optional constants (guarded)
try:
    from .constants import US_STATES, ETHNICITY_CHOICES
except Exception:
    US_STATES, ETHNICITY_CHOICES = [], []


# ----------------------------- JSON helpers -----------------------------
def json_ok(updated=None, message=None, status=200):
    payload = {"ok": True}
    if updated is not None:
        payload["updated"] = updated
    if message:
        payload["message"] = message
    return JsonResponse(payload, status=status)

def json_err(errors, status=400):
    return JsonResponse({"ok": False, "errors": errors}, status=status)

def is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"

def is_employer(user) -> bool:
    """
    Public helper used by other apps (e.g., main.views).
    Checks if the user belongs to the Employer group(s).
    Kept defensive so it never crashes if groups aren't set up.
    """
    if not getattr(user, "is_authenticated", False):
        return False
    try:
        return user.groups.filter(name__in=["Employer", "Employers"]).exists()
    except Exception:
        return False


# ----------------------------- Public profile ---------------------------
@login_required
def public_profile_view(request, username: str):
    # Only employers should view others' profiles (adjust logic as you like)
    if not is_employer(request.user):
        messages.error(request, "Only employers can view applicant profiles.")
        return redirect("home")

    target_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=target_user)
    resume = Resume.objects.filter(user=target_user).order_by("-created_at").first() if Resume else None

    return render(
        request,
        "profiles/public_profile.html",
        {
            "viewed_user": target_user,
            "profile": profile,
            "resume": resume,
            "is_owner": False,
        },
    )


# ----------------------------- Own profile ------------------------------
@login_required
def user_profile_view(request):
    """
    Own profile view.
    - Produces `skills_json` for the slide-out panel:
      {"selected": [...], "suggested": [...]}
    - Supports both TextField (comma-separated) and ManyToMany for resume.skills.
    """
    # Get the user’s profile (404 if the profile truly doesn’t exist)
    profile = get_object_or_404(UserProfile, user=request.user)

    # Latest resume for this user (ok if None)
    resume = Resume.objects.filter(user=request.user).order_by("-created_at").first()

    # ---- Build selected skills ----
    selected_skills = []

    if resume:
        # Case A: ManyToMany-like (has .all attribute)
        if hasattr(resume, "skills") and hasattr(getattr(resume, "skills"), "all"):
            # Convert related objects to plain strings
            selected_skills = [str(getattr(s, "name", s)).strip()
                               for s in resume.skills.all()
                               if str(getattr(s, "name", s)).strip()]
        else:
            # Case B: TextField (comma-separated)
            raw = getattr(resume, "skills", "") or ""
            selected_skills = [s.strip() for s in raw.split(",") if s.strip()]

    # ---- Suggested skills (fallback list; replace with DB-driven if you have one) ----
    suggested_skills = [
        "Customer Service", "Sales", "Scheduling",
        "Microsoft Excel", "Python", "Teamwork",
        "Communication", "Problem Solving"
    ]

    # Deduplicate + don’t suggest ones already selected
    selected_set = {s.lower() for s in selected_skills}
    suggested_clean = [s for s in suggested_skills if s.lower() not in selected_set]

    # JSON the shape the front-end expects
    skills_payload = {
        "selected": selected_skills,
        "suggested": suggested_clean
    }
    # mark_safe because you render with {{ skills_json|safe }} into a <script> tag
    skills_json = mark_safe(json.dumps(skills_payload))

    context = {
        "user": request.user,
        "profile": profile,
        "resume": resume,
        "US_STATES": US_STATES,
        "ETHNICITY_CHOICES": ETHNICITY_CHOICES,
        "skills_json": skills_json,
        "is_owner": True,  # you’re in the owner view
    }
    return render(request, "profiles/user_profile.html", context)

# ----------------------------- Updates: Personal ------------------------
@require_POST
@login_required
def update_personal_info(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    first = (request.POST.get("firstname") or "").strip()
    last  = (request.POST.get("lastname") or "").strip()
    phone = (request.POST.get("phone_number") or "").strip()
    email = (request.POST.get("personal_email") or "").strip()
    state = (request.POST.get("state") or "").strip()
    city  = (request.POST.get("city") or "").strip()

    errors = {}
    if not first: errors["firstname"] = "First name is required."
    if not last:  errors["lastname"]  = "Last name is required."

    if errors:
        return json_err(errors) if is_ajax(request) else redirect("my_profile")

    # Use Django User as the source of truth for names
    u = request.user
    u.first_name, u.last_name = first, last
    u.save(update_fields=["first_name", "last_name"])

    # Mirror to profile if you keep duplicates
    if hasattr(profile, "firstname"): profile.firstname = first
    if hasattr(profile, "lastname"):  profile.lastname  = last
    profile.phone_number = phone
    profile.personal_email = email
    profile.state = state
    profile.city = city
    profile.save()

    updated = {
        "full_name": f"{first} {last}",
        "initials": (first[:1] + last[:1]).upper(),
        "phone_number": phone, "personal_email": email, "state": state, "city": city,
    }
    return json_ok(updated) if is_ajax(request) else redirect("my_profile")


# ----------------------------- Updates: Emergency -----------------------
@require_POST
@login_required
def update_emergency_contact(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    data = {
      "emergency_contact_firstname": (request.POST.get("emergency_contact_firstname") or "").strip(),
      "emergency_contact_lastname":  (request.POST.get("emergency_contact_lastname") or "").strip(),
      "emergency_contact_relationship": (request.POST.get("emergency_contact_relationship") or "").strip(),
      "emergency_contact_phone": (request.POST.get("emergency_contact_phone") or "").strip(),
      "emergency_contact_email": (request.POST.get("emergency_contact_email") or "").strip(),
    }

    errors = {}
    if not data["emergency_contact_firstname"]: errors["emergency_contact_firstname"] = "Required."
    if not data["emergency_contact_lastname"]:  errors["emergency_contact_lastname"]  = "Required."
    if errors:
      return json_err(errors) if is_ajax(request) else redirect("my_profile")

    for k, v in data.items():
      setattr(profile, k, v)
    profile.save()

    updated = {**data, "emergency_contact_fullname": f"{data['emergency_contact_firstname']} {data['emergency_contact_lastname']}".strip()}
    return json_ok(updated) if is_ajax(request) else redirect("my_profile")


# ----------------------------- Updates: Employment ----------------------
@require_POST
@login_required
def update_employment_info(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    fields = ["authorized_us", "sponsorship_needed", "disability", "veteran_status", "gender", "status"]
    for f in fields:
        if f in request.POST:
            setattr(profile, f, request.POST.get(f))
    profile.save()

    updated = {f: getattr(profile, f, "") for f in fields}
    return json_ok(updated) if is_ajax(request) else redirect("my_profile")


# ----------------------------- Updates: Demographics --------------------
@require_POST
@login_required
def update_demographics(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    payload = {
        "gender": (request.POST.get("gender") or "").strip(),
        "ethnicity": (request.POST.get("ethnicity") or "").strip(),
        "race": (request.POST.get("race") or "").strip(),
        "disability_explanation": (request.POST.get("disability_explanation") or "").strip(),
        "veteran_explanation": (request.POST.get("veteran_explanation") or "").strip(),
    }

    for k, v in payload.items():
        if hasattr(profile, k):
            setattr(profile, k, v)
    profile.save()

    updated = {
        **payload,
        "pill_text": ", ".join([x for x in [payload["gender"], payload["ethnicity"], payload["race"]] if x]),
    }
    return json_ok(updated) if is_ajax(request) else redirect("my_profile")


# ----------------------------- Updates: Bio -----------------------------
@require_POST
@login_required
def update_bio(request):
    if request.method != "POST":
        return redirect("my_profile")
    profile = get_object_or_404(UserProfile, user=request.user)
    bio = (request.POST.get("bio") or "").strip()
    profile.bio = bio
    profile.save()
    return json_ok({"bio": bio}) if is_ajax(request) else redirect("my_profile")


# ----------------------------- Updates: Skills (Resume M2M) ------------
@require_POST
@login_required
def update_skills(request):
    if not (Resume and Skill):
        return json_err({"form": "Resume/Skill models are not available."}, status=501)

    resume = Resume.objects.filter(user=request.user).order_by("-created_at").first()
    if not resume:
        return json_err({"form": "No resume found."}, status=404)

    existing = {s.name.lower(): s for s in resume.skills.all()}

    # Add
    for raw in (request.POST.get("add_skills") or "").split(","):
        name = raw.strip()
        if not name: continue
        key = name.lower()
        if key not in existing:
            obj, _ = Skill.objects.get_or_create(name=name)
            existing[key] = obj

    # Remove
    for raw in (request.POST.get("remove_skills") or "").split(","):
        name = raw.strip()
        if not name: continue
        existing.pop(name.lower(), None)

    resume.skills.set([s.id for s in existing.values()])
    skills_sorted = sorted((s.name for s in existing.values()), key=str.lower)
    return json_ok({"skills": skills_sorted}) if is_ajax(request) else redirect("my_profile")


# ----------------------------- Profile picture -------------------------
@login_required
def update_profile_picture(request):
    """
    Handle profile picture upload.
    - Validates image header via Pillow.
    - Saves to UserProfile.profile_picture.
    - On non-AJAX, redirects back to /profile/.
    """
    if request.method == "POST" and "profile_picture" in request.FILES:
        image_file = request.FILES["profile_picture"]
        try:
            img = Image.open(image_file)
            img.verify()  # quick header check
            if img.format and img.format.lower() not in {"jpeg", "jpg", "png", "gif"}:
                messages.error(request, "Unsupported image format. Use JPEG, PNG, or GIF.")
                return redirect("my_profile")
        except UnidentifiedImageError:
            messages.error(request, "Invalid image file. Please upload a real image.")
            return redirect("my_profile")

        profile = get_object_or_404(UserProfile, user=request.user)
        profile.profile_picture = image_file
        profile.save()
        messages.success(request, "Profile picture updated successfully.")
    return redirect("my_profile")


@login_required
def remove_profile_picture(request):
    """
    Remove current user's profile picture and return to profile.
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.profile_picture:
        profile.profile_picture.delete(save=False)
        profile.profile_picture = None
        profile.save(update_fields=["profile_picture"])
        messages.success(request, "Your profile picture has been removed.")
    else:
        messages.info(request, "You don't have a profile picture set.")
    return redirect("my_profile")


# ----------------------------- Onboarding Final (example) ---------------
@login_required
def final_view(request):
    """
    Example of logging profile completion when the user lands here.
    If you already have a final step view, add the same track_event call there.
    """
    try:
        from core.utils.analytics import track_event
        track_event(event_type='profile_completed', request=request, metadata={"source": "profiles.final_view"})
    except Exception:
        pass

    # Optionally flash a message or update state before redirect
    return redirect("profiles:my_profile")
