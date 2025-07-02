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

# Home view
def home(request):
    return render(request, 'main/home.html')


def dashboard(request):
    return render(request, 'profiles/dashboard.html')

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
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # ✅ Redirect to original destination if exists
            next_url = request.GET.get('next') or request.POST.get('next')
            return redirect(next_url or 'dashboard')
    return render(request, 'login.html', {'form': form})

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

# Dashboard view with profile, resume and application info
@login_required
def dashboard_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    resume = Resume.objects.filter(user=request.user).first()
    applications = Application.objects.filter(applicant=request.user)

    return render(request, 'dashboard.html', {
        'profile': profile,
        'resume': resume,
        'applications': applications,
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