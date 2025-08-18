# main/views.py
# ======================================================================
# ReRoute (Main App) Views - Consolidated & Commented
# - User & Employer auth (login/signup/logout)
# - Dashboard(s)
# - Onboarding steps (step1–step4 + final summary)
# - Jobs list & basic skill-based matching (legacy)
# - Contact form with reCAPTCHA (optional; uses settings keys)
# - Settings page (password, email, deactivate/delete)
# - Misc pages: home, terms, privacy, resources, about
# - Password reset CBVs with custom templates
# ======================================================================

from __future__ import annotations

# -----------------------------
# Django / Stdlib Imports
# -----------------------------
import json
import logging
import traceback

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate, login, logout, views as auth_views, update_session_auth_hash
)
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Group
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import NoReverseMatch, reverse
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from job_list.models import Application
from main.forms import UserSignupForm
from resumes.models import Resume
from profiles.views import is_employer


# Optional dependency for contact form reCAPTCHA
# (safe if not used)
try:
    import requests
except Exception:
    requests = None

# -----------------------------
# Local Imports
# -----------------------------
from profiles.models import EmployerProfile, UserProfile

# Try to import a custom password form; if unavailable, we use Django's default.
try:
    from .forms import CustomPasswordChangeForm as PasswordForm
except Exception:
    PasswordForm = PasswordChangeForm

# If you rely on a shared Skill list:
try:
    from core.models import Skill
except Exception:
    Skill = None  # We’ll guard usage via conditionals

logger = logging.getLogger(__name__)

# views.py

from django.shortcuts import render
import logging
from django.apps import apps

logger = logging.getLogger(__name__)

def home(request):
    """
    Homepage:
    - Show a limited number of featured and recent posts.
    - If the 'blog' app or its table isn't available, degrade gracefully.
    """
    FEATURED_LIMIT = 3
    RECENT_LIMIT   = 6

    featured_posts = []
    recent_posts   = []

    try:
        from blog.models import BlogPost
        # --- Try to get the BlogPost model dynamically to avoid import-time crashes
        BlogPost = apps.get_model('blog', 'BlogPost') if apps.is_installed('blog') else None

        if BlogPost is not None:
            # Query only if model is available; this can still raise if table is missing
            featured_posts = (
                BlogPost.objects
                .filter(published=True, featured=True)
                .order_by('-created_at')[:FEATURED_LIMIT]
            )

            recent_posts = (
                BlogPost.objects
                .filter(published=True, featured=False)
                .order_by('-created_at')[:RECENT_LIMIT]
            )
        else:
            logger.warning("Blog app not installed; rendering home without blog posts.")

    except Exception as exc:
        # Log stacktrace so you can see missing table/column or other errors in Render logs
        logger.exception("Home view failed while fetching BlogPost items: %s", exc)
        # Fall back to empty lists; template will render without posts

    # ✅ Always render with safe defaults so template never crashes
    return render(request, 'main/home.html', {
        'featured_posts': featured_posts,
        'recent_posts': recent_posts,
        'FEATURED_LIMIT': FEATURED_LIMIT,
        'RECENT_LIMIT': RECENT_LIMIT,
    })


def about_us(request):
    """Public About page."""
    return render(request, 'main/about_us.html')


def resources_view(request):
    """Public Resources index page."""
    return render(request, 'resources/resource_list.html')


def opportunities_view(request):
    """
    Public-facing job search page (filters + results).
    If your template path is different, update it here.
    """
    return render(request, 'job_list/opportunities.html')


def terms_view(request):
    """Legal: Terms & Conditions."""
    return render(request, 'legal/terms_and_conditions.html')


def privacy_view(request):
    """Legal: Privacy Policy."""
    return render(request, 'legal/privacy_policy.html')

# =========================================================================
# Contact Page w/ reCAPTCHA (optional)
# =========================================================================

