from django.urls import path
from . import views

urlpatterns = [
    path('user/', views.user_dashboard, name='user_dashboard'),
    path('employer/', views.employer_dashboard, name='employer_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),

    # User
    path('saved-jobs/', views.saved_jobs_view, name='saved_jobs'),
    path('matches/', views.matched_jobs_view, name='matched_jobs'),

    # Employer
    path('employer/analytics/', views.employer_analytics, name='employer_analytics'),


]
