from django.contrib import admin
from .models import UserProfile
from .models import EmployerProfile

# Register your models here.
@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name')

