from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from profiles.models import UserProfile  # and Resume if applicable
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from profiles.models import UserProfile
from datetime import datetime
from django.core.files.base import ContentFile


# Example STEP_FORM_MAP definition; replace with your actual form classes
from .forms import Step1Form, Step2Form, Step3Form, Step4Form

STEP_FORM_MAP = {
    1: Step1Form,
    2: Step2Form,
    3: Step3Form,
    4: Step4Form,
}

# Create your views here.
# profiles/views.py
@login_required
@csrf_protect
def multi_step_form_view(request, step=1):
    steps = {
        1: Step1Form,
        2: Step2Form,
        3: Step3Form,
        4: Step4Form,
    }

    titles = {
        1: "Step 1: Bio",
        2: "Step 2: Profile Picture",
        3: "Step 3: Family Info",
        4: "Step 4: Demographics",
    }

    FormClass = steps.get(step)
    step_title = titles.get(step, "Profile Setup")

    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    form = FormClass(instance=user_profile)

    if request.method == 'POST':
      form = FormClass(request.POST, request.FILES, instance=user_profile)
      if form.is_valid():
          print(f"✅ Step {step} form is valid, saving...")
          form.save()
          if step < len(steps):
              print(f"➡️ Redirecting to step {step + 1}")
              return redirect('profile_step', step=step + 1)
          print("🎯 Final step complete — redirecting to dashboard")
          return redirect('dashboard')
      else:
          print(f"❌ Step {step} form has errors:")
          print(form.errors)


    progress = int((step / len(steps)) * 100)
    back_url = f"/profile/step/{step - 1}/" if step > 1 else None

    return render(request, 'profiles/multi_step_form.html', {
        'form': form,
        'step_title': step_title,
        'step': step,
        'progress': progress,
        'back_url': back_url,
    })



def redirect_to_first_step(request):
    return redirect('profile_step', step=1)

@login_required
def dashboard_view(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    resume = getattr(user_profile, 'resume', None)  # Optional resume logic

    # Step 1: Profile completion calculation
    total_fields = [
        user_profile.firstname,
        user_profile.lastname,
        user_profile.preferred_name,
        user_profile.phone_number,
        user_profile.bio,
        user_profile.gender,
        user_profile.ethnicity,
        user_profile.race,
        user_profile.veteran_status,
        user_profile.veteran_explanation,
        user_profile.disability,
        user_profile.disability_explanation,
        user_profile.profile_picture,
    ]
    filled_fields = [field for field in total_fields if field not in [None, '', []]]
    completion_percentage = int((len(filled_fields) / len(total_fields)) * 100)

    formatted_joined_date = request.user.date_joined.strftime("%b %d, %Y") if request.user.date_joined else None

    return render(request, 'profiles/dashboard.html', {
        'profile': user_profile,
        'resume': resume,
        'completion_percentage': completion_percentage,
        'joined_date': formatted_joined_date,
    })

@csrf_exempt
@login_required
def update_profile(request):
    if request.method == "POST":
        profile = UserProfile.objects.get(user=request.user)

        # Fix for optional date field
        raw_birthdate = request.POST.get("birthdate", "").strip()
        if raw_birthdate:
            try:
                profile.birthdate = datetime.strptime(raw_birthdate, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({"success": False, "error": "Invalid birthdate format"}, status=400)
        else:
            profile.birthdate = None  # This line avoids the crash

        # Update the fields safely
        profile.firstname = request.POST.get("firstname", profile.firstname)
        profile.lastname = request.POST.get("lastname", profile.lastname)
        profile.phone_number = request.POST.get("phone_number", profile.phone_number)
        profile.personal_email = request.POST.get("personal_email", profile.personal_email)
        profile.bio = request.POST.get("bio", profile.bio)
        profile.status = request.POST.get("status", profile.status)
        profile.birthdate = request.POST.get("birthdate", profile.birthdate)
        profile.gender = request.POST.get("gender", profile.gender)

        profile.save()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=400)

@login_required
def upload_profile_picture(request):
    if request.method == 'POST':
        image_file = request.FILES.get('cropped_image') or request.FILES.get('profile_picture')
        if image_file:
            profile = request.user.profile
            profile.profile_picture.save(image_file.name, image_file)
            profile.save()
    return redirect('dashboard')  # or change this to your actual dashboard view name

@login_required
def delete_profile_picture(request):
    profile = request.user.profile
    if request.method == 'POST':
        profile.profile_picture.delete(save=True)
    return redirect('dashboard')
