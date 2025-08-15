from django.contrib import admin
from resumes.models import Resume, Application
from profiles.models import UserProfile


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
