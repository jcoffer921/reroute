from django.db import models
from django.contrib.auth.models import User
from main.models import Job

US_STATE_CHOICES = [
    ('AL', 'Alabama'),
    ('AK', 'Alaska'),
    ('AZ', 'Arizona'),
    ('AR', 'Arkansas'),
    ('CA', 'California'),
    ('CO', 'Colorado'),
    ('CT', 'Connecticut'),
    ('DE', 'Delaware'),
    ('FL', 'Florida'),
    ('GA', 'Georgia'),
    ('HI', 'Hawaii'),
    ('ID', 'Idaho'),
    ('IL', 'Illinois'),
    ('IN', 'Indiana'),
    ('IA', 'Iowa'),
    ('KS', 'Kansas'),
    ('KY', 'Kentucky'),
    ('LA', 'Louisiana'),
    ('ME', 'Maine'),
    ('MD', 'Maryland'),
    ('MA', 'Massachusetts'),
    ('MI', 'Michigan'),
    ('MN', 'Minnesota'),
    ('MS', 'Mississippi'),
    ('MO', 'Missouri'),
    ('MT', 'Montana'),
    ('NE', 'Nebraska'),
    ('NV', 'Nevada'),
    ('NH', 'New Hampshire'),
    ('NJ', 'New Jersey'),
    ('NM', 'New Mexico'),
    ('NY', 'New York'),
    ('NC', 'North Carolina'),
    ('ND', 'North Dakota'),
    ('OH', 'Ohio'),
    ('OK', 'Oklahoma'),
    ('OR', 'Oregon'),
    ('PA', 'Pennsylvania'),
    ('RI', 'Rhode Island'),
    ('SC', 'South Carolina'),
    ('SD', 'South Dakota'),
    ('TN', 'Tennessee'),
    ('TX', 'Texas'),
    ('UT', 'Utah'),
    ('VT', 'Vermont'),
    ('VA', 'Virginia'),
    ('WA', 'Washington'),
    ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'),
    ('WY', 'Wyoming'),
]

# models.py

class Resume(models.Model):
    TEMPLATE_CHOICES = [
        ('professional', 'Professional'),
        ('modern', 'Modern'),
        ('simple', 'Simple'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_resumes')
    file = models.FileField(upload_to='resumes/', blank=True, null=True)
    template = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, default='professional')
    full_name = models.CharField(max_length=100, blank=True)  # ✅ ADD THIS
    summary = models.TextField(blank=True)
    skill_summary = models.TextField(blank=True)  # ✅ ADD THIS
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
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=2, choices=US_STATE_CHOICES, blank=True)

    def __str__(self):
        return self.full_name

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
