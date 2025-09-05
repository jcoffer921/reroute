# views.py
from io import BytesIO
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from weasyprint import HTML

from profiles.models import UserProfile
from core.constants import RELATABLE_SKILLS
from core.models import Skill

from .models import (
    Resume, ContactInfo, Education, Experience,
    EducationEntry, ExperienceEntry
)
from .forms import (
    ContactInfoForm, EducationForm, EducationFormSet,
    ExperienceForm, ExperienceFormSet, SkillForm, ResumeImportForm
)
from .utils.resume_parser import (
    read_upload_file, extract_resume_information, validate_file_extension,
    validate_file_size, analyze_with_ollama
)

# ------------------ Helpers ------------------

def _normalize_skill_name(name: str) -> str:
    # Lowercase + collapse whitespace so “Forklift ” == “forklift”
    return " ".join((name or "").strip().split()).lower()


def _get_or_create_resume(user):
    """
    Get the most recent resume for a user, or create an empty one.
    """
    resume = Resume.objects.filter(user=user).order_by('-created_at').first()
    if not resume:
        resume = Resume.objects.create(user=user)
    return resume


def _get_skill_categories():
    """
    Provide consistent buckets for the skills step (front-end uses this).
    """
    return {
        "Trade / Hands-On": RELATABLE_SKILLS[:13],
        "Soft Skills": RELATABLE_SKILLS[13:24],
        "Job Readiness": RELATABLE_SKILLS[24:38],
        "Entrepreneurial": RELATABLE_SKILLS[38:]
    }

# ------------------ Entry / Welcome ------------------

@login_required
def resume_welcome(request):
    return render(request, 'resumes/welcome.html')


@login_required
def create_resume(request):
    # Single entry point for builder flow
    return redirect('resumes:resume_contact_info')

# ------------------ Imported Resume Views ------------------

@login_required
def resume_import(request, resume_id):
    """
    Show imported resume details. Also allows "Save to profile" (POST).
    """
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    if request.method == "POST":
        messages.success(request, "✅ Resume saved to your profile successfully!")
        # Send users back to the dashboard's user view
        return redirect("dashboard:user")

    return render(request, "resumes/imported_resume_view.html", {
        "resume": resume,
    })


@login_required
def resume_upload_page(request):
    return render(request, 'resumes/import_resume.html')


