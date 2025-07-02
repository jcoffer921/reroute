from django.db import models
from django.contrib.auth.models import User

from profiles.constants import ETHNICITY_CHOICES, GENDER_CHOICES, YES_NO

# Original job seeker model
class JobSeeker(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    skills = models.TextField()
    interests = models.TextField()
    resume = models.FileField(upload_to='resumes/', blank=True)

    def __str__(self):
        return self.name

# Original job model
class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=100)
    employer = models.CharField(max_length=100)
    tags = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.title} at {self.employer}"

# New: Resume tied to User
class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='main_resumes')
    file = models.FileField(upload_to='resumes/', blank=True, null=True)

    # New fields for building resumes directly
    education = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resume for {self.user.username}"


# New: Job application model
class Application(models.Model):
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='main_applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='main_job_applications')
    status = models.CharField(max_length=50, default='pending')

    def __str__(self):
        return f"{self.applicant.username} applied to {self.job.title}"
