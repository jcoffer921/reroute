import uuid
from datetime import datetime
from django.db import models, transaction
from django.contrib.auth.models import User
from django.db.models import JSONField
from profiles.constants import USER_STATUS_CHOICES, YES_NO


class UserProfile(models.Model):
    # -------------------------------------
    # Core User Link
    # -------------------------------------
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # -------------------------------------
    # Step 1: Basic Profile Details
    # -------------------------------------
    firstname = models.CharField(max_length=50, blank=True)
    lastname = models.CharField(max_length=50, blank=True)
    preferred_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    personal_email = models.EmailField(blank=True)
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)

    # -------------------------------------
    # Step 2: Additional Info
    # -------------------------------------
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    pronouns = models.CharField(max_length=50, blank=True)
    native_language = models.CharField(max_length=100, blank=True)
    year_of_incarceration = models.IntegerField(blank=True, null=True)
    year_released = models.IntegerField(blank=True, null=True)
    relation_to_reroute = models.CharField(max_length=100, blank=True)

    # -------------------------------------
    # Step 3: Emergency Contact
    # -------------------------------------
    emergency_contact_firstname = models.CharField(max_length=100, blank=True)
    emergency_contact_lastname = models.CharField(max_length=100, blank=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_email = models.EmailField(blank=True)

    # -------------------------------------
    # Step 4: Demographics
    # -------------------------------------
    gender = models.CharField(max_length=50, blank=True)
    ethnicity = models.CharField(max_length=50, blank=True)
    # Temporarily preserve the old data
    race = JSONField(default=list, blank=True, null=True)


    disability = models.CharField(
        max_length=3,
        choices=YES_NO,
        blank=True,
        null=True
    )
    veteran_status = models.CharField(
        max_length=3,
        choices=YES_NO,
        blank=True,
        null=True
    )
    disability_explanation = models.TextField(blank=True, null=True)
    veteran_explanation = models.TextField(blank=True, null=True)

    # -------------------------------------
    # ReRoute User Journey Status
    # -------------------------------------
    status = models.CharField(
        max_length=30,
        choices=USER_STATUS_CHOICES,
        blank=True,
        help_text="User-defined status reflecting their current journey."
    )

    # -------------------------------------
    # Platform Admin Account Control
    # -------------------------------------
    account_status = models.CharField(
        max_length=20,
        default='active',
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('suspended', 'Suspended')
        ],
        help_text="Platform-controlled account state."
    )

    # Verified status for public profile
    verified = models.BooleanField(
        default=True,
        help_text="Show a verified badge on this user's public profile."
    )

    work_in_us = models.CharField(max_length=10, choices=YES_NO, blank=True)
    sponsorship_needed = models.CharField(max_length=10, choices=YES_NO, blank=True)
    lgbtq = models.CharField(max_length=10, choices=YES_NO, blank=True)

    # -------------------------------------
    # Auto-generated ReRoute User ID
    # Format: RR-YYYY-XXXXXX
    # -------------------------------------
    user_uid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        db_index=True,
        editable=False
    )


    def save(self, *args, **kwargs):
        """
        Automatically generate a unique ReRoute user ID on first save.
        """
        if not self.user_uid:
            self.user_uid = self.generate_uid()
        super().save(*args, **kwargs)

    def generate_uid(self):
        """
        Generates a structured, unique user ID like:
        Example: RR-2025-000123
        Falls back to temporary ID if user is not yet saved.
        """
        if self.user and self.user.id and self.user.date_joined:
            return f"RR-{self.user.date_joined.year}-{self.user.id:06d}"
        else:
            year = datetime.now().year
            with transaction.atomic():
                count = (
                    UserProfile.objects
                    .filter(user_uid__startswith=f"RR-{year}")
                    .count() + 1
                )
                return f"RR-{year}-TEMP{count:06d}"

    def __str__(self):
        """
        String representation in admin panel and debugging.
        """
        return self.user.get_full_name() or self.user.username

    class Meta:
        ordering = ['user_uid']
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
