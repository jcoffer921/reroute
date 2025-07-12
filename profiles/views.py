import profile
from urllib import request
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
from django.views.decorators.http import require_POST
from main.models import Resume
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from profiles.models import UserProfile
from PIL import Image, UnidentifiedImageError
from .constants import US_STATES, ETHNICITY_CHOICES
from datetime import datetime



# Removed invalid top-level return statement. If you need this view, define it inside a function.

def public_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=user)
    resume = Resume.objects.filter(user=user).first()

    return render(request, 'profiles/public_profile.html', {
        'user': user,
        'profile': profile,
        'resume': resume,
        'US_STATES': US_STATES,
        'ETHNICITY_CHOICES': ETHNICITY_CHOICES,
    })

# Create your views here.
# profiles/views.py
@login_required
@csrf_protect
def multi_step_form_view(request, step=1):
    return redirect('public_profile', username=request.user.username)  # Redirect to the update profile view



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

@require_POST
@login_required
def update_bio(request):
    profile = UserProfile.objects.get(user=request.user)
    profile.bio = request.POST.get('bio', '')
    profile.save()
    return redirect('public_profile', username=request.user.username)

@require_POST
@login_required
def update_personal_info(request):
    profile = UserProfile.objects.get(user=request.user)

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
def update_employment_info(request):
    profile = request.user.profile
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
    profile = UserProfile.objects.get(user=request.user)
    profile.emergency_contact_firstname = request.POST.get("emergency_contact_firstname", "")
    profile.emergency_contact_lastname = request.POST.get("emergency_contact_lastname", "")
    profile.emergency_contact_relationship = request.POST.get("emergency_contact_relationship", "")
    profile.emergency_contact_phone = request.POST.get("emergency_contact_phone", "")
    profile.emergency_contact_email = request.POST.get("emergency_contact_email", "")
    profile.save()
    return redirect('public_profile', username=request.user.username)


@require_POST
@login_required
def update_demographics(request):
    profile = UserProfile.objects.get(user=request.user)

    profile.gender = request.POST.get("gender", "")
    profile.ethnicity = request.POST.get("ethnicity", "")


    # Option 2: (SAFER DEFAULT) Store as comma-separated string
    # profile.race = ", ".join(race_list)

    profile.disability_explanation = request.POST.get("disability_explanation", "")
    profile.veteran_explanation = request.POST.get("veteran_explanation", "")

    profile.save()
    return redirect('public_profile', username=request.user.username)


@login_required
def update_profile_picture(request):
    if request.method == 'POST' and 'profile_picture' in request.FILES:
        image_file = request.FILES['profile_picture']

        # Validate image using Pillow
        try:
            img = Image.open(image_file)
            img.verify()  # Check if it's a valid image
            if img.format.lower() not in ['jpeg', 'png', 'gif']:
                messages.error(request, "Unsupported image format. Use JPEG, PNG, or GIF.")
                return redirect('profile', username=request.user.username)
        except UnidentifiedImageError:
            messages.error(request, "Invalid image file. Please upload a real image.")
            return redirect('profile', username=request.user.username)

        # Save image to profile
        profile = request.user.profile
        profile.profile_picture = image_file
        profile.save()

        messages.success(request, "Profile picture updated successfully.")

    return redirect('profile', username=request.user.username)

@require_POST
@login_required
def delete_profile_picture(request):
    profile = request.user.profile
    if profile.profile_picture:
        profile.profile_picture.delete()
        profile.save()
    return redirect('dashboard')  # or wherever you want to send them

@login_required
def edit_personal_info(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'profiles/edit_personal_info.html', {
        'profile': profile,
        'US_STATES': US_STATES,

    })

@login_required
def edit_emergency_contact(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'profiles/edit_emergency.html', {
        'profile': profile,
    })

@login_required
def edit_employment(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'profiles/edit_employment.html', {
        'profile': profile,
    })

from .constants import US_STATES, ETHNICITY_CHOICES

@login_required
def edit_demographics(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'profiles/edit_demographics.html', {
        'profile': profile,
        'ETHNICITY_CHOICES': ETHNICITY_CHOICES,
    })

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@login_required
def remove_profile_picture(request):
    profile = request.user.userprofile
    profile.profile_picture.delete(save=True)
    return redirect('public_profile', username=request.user.username)