@login_required
def parse_resume_upload(request):
    """
    Parse an uploaded resume, AI-extract structured fields, and persist them.
    This is wrapped in a DB transaction so partial saves do not leave
    orphaned data if parsing fails.
    """
    if request.method != "POST" or not request.FILES.get("file"):
        return JsonResponse({"error": "No file uploaded"}, status=400)

    file = request.FILES["file"]

    try:
        # --- Validate and read ---
        ext = validate_file_extension(file)
        validate_file_size(file)
        content = read_upload_file(file, ext)

        # --- Ask the model for structured JSON ---
        ai_prompt = f"""
Extract the following fields from the resume:

- contact_info: {{
    full_name: string,
    email: string,
    phone: string,
    city: string,
    state: string
}}
- skills: [string]
- experience: [{{ job_title: string, company: string, dates: string }}]
- education: [{{ school_name: string, degree: string, graduation_year: string }}]

Return valid JSON ONLY in this exact structure (no prose, no comments):

{{
  "contact_info": {{
    "full_name": "",
    "email": "",
    "phone": "",
    "city": "",
    "state": ""
  }},
  "skills": [],
  "experience": [],
  "education": []
}}

Resume content:
{content}
        """.strip()

        ai_response = analyze_with_ollama(ai_prompt, model="mistral:latest")

        # --- Create the Resume first (so we always keep the file/raw_text) ---
        with transaction.atomic():
            resume = Resume.objects.create(
                user=request.user,
                file=file,
                raw_text=content,
                ai_summary=ai_response,
                is_imported=True
            )

            # Try to parse strictly as JSON; if it fails, we still return the resume_id
            parsed = None
            try:
                parsed = json.loads(ai_response or "{}")
            except json.JSONDecodeError:
                # Keep going; the user can still view raw_text and add details manually
                pass

            if parsed:
                # --- Contact Info ---
                contact_data = parsed.get("contact_info") or {}
                if any(contact_data.values()):
                    ContactInfo.objects.update_or_create(
                        resume=resume,
                        defaults={
                            "full_name": contact_data.get("full_name", "")[:255],
                            "email": contact_data.get("email", "")[:254],
                            "phone": contact_data.get("phone", "")[:20],
                            "city": contact_data.get("city", "")[:100],
                            "state": (contact_data.get("state") or "")[:2].upper(),
                        }
                    )

                # --- Skills (normalized) ---
                for raw_name in parsed.get("skills", []):
                    norm = _normalize_skill_name(raw_name)
                    if not norm:
                        continue
                    skill, _ = Skill.objects.get_or_create(name=norm)
                    resume.skills.add(skill)

                # --- Experience Entries (imported) ---
                for item in parsed.get("experience", []):
                    ExperienceEntry.objects.create(
                        resume=resume,
                        job_title=(item.get("job_title") or "")[:255],
                        company=(item.get("company") or "")[:255],
                        dates=item.get("dates", "")[:100],
                    )

                # --- Education Entries (imported) ---
                for edu in parsed.get("education", []):
                    EducationEntry.objects.create(
                        resume=resume,
                        school_name=(edu.get("school_name") or "")[:255],
                        degree=(edu.get("degree") or "")[:255],
                        graduation_year=(edu.get("graduation_year") or "")[:4],
                    )

        return JsonResponse({"resume_id": resume.id, "message": "Parsed successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

# ------------------ Builder Steps ------------------

@login_required
def contact_info_step(request):
    """
    Step 1: user-provided contact info (builder).
    """
    resume = _get_or_create_resume(request.user)
    contact_info, _ = ContactInfo.objects.get_or_create(resume=resume)

    if request.method == 'POST':
        contact_form = ContactInfoForm(request.POST, instance=contact_info)
        if contact_form.is_valid():
            obj = contact_form.save(commit=False)
            obj.resume = resume
            obj.save()
            return redirect('resumes:resume_education_step')
    else:
        contact_form = ContactInfoForm(instance=contact_info)

    return render(request, 'resumes/steps/contact_info_step.html', {'contact_form': contact_form})


@login_required
def education_step(request):
    """
    Step 2: builder education entries. We replace existing builder entries
    on each POST to keep the step idempotent.
    """
    resume = _get_or_create_resume(request.user)
    formset = EducationFormSet(queryset=Education.objects.filter(resume=resume))

    if request.method == 'POST':
        formset = EducationFormSet(request.POST)
        if formset.is_valid():
            Education.objects.filter(resume=resume).delete()
            for form in formset:
                if form.cleaned_data:
                    instance = form.save(commit=False)
                    instance.resume = resume
                    instance.save()
            return redirect('resumes:resume_experience_step')

    return render(request, 'resumes/steps/education_step.html', {'formset': formset})


@login_required
def experience_step(request):
    """
    Step 3: builder experience entries. Same idempotent pattern as education.
    """
    resume = _get_or_create_resume(request.user)
    formset = ExperienceFormSet(queryset=Experience.objects.filter(resume=resume))

    if request.method == 'POST':
        formset = ExperienceFormSet(request.POST)
        if formset.is_valid():
            Experience.objects.filter(resume=resume).delete()
            for form in formset:
                if form.cleaned_data:
                    instance = form.save(commit=False)
                    instance.resume = resume
                    instance.save()
            return redirect('resumes:resume_skills_step')

    return render(request, 'resumes/steps/experience_step.html', {'formset': formset})


@login_required
def skills_step(request):
    """
    Step 4: Skills. The template expects:
      - hidden textarea 'selected_skills' (CSV)
      - context vars: 'initial_skills' (list[str]), 'suggested_skills' (list[str])
    """
    resume = _get_or_create_resume(request.user)

    if request.method == 'POST':
        # Form posts CSV of skills via the hidden <textarea name="selected_skills">
        csv = request.POST.get('selected_skills', '')
        names = [s for s in (x.strip() for x in csv.split(',')) if s]

        # Replace existing skills with normalized set
        resume.skills.clear()
        for raw in names:
            norm = _normalize_skill_name(raw)
            if not norm:
                continue
            skill, _ = Skill.objects.get_or_create(name=norm)
            resume.skills.add(skill)

        # Continue to your preview/created page
        return redirect('resumes:created_resume_view', resume_id=resume.id)

    # For initial hydration, show what the resume already has
    initial_skills = [s.name for s in resume.skills.all()]

    # Pull 20–30 sensible suggestions (you can tune this slice)
    suggested_skills = RELATABLE_SKILLS[:30]

    return render(request, 'resumes/steps/skills_step.html', {
        'initial_skills': initial_skills,
        'suggested_skills': suggested_skills,
    })

# ------------------ Views (Preview, Created, Download) ------------------

@login_required
def created_resume_view(request, resume_id):
    """
    Final read of a created resume (builder flow), with prefetch to avoid N+1.
    Falls back to imported entries if builder sets are empty (rare).
    """
    resume = get_object_or_404(
        Resume.objects.select_related('user').prefetch_related(
            'skills', 'education', 'experiences', 'education_entries', 'experience_entries'
        ),
        id=resume_id, user=request.user
    )

    # Prefer builder data; fall back to imported entries if builder is empty.
    education_entries = list(resume.education.all()) or list(resume.education_entries.all())
    experience_entries = list(resume.experiences.all()) or list(resume.experience_entries.all())
    contact_info = getattr(resume, 'contact_info', None)

    # If you need profile data:
    profile = UserProfile.objects.filter(user=request.user).first()

    return render(request, 'resumes/created_resume_view.html', {
        'resume': resume,
        'profile': profile,
        'contact_info': contact_info,
        'education_entries': education_entries,
        'experience_entries': experience_entries,
    })


@login_required
def resume_preview(request, resume_id=None):
    """
    Unified preview used by builder 'Preview' and by the standalone preview route.
    Reads *either* builder sets or imported sets transparently.
    Also accepts POST (JSON) to update basic fields quickly.
    """
    # If no ID, preview most recent; else use given
    if resume_id:
        resume = get_object_or_404(
            Resume.objects.prefetch_related('skills', 'education', 'experiences', 'education_entries', 'experience_entries'),
            id=resume_id, user=request.user
        )
    else:
        resume = Resume.objects.filter(user=request.user).order_by('-created_at').first() or Resume.objects.create(user=request.user)

    if request.method == 'POST':
        try:
            data = json.loads(request.body or "{}")
            # Optional quick updates (name, skills)
            if 'full_name' in data:
                resume.full_name = (data.get('full_name') or '')[:100]

            if 'skills' in data and isinstance(data['skills'], list):
                resume.skills.clear()
                for raw in data['skills']:
                    norm = _normalize_skill_name(str(raw))
                    if norm:
                        skill, _ = Skill.objects.get_or_create(name=norm)
                        resume.skills.add(skill)

            resume.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    # Contact info fallback
    contact_info = getattr(resume, 'contact_info', None) or {
        'email': request.user.email or "you@example.com",
        'phone': "(000) 000-0000",
        'location': "City, State",
    }

    # Prefer builder sets; fallback to imported
    education_entries = list(resume.education.all()) or list(resume.education_entries.all())
    experience_entries = list(resume.experiences.all()) or list(resume.experience_entries.all())
    skills = resume.skills.all()

    # Optional: naive skill guessing if empty and raw_text exists
    if not skills and resume.raw_text:
        lines = resume.raw_text.lower().split('\n')
        guessed = [line.strip() for line in lines if 'skill' in line or ',' in line]
        for guess in guessed[:5]:
            norm = _normalize_skill_name(guess)
            if norm:
                skill, _ = Skill.objects.get_or_create(name=norm)
                resume.skills.add(skill)
        skills = resume.skills.all()

    return render(request, 'resumes/resume_preview.html', {
        'resume': resume,
        'contact_info': contact_info,
        'raw_text': resume.raw_text,
        'education_entries': education_entries,
        'experience_entries': experience_entries,
        'skills': skills,
    })


@login_required
@csrf_exempt  # If you add proper CSRF in your JS, you can remove this.
def save_created_resume(request, resume_id):
    """
    Marks a resume as 'created' (not imported). Kept simple.
    """
    if request.method != 'POST':
        return JsonResponse({"status": "invalid"}, status=405)

    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    try:
        resume.is_imported = False
        resume.save(update_fields=['is_imported'])
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "error": str(e)}, status=400)


@login_required
def download_resume(request, resume_id):
    """
    Render current resume to PDF using WeasyPrint.
    """
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    template_name = f"resumes/{resume.template}.html" if resume.template in ['simple', 'professional', 'modern'] else "resumes/simple.html"
    html_string = render_to_string(template_name, {'resume': resume})

    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(target=pdf_file)
    pdf_file.seek(0)

    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{resume.user.username}_resume.pdf"'
    return response


@login_required
def upload_profile_picture(request):
    """
    Store a user profile picture. Uses UserProfile instead of request.user.profile
    to avoid AttributeError if a OneToOne proxy isn't configured.
    """
    if request.method == 'POST':
        image_file = request.FILES.get('cropped_image')
        if image_file:
            profile = get_object_or_404(UserProfile, user=request.user)
            # NOTE: adjust field name if your model uses something other than 'profile_picture'
            profile.profile_picture.save(image_file.name, image_file)
            profile.save()
    return redirect('dashboard')
