import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from profiles.models import UserProfile
from resumes.models import Resume
from django.contrib.auth.forms import PasswordChangeForm


# Built-in Django User creation form + email + email duplication check
class UserSignupForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'\d', password):
            raise ValidationError("Password must include at least one number.")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must include at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must include at least one lowercase letter.")
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            raise ValidationError("Password must include at least one special character.")

        return password
    
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'placeholder': 'Current Password'
        })
        self.fields['new_password1'].widget.attrs.update({
            'placeholder': 'New Password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'placeholder': 'Confirm Password'
        })

# Extended form for profile
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture']

# Step 1 – Basic Info
class Step1Form(forms.Form):
    full_name = forms.CharField(label="Full Name", max_length=100)
    email = forms.EmailField()

# Step 2 – Profile Details
class Step2Form(forms.Form):
    bio = forms.CharField(widget=forms.Textarea, required=False)
    profile_picture = forms.ImageField(required=False)

# Step 3 – Family Info
class Step3Form(forms.Form):
    emergency_contact = forms.CharField(label="Emergency Contact", max_length=100)
    relationship = forms.CharField(label="Relationship to Emergency Contact", max_length=100)

# Step 4 – Demographics
class Step4Form(forms.Form):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    race = forms.ChoiceField(choices=[
        ('Black', 'Black or African American'),
        ('White', 'White'),
        ('Asian', 'Asian'),
        ('Latino', 'Latino or Hispanic'),
        ('Native', 'Native American'),
        ('Other', 'Other'),
    ])


