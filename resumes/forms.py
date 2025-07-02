from django import forms
from .models import Resume, ContactInfo, Education, Experience, Skill, Project

# Old form removed: ResumeForm using flat fields
# New: Step-based forms for each resume section

# Step 1: Contact Info Form
class ContactInfoForm(forms.ModelForm):
    class Meta:
        model = ContactInfo
        fields = ['full_name', 'email', 'phone', 'location']

class SummaryForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['summary']
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write a brief professional summary...'}),
        }

# Step 2: Education Form (Inclusive of Training & Certifications)
class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['school', 'degree', 'start_date', 'end_date', 'description']
        widgets = {
            'school': forms.TextInput(attrs={'class': 'form-control'}),
            'degree': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['degree'].required = False
        self.fields['end_date'].required = False
        self.fields['description'].required = False



# Step 3: Experience Form
class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['job_title', 'company', 'start_date', 'end_date', 'description']
        widgets = {
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'e.g.\nPromoted for leadership\nManaged floor staff\nHandled ticket sales...',
            }),
        }

# Step 4: Skill Form
class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name']

# Step 5: Project Form (optional)
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'link', 'description']
