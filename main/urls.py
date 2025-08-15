from django.urls import path, include 
from django.urls import path
from . import views
from .views import signup_view
from django.contrib.auth import views as auth_views
from .views import signup_view, home  # Add your custom views as needed
from dashboard.views import dashboard_redirect  # NEW
from . import views
from job_list.user import views as user_views
from job_list.employers import views as employer_views
from django.shortcuts import redirect
from .forms import Step1Form, Step2Form, Step3Form, Step4Form
from .views import (
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView
)

urlpatterns = [
    # Core Pages
    path('', views.home, name='home'),
    path('about-us/', views.about_us, name='about_us'),
    path('login/', views.login_view, name='login'),
    path('employer/signup/', views.employer_signup_view, name='employer_signup'),
    path('employer/login/', views.employer_login_view, name='employer_login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('contact/', views.contact_view, name='contact'),
    path('settings/', views.settings_view, name='settings'),
    path('resources/', views.resources_view, name='resources'),
    #path('blog/articles/', lambda request: redirect('blog_list', permanent=True)),
    path('blog/', include('blog.urls')),  # This connects /blog/* to blog.urls
    path('employer/dashboard/', views.employer_dashboard_view, name='employer_dashboard'),

    path('resumes/', include('resumes.urls')),
    path('profile/step1/', lambda request: redirect('resumes:resume_contact_info')),


    # Job-related pages
    # User-side job board
    path('', user_views.opportunities_view, name='opportunities'),  # /jobs/
    path('<int:job_id>/', user_views.job_detail_view, name='job_detail'),  # /jobs/5/
    path('<int:job_id>/apply/', user_views.apply_to_job, name='apply_to_job'),

    # Match/suggested jobs (keep if used)
    path('match/<int:seeker_id>/', user_views.match_jobs, name='match_jobs'),

    # Employer-side job controls
    path('employer/dashboard/', employer_views.dashboard_view, name='employer_dashboard'),
    path('employer/job/create/', employer_views.create_job, name='create_job'),

    # Resume or dashboard related
    path('dashboard/', include('dashboard.urls')),  # Include dashboard app URLs
    path('profile/', include('profiles.urls')),  # include profiles app URLs
    path('api/skills/', views.get_skills_json, name='get_skills_json'),


    # Auth: Password Reset Flow (using custom templates)
    path('accounts/password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Terms and Policy
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
]
