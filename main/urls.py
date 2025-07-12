from django.urls import path, include 
from django.urls import path
from . import views
from .views import signup_view
from django.contrib.auth import views as auth_views
from .views import signup_view, home  # Add your custom views as needed
from dashboard.views import dashboard_redirect  # NEW
from . import views
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
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('contact/', views.contact_view, name='contact'),
    path('settings/', views.settings_view, name='settings'),
    path('resources/', views.resources_view, name='resources'),




    # Job-related pages
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/match/<int:seeker_id>/', views.match_jobs, name='match_jobs'),

    # Multi-step profile onboarding
    path('profile/step1/', views.step1, name='step1'),
    path('profile/step2/', views.step2, name='step2'),
    path('profile/step3/', views.step3, name='step3'),
    path('profile/step4/', views.step4, name='step4'),
    path('profile/summary/', views.final_view, name='final_view'),

    # Resume or dashboard related
    path('dashboard/', dashboard_redirect, name='dashboard_home'),  # ✅ NEW
    path('dashboard/', include('dashboard.urls')),  # Include dashboard app URLs
    path('profile/', include('profiles.urls')),  # include profiles app URLs


    # Auth: Password Reset Flow (using custom templates)
    path('accounts/password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Terms and Policy
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
]
