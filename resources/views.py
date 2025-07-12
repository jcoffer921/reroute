# resources/views.py
from django.shortcuts import render

def resource_list(request):
    return render(request, 'resources/resource_list.html')


def interview_prep(request):
    return render(request, 'resources/job_tools/interview_prep.html')

def email_guidance(request):
    return render(request, 'resources/job_tools/email_guidance.html')

def legal_aid(request):
    return render(request, 'resources/reentry_help/legal_aid.html')