from io import BytesIO
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from weasyprint import HTML

from .models import Resume, ContactInfo, Education, Experience, Skill, Project
from .forms import ContactInfoForm, EducationForm, ExperienceForm, SkillForm

# === Summary form (bound to Resume model) ===
from django import forms
class SummaryForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['summary']
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Write a short professional summary...'})
        }

# === Resume Creation Entry Point ===
@login_required
def create_resume(request):
    return redirect('resumes:resume_contact_info')

# === Step 1: Contact Info ===
@login_required
def contact_info_step(request):
    resume, _ = Resume.objects.get_or_create(user=request.user)
    contact_info, _ = ContactInfo.objects.get_or_create(resume=resume)

    if request.method == 'POST':
        contact_form = ContactInfoForm(request.POST, instance=contact_info)
        if contact_form.is_valid():
            contact_form.save()
            return redirect('resumes:resume_education_step')
    else:
        contact_form = ContactInfoForm(instance=contact_info)

    return render(request, 'resumes/steps/contact_info_step.html', {
        'contact_form': contact_form,
    })

# === Step 2: Education ===
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import Resume, Education
from .forms import EducationForm


from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from .models import Resume, Education
from .forms import EducationForm
from django.contrib.auth.decorators import login_required

@login_required
def education_step(request):
    resume = get_object_or_404(Resume, user=request.user)
    EducationFormSet = modelformset_factory(Education, form=EducationForm, extra=0, can_delete=True)

    if request.method == 'POST':
        formset = EducationFormSet(request.POST, queryset=Education.objects.filter(resume=resume))

        if formset.is_valid():
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    instance = form.save(commit=False)
                    instance.resume = resume
                    instance.save()

            # ✅ Correct deletion handling
            if formset.can_delete:
                for form in formset.forms:
                    if form.cleaned_data.get('DELETE', False) and form.instance.pk:
                        form.instance.delete()

            return redirect('resumes:resume_experience_step')
        else:
            print("⛔ Formset is invalid")
            print(formset.errors)
    else:
        formset = EducationFormSet(queryset=Education.objects.filter(resume=resume))

    return render(request, 'resumes/steps/education_step.html', {'formset': formset})




# === Step 3: Experience ===
@login_required
def experience_step(request):
    resume = get_object_or_404(Resume, user=request.user)
    ExperienceFormSet = modelformset_factory(Experience, form=ExperienceForm, extra=0, can_delete=True)

    if request.method == 'POST':
        formset = ExperienceFormSet(request.POST, queryset=Experience.objects.filter(resume=resume))
        if formset.is_valid():
            instances = formset.save(commit=False)

            for instance in instances:
                instance.resume = resume
                instance.save()

            for obj in formset.deleted_objects:
                obj.delete()

            return redirect('resumes:resume_skills_step')
        else:
            print("Formset is invalid:", formset.errors)
    else:
        formset = ExperienceFormSet(queryset=Experience.objects.filter(resume=resume))

    return render(request, 'resumes/steps/experience_step.html', {'formset': formset})

# === Step 4: Skills ===
@login_required
def skills_step(request):
    resume = get_object_or_404(Resume, user=request.user)

    if request.method == 'POST':
        skills_input = request.POST.get('skills_input', '')
        skill_lines = [line.strip() for line in skills_input.split('\n') if line.strip()]

        # Clear old skills (if needed)
        Skill.objects.filter(resume=resume).delete()

        # Save each new skill
        for skill_name in skill_lines:
            Skill.objects.create(resume=resume, name=skill_name)

        return redirect('resumes:resume_summary_step')  # or whatever is next
    else:
        # Preload saved skills
        existing_skills = Skill.objects.filter(resume=resume)
        initial_value = "\n".join(skill.name for skill in existing_skills)

    return render(request, 'resumes/steps/skills_step.html', {
        'initial_skills': initial_value
    })


# === Step 5: Summary ===
@login_required
def summary_step(request):
    resume = get_object_or_404(Resume, user=request.user)

    if request.method == 'POST':
        form = SummaryForm(request.POST, instance=resume)
        if form.is_valid():
            form.save()
            return redirect('resumes:resume_preview', resume_id=resume.id)
    else:
        form = SummaryForm(instance=resume)

    return render(request, 'resumes/steps/summary_step.html', {'form': form})

@login_required
def resume_preview(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    contact_info = ContactInfo.objects.filter(resume=resume).first()

    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Update resume core fields
            resume.full_name = data.get('full_name', resume.full_name)
            resume.summary = data.get('summary', resume.summary)
            resume.skill_summary = '\n'.join(data.get('skills', []))

            # Update or create contact info
            # ✅ New (safe + accurate for city/state split)
            if contact_info:
                contact_parts = data.get('contact_info', '').split('|')

                if len(contact_parts) >= 1:
                    contact_info.email = contact_parts[0].strip()

                if len(contact_parts) >= 2:
                    contact_info.phone = contact_parts[1].strip()

                if len(contact_parts) >= 3:
                    location = contact_parts[2].strip()
                    if ',' in location:
                        city, state = map(str.strip, location.split(','))
                        contact_info.city = city
                        contact_info.state = state.upper()[:2]
                    else:
                        contact_info.city = location
                        contact_info.state = ''

                contact_info.save()


            resume.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    # Pre-fill the resume fields from session if not already set
    resume.full_name = resume.full_name or request.session.get('full_name', 'Your Name')
    resume.summary = resume.summary or request.session.get('summary', '')
    resume.skill_summary = resume.skill_summary or request.session.get('skills', '')
    resume.save()

    # Optional: Pre-fill contact info from session if blank
    # Optional: Pre-fill contact info from session if blank
    if contact_info:
        contact_info.email = contact_info.email or request.session.get('email', '')
        contact_info.phone = contact_info.phone or request.session.get('phone', '')

        # Handle city/state if session stored them as a single string (e.g., "Philadelphia, PA")
        location_string = request.session.get('location', '')
        if ',' in location_string:
            city, state = map(str.strip, location_string.split(','))
            contact_info.city = contact_info.city or city
            contact_info.state = contact_info.state or state.upper()[:2]
        elif location_string:
            contact_info.city = contact_info.city or location_string
            contact_info.state = contact_info.state or ''

        contact_info.save()

    return render(request, 'resumes/resume_preview.html', {
        'resume': resume,
        'contact_info': contact_info,
    })


# === Download PDF ===
@login_required
def download_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    template_name = f"resumes/{resume.template}.html" if resume.template in ['simple', 'professional', 'modern'] else "resumes/simple.html"
    html_string = render_to_string(template_name, {'resume': resume})

    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(target=pdf_file)
    pdf_file.seek(0)

    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{resume.user.username}_resume.pdf"'
    return response

# === Upload Profile Picture ===
@login_required
def upload_profile_picture(request):
    if request.method == 'POST':
        image_file = request.FILES.get('cropped_image')
        if image_file:
            profile = request.user.profile
            profile.profile_picture.save(image_file.name, image_file)
            profile.save()
    return redirect('dashboard')
