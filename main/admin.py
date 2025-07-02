from django.contrib import admin
from .models import JobSeeker, Resume, Job, Application
from profiles.models import UserProfile


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "employer", "location", "tags")
    search_fields = ("title", "employer", "location", "tags")
    list_filter = ("location", "employer")

@admin.register(JobSeeker)
class JobSeekerAdmin(admin.ModelAdmin):
    list_display = ("name", "email")
    search_fields = ("name", "email", "skills", "interests")

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "applicant", "status")
    list_filter = ("status",)
    search_fields = ("job__title", "applicant__username")

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("user", "file")
    search_fields = ("user__username",)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "user_uid", "phone_number", "birthdate", "status", "account_status")
    list_filter = ("account_status", "status")
    search_fields = ("user__username", "user_uid", "phone_number", "bio")
    readonly_fields = ("user_uid",)


    def has_delete_permission(self, request, obj=None):
        if obj and obj.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)