def contact_view(request):
    """
    Contact form that validates Google reCAPTCHA v2/v3.
    Expects these in settings:
      - RECAPTCHA_SITE_KEY
      - RECAPTCHA_SECRET_KEY
      - CONTACT_RECEIVER_EMAIL
      - DEFAULT_FROM_EMAIL
    Template: main/contact_us.html (must render the site key on the page)
    """
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        organization = request.POST.get('organization')
        interest = request.POST.get('interest')
        message = request.POST.get('message')
        recaptcha_token = request.POST.get('g-recaptcha-response')

        # Verify reCAPTCHA if available/configured
        if requests and getattr(settings, 'RECAPTCHA_SECRET_KEY', None):
            try:
                resp = requests.post(
                    'https://www.google.com/recaptcha/api/siteverify',
                    data={'secret': settings.RECAPTCHA_SECRET_KEY, 'response': recaptcha_token},
                    timeout=6,
                ).json()
            except Exception as e:
                logger.warning(f"reCAPTCHA call failed: {e}")
                resp = {'success': False}

            if not resp.get('success'):
                messages.error(request, "reCAPTCHA verification failed. Please try again.")
                return redirect('contact')

        # Send email
        try:
            from django.core.mail import send_mail

            subject = f"New Contact Form Submission: {interest or 'General Inquiry'}"
            body = (
                f"Name: {first_name} {last_name}\n"
                f"Email: {email}\n"
                f"Phone: {phone or 'N/A'}\n"
                f"Organization: {organization or 'N/A'}\n"
                f"Interested in: {interest or 'N/A'}\n\n"
                f"Message:\n{message}"
            )
            send_mail(
                subject,
                body,
                getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                [getattr(settings, 'CONTACT_RECEIVER_EMAIL', '')],
                fail_silently=False,
            )
            messages.success(request, "Thanks for reaching out — we'll be in touch soon.")
            return redirect('contact')

        except Exception as e:
            logger.error(f"Contact email failed: {e}")
            messages.error(request, "Something went wrong. Please try again.")

    return render(request, 'main/contact_us.html', {
        'recaptcha_site_key': getattr(settings, 'RECAPTCHA_SITE_KEY', None)
    })

# =========================================================================
# Auth: USER Signup/Login/Logout
# =========================================================================

