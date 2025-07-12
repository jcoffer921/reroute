# resources/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.resource_list, name='resource_list'),

    # Job tools resources
    path('job-tools/interview-prep/', views.interview_prep, name='interview_prep'),
    path('job-tools/email-guidance/', views.email_guidance, name='email_guidance'),

    # Reentry help resources
    path('reentry-help/legal-aid/', views.legal_aid, name='legal_aid'),

]
