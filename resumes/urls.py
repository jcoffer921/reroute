from django.urls import path
from . import views

urlpatterns = [
    # Resume builder step routes
    path('build/contact/', views.contact_info_step, name='resume_contact_info'),
    path('build/education/', views.education_step, name='resume_education_step'),
    path('build/experience/', views.experience_step, name='resume_experience_step'),
    path('build/skills/', views.skills_step, name='resume_skills_step'),
    path('build/summary/', views.summary_step, name='resume_summary_step'),
    path('build/preview/', views.resume_preview, name='resume_preview_step'),

    # Resume output routes
    path('<int:resume_id>/preview/', views.resume_preview, name='resume_preview'),
    path('<int:resume_id>/download/', views.download_resume, name='download_resume'),

    # Profile picture (used on dashboard)
    path('upload-profile-picture/', views.upload_profile_picture, name='upload_profile_picture'),

    # Placeholder for future resume creation flow
    path('create/contact/', views.contact_info_step, name='resume_contact_info_create'),
]