def signup_view(request):
    """
    Regular user signup.
    - Uses UserSignupForm (validates email uniqueness & password strength).
    - Logs in the user on success and redirects to dashboard (or ?next=).
    """
    # Bind POST data if present so errors re-render on the page
    user_form = UserSignupForm(request.POST or None)

    if request.method == 'POST':
        try:
            if user_form.is_valid():
                # Form.save() already hashes the password (per our form code)
                user = user_form.save()
                login(request, user)

                # Respect ?next= if provided and safe; else go to dashboard
                next_url = request.POST.get('next') or request.GET.get('next') or reverse('dashboard')
                return redirect(next_url)

            # Log validation errors to server logs (won't crash now)
            logger.info("Signup validation errors: %s", user_form.errors)
        except Exception as e:
            # Log full traceback to server logs and fall through to re-render
            logger.exception("Signup exception: %s", e)

    return render(request, 'main/signup.html', {'user_form': user_form})


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Unified user login:
      - GET: render login page
      - POST (JSON): {username/email, password, next?} -> JSON
      - POST (form): username/email + password -> redirect or re-render with error
    """

    # ---------- GET: show page ----------
    if request.method == "GET":
        return render(request, "main/login.html")

    # ---------- Helper: auth by username OR email ----------
    def auth_user(identifier: str, password: str):
        # Normalize
        identifier = (identifier or "").strip()
        password = password or ""
        if not identifier or not password:
            return None, "Username/email and password are required."

        # Resolve email -> username if needed (case-insensitive)
        u = User.objects.filter(Q(username__iexact=identifier) | Q(email__iexact=identifier)).first()
        username = u.username if u else identifier

        # Authenticate
        user = authenticate(request, username=username, password=password)
        if not user:
            return None, "Invalid credentials"
        if not user.is_active:
            return None, "This account is inactive."
        return user, None

    # ---------- Helper: compute safe redirect ----------
    def safe_dest(user, requested_next: str | None):
        """
        Prefer a safe ?next= when present; otherwise choose by role.
        Falls back to hardcoded paths if URL names aren't wired.
        """
        # 1) Safe-guard ?next=
        if requested_next and url_has_allowed_host_and_scheme(
            requested_next, allowed_hosts={request.get_host()}
        ):
            return requested_next

        # 2) Role-aware default
        try:
            name = "employer_dashboard" if is_employer(user) else "dashboard:user_dashboard"
            return reverse(name)
        except NoReverseMatch:
            # Fallback to paths if names differ locally
            return "/employer/dashboard/" if is_employer(user) else "/u/dashboard/"

    # ---------- Branch by content type ----------
    content_type = (request.headers.get("Content-Type") or "").split(";")[0].strip()

    # A) JSON/AJAX
    if content_type == "application/json":
        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"status": "fail", "message": "Invalid JSON"}, status=400)

        identifier = data.get("username") or data.get("email") or ""
        password   = data.get("password") or ""
        requested_next = data.get("next")  # may be None

        user, err = auth_user(identifier, password)
        if err:
            code = 401 if err == "Invalid credentials" else 400
            return JsonResponse({"status": "fail", "message": err}, status=code)

        login(request, user)
        return JsonResponse({
            "status": "success",
            "redirect": safe_dest(user, requested_next),  # ✅ role-aware & safe
        })

    # B) Classic form (treat blank/unknown CT as form too)
    if content_type in ("application/x-www-form-urlencoded", "multipart/form-data", ""):
        identifier = request.POST.get("username") or request.POST.get("email") or ""
        password   = request.POST.get("password") or ""
        requested_next = request.POST.get("next")  # may be None

        user, err = auth_user(identifier, password)
        if err:
            # Re-render with inline error
            return render(request, "main/login.html", {
                "error": err,
                "prefill_identifier": identifier,
                "next": requested_next,  # keep it if present
            }, status=401 if err == "Invalid credentials" else 400)

        login(request, user)
        return redirect(safe_dest(user, requested_next))

    # C) Anything else → 400
    return HttpResponseBadRequest("Unsupported Content-Type for POST.")

def logout_view(request):
    """Log out anyone (user or employer) and bounce to login."""
    logout(request)
    return redirect('login')

# =========================================================================
# Auth: EMPLOYER Signup/Login & Dashboard
# =========================================================================

def _unique_username_from_email(email: str) -> str:
    """
    Generate a unique username from email local-part, e.g., "acme" -> "acme", "acme1", ...
    Keeps it readable and avoids a second form field.
    """
    base = slugify((email or "").split("@")[0]) or "user"
    username = base
    i = 1
    while User.objects.filter(username__iexact=username).exists():
        i += 1
        username = f"{base}{i}"
    return username

def _safe_redirect(default_name: str, default_path: str = "/"):
    try:
        return reverse(default_name)
    except NoReverseMatch:
        return default_path

@csrf_protect
@require_http_methods(["GET", "POST"])
def employer_signup_view(request):
    """
    Create an employer account + company profile.
    - Requires: first_name, last_name, email, password1, password2, company_name
    - Optional: website, description
    - Side effects: creates EmployerProfile, adds Employer group, logs in user
    """
    if request.method == "GET":
        return render(request, "main/employer_signup.html")

    # ---- Collect fields from POST ----
    first_name   = (request.POST.get("first_name") or "").strip()
    last_name    = (request.POST.get("last_name") or "").strip()
    email        = (request.POST.get("email") or "").strip().lower()
    password1    = request.POST.get("password1") or ""
    password2    = request.POST.get("password2") or ""
    company_name = (request.POST.get("company_name") or "").strip()
    website      = (request.POST.get("website") or "").strip()
    description  = (request.POST.get("description") or "").strip()
    agree        = request.POST.get("agree_terms") == "1"

    # ---- Basic validation ----
    errors = {}
    if not first_name:   errors["first_name"] = "First name is required."
    if not last_name:    errors["last_name"] = "Last name is required."
    if not email:        errors["email"] = "Email is required."
    if not company_name: errors["company_name"] = "Company name is required."
    if not password1:    errors["password1"] = "Password is required."
    if password1 and password1 != password2:
        errors["password2"] = "Passwords do not match."
    if not agree:
        errors["agree_terms"] = "You must agree to the Terms and Privacy Policy."

    # Uniqueness checks (email unique; username auto-generated later)
    if email and User.objects.filter(email__iexact=email).exists():
        errors["email"] = "An account with this email already exists."

    # Password validation (Django’s built-in validators)
    if password1 and password1 == password2:
        try:
            validate_password(password1)
        except ValidationError as ve:
            errors["password1"] = " ".join(ve.messages)

    if errors:
        # Re-render with inline field errors and keep safe prefill values
        return render(request, "main/employer_signup.html", {
            "errors": errors,
            "prefill": {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "company_name": company_name,
                "website": website,
                "description": description,
            }
        }, status=400)

    # ---- Create user + employer profile ----
    username = _unique_username_from_email(email)
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password1,
        first_name=first_name,
        last_name=last_name,
    )

    # Create EmployerProfile (signals aren’t needed here)
    EmployerProfile.objects.create(
        user=user,
        company_name=company_name,
        website=website,
        description=description,
    )

    # Optional: add to Employer group so permissions stay tidy
    try:
        employer_group, _ = Group.objects.get_or_create(name="Employer")
        user.groups.add(employer_group)
    except Exception:
        # Don’t block signup on group issues
        pass

    # Login and redirect to employer dashboard
    login(request, user)
    dest = _safe_redirect("employer_dashboard", "/employer/dashboard/")
    return redirect(dest)


@csrf_protect
@require_http_methods(["GET", "POST"])
def employer_login_view(request):
    """
    Employer-only login that supports JSON + classic form.
    - Auth by username OR email (case-insensitive)
    - Requires 'is_employer(user)' (EmployerProfile OR Employer group)
    - Honors ?next= only if safe; otherwise goes to employer dashboard
    """

    # --- helpers (same as you have) ---
    def auth_employer(identifier: str, password: str):
        identifier = (identifier or "").strip()
        password = password or ""
        if not identifier or not password:
            return None, "Username/email and password are required."

        u = User.objects.filter(Q(username__iexact=identifier) | Q(email__iexact=identifier)).first()
        username_for_auth = u.username if u else identifier

        user = authenticate(request, username=username_for_auth, password=password)
        if not user:
            return None, "Invalid credentials"
        if not user.is_active:
            return None, "This account is inactive."
        if not is_employer(user):  # EmployerProfile OR Employer group
            return None, "This account is not an employer."
        return user, None

    def safe_dest_employer(requested_next):
        if requested_next and url_has_allowed_host_and_scheme(requested_next, {request.get_host()}):
            return requested_next
        try:
            return reverse("employer_dashboard")
        except NoReverseMatch:
            return "/employer/dashboard/"

    # --- Branch: try JSON first; otherwise treat as form ---
    ctype = (request.headers.get("Content-Type") or "").split(";")[0].strip()
    is_json = ctype == "application/json"

    if is_json:
        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            # 👇 Fallback to form-style handling instead of 400
            is_json = False

    if is_json:
        identifier   = (data.get("username") or data.get("email") or "").strip()
        password     = data.get("password") or ""
        requested_next = data.get("next")

        user, err = auth_employer(identifier, password)
        if err:
            code = 401 if err == "Invalid credentials" else (403 if err == "This account is not an employer." else 400)
            return JsonResponse({"status": "fail", "message": err}, status=code)

        login(request, user)
        return JsonResponse({"status": "success", "redirect": safe_dest_employer(requested_next)})

    # --- Form (or unknown content-type): never 400 here ---
    identifier   = request.POST.get("username") or request.POST.get("email") or ""
    password     = request.POST.get("password") or ""
    requested_next = request.POST.get("next")

    user, err = auth_employer(identifier, password)
    if err:
        return render(request, "main/employer_login.html", {
            "error": err,
            "prefill_identifier": identifier,
        })

    login(request, user)
    return redirect(safe_dest_employer(requested_next))

@login_required
def employer_dashboard_view(request):
    """
    Basic employer dashboard gate:
    - Only members of 'Employer' group can enter
    Template: employers/dashboard.html
    """
    if not request.user.groups.filter(name='Employer').exists():
        return HttpResponseForbidden("Access denied: Employers only.")
    return render(request, 'dashboard/employer_dashboard.html')


# =========================================================================
# User Dashboard + Settings
# =========================================================================

def dashboard(request):
    """
    Simple user dashboard view.
    Template: profiles/dashboard.html
    """
    return render(request, 'profiles/dashboard.html')


@login_required
def dashboard_view(request):
    """
    If another part of the code imports `dashboard_view`, keep this for compatibility.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    resume = Resume.objects.filter(user=request.user).first()
    applications = Application.objects.filter(applicant=request.user)

    return render(request, 'dashboard.html', {
        'profile': profile,
        'resume': resume,
        'applications': applications,
    })


