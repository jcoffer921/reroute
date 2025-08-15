from django.shortcuts import redirect
from django.urls import path
from . import views
from .views import user_profile_view, public_profile_view, remove_profile_picture, update_personal_info
from .views import update_profile_picture



urlpatterns = [
    # Public profile views
    path('view/<str:username>/', public_profile_view, name='public_profile'),
    path('profile/<str:username>/', public_profile_view, name='profile'),

    # 🔥 Logged-in user's personal profile
    path('', user_profile_view, name='my_profile'),  # <-- ✅ This is what you asked for

    path('profile/step1/', lambda request: redirect('resumes:resume_contact_info')),

    # Profile update routes
    path('update/', views.update_profile, name='update_profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('update-picture/', update_profile_picture, name='update_profile_picture'),
    path('update/personal-info/', update_personal_info, name='update_personal_info'),
    path('update/employment/', views.update_employment_info, name='update_employment_info'),
    path('profile/update/emergency/', views.update_emergency_contact, name='update_emergency_contact'),
    path('profile/update/demographics/', views.update_demographics, name='update_demographics'),
    path('profile/update/skills/', views.update_skills, name='update_skills'),
    path('profile/edit/skills/', views.edit_skills, name='edit_skills'),
    path('profile/remove-picture/', remove_profile_picture, name='remove_profile_picture'),
    path('profile/update/bio/', views.update_bio, name='update_bio'),
    # path('delete-picture/', views.delete_profile_picture, name='delete_profile_picture'),
]
