from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Job, JobSeeker, Resume, Application
from profiles.models import UserProfile
from .forms import UserSignupForm, Step1Form, Step2Form, Step3Form, Step4Form
from django.http import JsonResponse

# Home view
def home(request):
    return render(request, 'main/home.html')

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
def signup_view(request):
    if request.method == 'POST':
        user_form = UserSignupForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            login(request, user)
            return redirect('profile_step', step=1)
    else:
        user_form = UserSignupForm()
    return render(request, 'main/signup.html', {'user_form': user_form})

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
