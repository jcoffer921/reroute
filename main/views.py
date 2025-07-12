from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import traceback
from .models import Job, JobSeeker, Resume, Application
from profiles.models import UserProfile
from .forms import UserSignupForm, Step1Form, Step2Form, Step3Form, Step4Form
from django.http import JsonResponse
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  # Only for dev/testing – remove in prod
from django.contrib import messages
from django.core.mail import send_mail
import requests
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import CustomPasswordChangeForm  # make sure you’ve defined this
from blog.models import BlogPost

import json

# Home view with blog posts
def home(request):
    latest_posts = BlogPost.objects.filter(published=True).order_by('-created_at')[:3]
    return render(request, 'main/home.html', {
        'latest_posts': latest_posts,
    })

def resources_view(request):
    return render(request, 'resources/resource_list.html')


def terms_view(request):
    return render(request, 'legal/terms_and_conditions.html')

def privacy_view(request):
    return render(request, 'legal/privacy_policy.html')

def about_us(request):
    return render(request, 'main/about_us.html')

@login_required
def settings_view(request):
    password_form = CustomPasswordChangeForm(request.user)  # <-- now using custom form

    if request.method == 'POST':
        if 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(request.user, request.POST)  # <-- also use custom here
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully.")
                return redirect('settings')

        elif 'update_email' in request.POST:
            new_email = request.POST.get('email')
            if new_email:
                request.user.email = new_email
                request.user.save()
                messages.success(request, "Email updated successfully.")
                return redirect('settings')

        elif 'deactivate_account' in request.POST:
            request.user.is_active = False
            request.user.save()
            messages.warning(request, "Account deactivated. You’ve been logged out.")
            return redirect('logout')

        elif 'delete_account' in request.POST:
            request.user.delete()
            messages.error(request, "Your account has been permanently deleted.")
            return redirect('home')

    return render(request, 'main/settings.html', {
        'password_form': password_form,
    })

# Contact Us Page View
def contact_view(request):
    if request.method == "POST":
        # ----------------------------
        # 1. Extract form data
        # ----------------------------
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        organization = request.POST.get('organization')
        interest = request.POST.get('interest')
        message = request.POST.get('message')
        recaptcha_token = request.POST.get('g-recaptcha-response')

        # ----------------------------
        # 2. Verify reCAPTCHA response
        # ----------------------------
        recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
        recaptcha_data = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_token
        }
        recaptcha_response = requests.post(recaptcha_url, data=recaptcha_data).json()

        if not recaptcha_response.get('success'):
            messages.error(request, "reCAPTCHA verification failed. Please try again.")
            return redirect('contact')

        # ----------------------------
        # 3. Format the email
        # ----------------------------
        subject = f"New Contact Form Submission: {interest}"
        body = (
            f"Name: {first_name} {last_name}\n"
            f"Email: {email}\n"
            f"Phone: {phone or 'N/A'}\n"
            f"Organization: {organization or 'N/A'}\n"
            f"Interested in: {interest}\n\n"
            f"Message:\n{message}"
        )

        try:
            # ----------------------------
            # 4. Send the email
            # ----------------------------
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_RECEIVER_EMAIL],
                fail_silently=False,
            )
            messages.success(request, "Thanks for reaching out — we'll be in touch soon.")
            return redirect('contact')

        except Exception as e:
            print("Email send error:", e)
            messages.error(request, "Something went wrong. Please try again.")

    # ----------------------------
    # GET request or fallback
    # ----------------------------
    return render(request, 'main/contact_us.html', {
        'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY  # Pass to the template
    })


# Job list display
def job_list(request):
    jobs = Job.objects.all()
    return render(request, 'main/job_list.html', {'jobs': jobs})

# Match jobs to seeker skills
def match_jobs(request, seeker_id):
    seeker = JobSeeker.objects.get(id=seeker_id)
    seeker_skills = [skill.strip().lower() for skill in seeker.skills.split(",")]

    matches = Job.objects.none()
    for skill in seeker_skills:
        matches |= Job.objects.filter(tags__icontains=skill)

    matches = matches.distinct()
    return render(request, 'main/match_jobs.html', {'matches': matches})

# Sign up and redirect to profile step form
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserSignupForm
import traceback

def signup_view(request):
    if request.method == 'POST':
        try:
            user_form = UserSignupForm(request.POST, request.FILES)  # include files in case you add uploads later
            if user_form.is_valid():
                user = user_form.save(commit=False)

                # Set the password securely
                user.set_password(user_form.cleaned_data['password'])

                # Save the user
                user.save()

                # Log in the user and redirect
                login(request, user)
                return redirect('dashboard')
            else:
                print("Form validation errors:", user_form.errors)
        except Exception as e:
            print("Signup exception:", e)
            traceback.print_exc()
            # Optional: return HttpResponseServerError("Something went wrong.")
    else:
        user_form = UserSignupForm()

    return render(request, 'main/signup.html', {'user_form': user_form})


def login_view(request):
    if request.method == "GET":
        return render(request, 'main/login.html')  # ✅ Serve login page

    elif request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            next_url = data.get('next', '/dashboard/')

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return JsonResponse({'status': 'success', 'redirect': next_url})
            else:
                return JsonResponse({'status': 'fail', 'message': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'status': 'fail', 'message': 'Error during login'}, status=500)

    # Optionally handle traditional POST form logins too
    return JsonResponse({'status': 'fail', 'message': 'Unsupported request'}, status=400)

def logout_view(request):
    logout(request)
    return redirect('login')  # or redirect to 'home' or any public page

# Multi-step profile builder (example steps)
def step1(request):
    if request.method == 'POST':
        form = Step1Form(request.POST)
        if form.is_valid():
            request.session['step1'] = form.cleaned_data
            return redirect('step2')
    else:
        form = Step1Form(initial=request.session.get('step1', {}))
    return render(request, 'get_started/step1.html', {'form': form})

def step2(request):
    if request.method == 'POST':
        form = Step2Form(request.POST)
        if form.is_valid():
            request.session['step2'] = form.cleaned_data
            return redirect('step3')
    else:
        form = Step2Form(initial=request.session.get('step2', {}))
    return render(request, 'get_started/step2.html', {'form': form})

def step3(request):
    if request.method == 'POST':
        form = Step3Form(request.POST)
        if form.is_valid():
            request.session['step3'] = form.cleaned_data
            return redirect('step4')
    else:
        form = Step3Form(initial=request.session.get('step3', {}))
    return render(request, 'get_started/step3.html', {'form': form})

def step4(request):
    if request.method == 'POST':
        form = Step4Form(request.POST)
        if form.is_valid():
            request.session['step4'] = form.cleaned_data
            return redirect('home')
    else:
        form = Step4Form(initial=request.session.get('step4', {}))
    return render(request, 'get_started/step4.html', {'form': form})

# Final summary of all steps
def final_view(request):
    step1_data = request.session.get('step1', {})
    step2_data = request.session.get('step2', {})
    step3_data = request.session.get('step3', {})
    step4_data = request.session.get('step4', {})

    return render(request, 'get_started/final.html', {
        'step1': step1_data,
        'step2': step2_data,
        'step3': step3_data,
        'step4': step4_data
    })

# Optional redirect to new resume builder flow
def create_resume_redirect(request):
    return redirect('resumes:resume_contact_info')

# Preview a resume using selected template
def resume_preview(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    template_name = f"resumes/templates/{resume.template}.html" if resume.template else "resumes/templates/simple.html"
    return render(request, template_name, {'resume': resume})

# Password reset views using custom templates
class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'registration/password_reset_form.html'

class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'

class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'