@login_required
def settings_view(request):
    """
    Unified settings screen for:
    - Change password (uses CustomPasswordChangeForm if present)
    - Update email
    - Deactivate or delete account
    Template: main/settings.html
    """
    password_form = PasswordForm(request.user)

    if request.method == 'POST':
        # Change Password
        if 'change_password' in request.POST:
            password_form = PasswordForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully.")
                return redirect('settings')

        # Update Email
        elif 'update_email' in request.POST:
            new_email = request.POST.get('email')
            if new_email:
                request.user.email = new_email
                request.user.save()
                messages.success(request, "Email updated successfully.")
                return redirect('settings')

        # Deactivate
        elif 'deactivate_account' in request.POST:
            request.user.is_active = False
            request.user.save()
            messages.warning(request, "Account deactivated. You've been logged out.")
            return redirect('logout')

        # Delete
        elif 'delete_account' in request.POST:
            request.user.delete()
            messages.error(request, "Your account has been permanently deleted.")
            return redirect('home')

    return render(request, 'main/settings.html', {'password_form': password_form})

# =========================================================================
# Resume Helpers
# =========================================================================

def create_resume_redirect(request):
    """
    Temporary redirect into your resumes app flow.
    Update the namespace/path if needed.
    """
    return redirect('resumes:resume_contact_info')

