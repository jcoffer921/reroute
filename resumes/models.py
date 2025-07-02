from django.db import models
from django.contrib.auth.models import User
from main.models import Job

# Resume model that holds top-level resume metadata
class Resume(models.Model):
    TEMPLATE_CHOICES = [
        ('professional', 'Professional'),
        ('modern', 'Modern'),
        ('simple', 'Simple'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_resumes')
    file = models.FileField(upload_to='resumes/', blank=True, null=True)
    template = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, default='professional')
    summary = models.TextField(blank=True)  # Optional professional summary
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume for {self.user.username}"

# Step 1: Contact Information
class ContactInfo(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='contact_info')

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=255, blank=True)

# Step 2: Education or Training entries (can have many per resume)
class Education(models.Model):
    # Link each education/training entry to a specific resume
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='education')

    # Updated field names to support broader learning backgrounds
    school = models.CharField("School / Program / Training Name", max_length=255)
    degree = models.CharField("Degree / Certification / Course", max_length=255, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField("Description (optional)", blank=True)

    def __str__(self):
        return f"{self.school} - {self.degree}" if self.degree else f"{self.school}"


# Step 3: Experience entries (can have many per resume)
class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experiences')
    job_title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.job_title} at {self.company}"




# Step 4: Skill entries (can have many per resume)
class Skill(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=255)


# Step 5: Optional project entries
class Project(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='projects')

    title = models.CharField(max_length=255)
    link = models.URLField(blank=True)
    description = models.TextField(blank=True)

# Job application model linking a user to a job they applied for
class Application(models.Model):
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='resume_job_applications')
    status = models.CharField(max_length=50, default='pending')  # e.g. pending, accepted, rejected

    def __str__(self):
        return f"{self.applicant.username} applied to {self.job.title}"
