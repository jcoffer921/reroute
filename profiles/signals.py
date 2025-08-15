# ---------------------------------
# Signals: ensure profile existence
# ---------------------------------
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from profiles.models import UserProfile
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@login_required
def remove_profile_picture(request):
    """Legacy alias that removes picture then redirects to public profile."""
    profile = request.user.profile
    if profile.profile_picture:
        profile.profile_picture.delete(save=True)
    return redirect('public_profile', username=request.user.username)