def resume_preview(request, resume_id: int):
    """
    Render a resume by template selection stored on the model.
    NOTE: This assumes `Resume` has a `template` field. If not, adjust accordingly.
    """
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    template_name = f"resumes/templates/{getattr(resume, 'template', '')}.html" if getattr(resume, 'template', None) else "resumes/templates/simple.html"
    return render(request, template_name, {'resume': resume})

def get_skills_json(request):
    """
    Returns a JSON list of skill names from the `core.Skill` model.
    If `core` app isn’t available, returns an empty list.
    """
    if Skill is None:
        return JsonResponse([], safe=False)
    skills = list(Skill.objects.values_list('name', flat=True))
    return JsonResponse(skills, safe=False)

# =========================================================================
# Password Reset (Custom Templates)
# =========================================================================

class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'registration/password_reset_form.html'


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'


# =========================================================================
# Dev-only Utilities
# =========================================================================

def dev_auto_login_user(request):
    """
    TEMP: Automatically logs in a hardcoded regular user.
    Use ONLY for development testing.
    """
    user = authenticate(username='testuser', password='TestPass123!')
    if user:
        login(request, user)
        return redirect('dashboard')
    return redirect('login')


def dev_create_test_user():
    """
    Creates a hardcoded user account for development.
    Includes group assignment for "User".
    """
    print("🔍 Creating test user account...")

    user_group, created = Group.objects.get_or_create(name='User')
    if created:
        print(f"✅ User group created (ID: {user_group.id})")
    else:
        print("ℹ️ User group already exists.")

    if User.objects.filter(username='testuser').exists():
        user = User.objects.get(username='testuser')
        print("ℹ️ Test user already exists.")
    else:
        user = User.objects.create_user(
            username='testuser',
            email='user@example.com',
            password='TestPass123!'
        )
        user.first_name = "Test"
        user.last_name = "User"
        user.save()
        print("✅ Test user created.")

    if not user.groups.filter(name='User').exists():
        user.groups.add(user_group)
        print("✅ User group assigned.")
    else:
        print("ℹ️ User already in group.")

    print("🎯 Test user account ready.")

def dev_auto_login_employer(request):
    """
    TEMP: Automatically logs in a hardcoded employer.
    Use ONLY for development testing.
    """
    employer = authenticate(username='testemployer', password='TestPass123!')
    if employer:
        login(request, employer)
        return redirect('/employer/dashboard/')
    return redirect('employer_login')


def dev_create_test_employer():
    """
    Creates a hardcoded employer account for development.
    Includes group assignment for "Employer".
    """
    print("🔍 Creating test employer account...")

    employer_group, created = Group.objects.get_or_create(name='Employer')
    if created:
        print(f"✅ Employer group created (ID: {employer_group.id})")
    else:
        print("ℹ️ Employer group already exists.")

    if User.objects.filter(username='testemployer').exists():
        employer_user = User.objects.get(username='testemployer')
        print("ℹ️ Test employer already exists.")
    else:
        employer_user = User.objects.create_user(
            username='testemployer',
            email='employer@example.com',
            password='TestPass123!'
        )
        employer_user.first_name = "Test"
        employer_user.last_name = "Employer"
        employer_user.save()
        print("✅ Test employer created.")

    if not employer_user.groups.filter(name='Employer').exists():
        employer_user.groups.add(employer_group)
        print("✅ Employer group assigned.")
    else:
        print("ℹ️ Employer already in group.")

    print("🎯 Test employer account ready.")