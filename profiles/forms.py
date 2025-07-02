from django import forms

from resumes import models
from .models import UserProfile
from profiles.constants import USER_STATUS_CHOICES, YES_NO, US_STATES, PRONOUN_CHOICES, LANGUAGE_CHOICES, GENDER_CHOICES, ETHNICITY_CHOICES, RACE_CHOICES

class Step1Form(forms.ModelForm):
    state = forms.ChoiceField(choices = US_STATES)
    class Meta:
        model = UserProfile
        fields = [
            'firstname',
            'lastname',
            'preferred_name',
            'phone_number',
            'personal_email',
            'street_address',
            'city',
            'state',
            'zip_code',
            'bio',
        ] 

    def clean(self):
        cleaned_data = super().clean()

        required_fields = [
            'firstname', 'lastname', 'phone_number',
            'personal_email', 'street_address', 'city', 'state', 'zip_code'
        ]
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, 'This field is required.')


class Step2Form(forms.ModelForm):
    pronouns = forms.ChoiceField(choices=PRONOUN_CHOICES)
    pronouns_other = forms.CharField(required=False)

    native_language = forms.ChoiceField(choices=LANGUAGE_CHOICES)
    native_language_other = forms.CharField(required=False)

    birthdate = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        required=False,
        label="Birthdate"
    )


    class Meta:
        model = UserProfile
        fields = [
            'profile_picture',
            'birthdate',
            'pronouns',
            'native_language',
            'year_of_incarceration',
            'year_released',
            'relation_to_reroute',
        ]

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('pronouns') == 'other' and not cleaned_data.get('pronouns_other'):
            self.add_error('pronouns_other', 'Please specify your pronouns.')

        if cleaned_data.get('native_language') == 'other' and not cleaned_data.get('native_language_other'):
            self.add_error('native_language_other', 'Please specify your native language.')

        required_fields = ['birthdate', 'pronouns', 'native_language']
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, 'This field is required.')


    

class Step3Form(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'emergency_contact_firstname',
            'emergency_contact_lastname',
            'emergency_contact_relationship',
            'emergency_contact_phone',
            'emergency_contact_email',
        ]

    def clean(self):
        cleaned_data = super().clean()
        required_fields = self.Meta.fields

        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, 'This field is required.')

class Step4Form(forms.ModelForm):
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Gender"
    )
    ethnicity = forms.ChoiceField(
        choices=ETHNICITY_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Ethnicity"
    )
    race = forms.MultipleChoiceField(
        choices=RACE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Race (check all that apply):"
    )
    disability = forms.ChoiceField(
        choices=YES_NO,
        widget=forms.RadioSelect,
        label="Do you have a disability?",
        required=True
    )
    disability_explanation = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label="If yes, please briefly describe your disability"
    )
    veteran_status = forms.ChoiceField(
        choices=YES_NO,
        widget=forms.RadioSelect,
        label="Are you a veteran?",
        required=True
    )
    veteran_explanation = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label="If yes, please describe your service or background"
    )

    status = forms.ChoiceField(
        choices= USER_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Current Status"
    )



    class Meta:
        model = UserProfile
        fields = [
            'gender',
            'ethnicity',
            'race',
            'disability',
            'disability_explanation',
            'veteran_status',
            'veteran_explanation',
            'status',
        ]

    def clean_gender(self):
        value = self.cleaned_data.get('gender', '').strip()
        if value == '':
            raise forms.ValidationError("Please select your gender.")
        return value

    def clean_ethnicity(self):
        value = self.cleaned_data.get('ethnicity', '').strip()
        if value == '':
            raise forms.ValidationError("Please select your ethnicity.")
        return value
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.race = self.cleaned_data.get('race')  
        if commit:
            profile.save()
        return profile

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('disability') == 'yes' and not cleaned_data.get('disability_explanation'):
            self.add_error('disability_explanation', 'Please provide a brief explanation.')

        if cleaned_data.get('veteran_status') == 'yes' and not cleaned_data.get('veteran_explanation'):
            self.add_error('veteran_explanation', 'Please describe your service.')

