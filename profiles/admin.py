from django.contrib import admin
from .models import UserProfile
from .models import EmployerProfile
from django.db.models import Q


class VerifiedStatusFilter(admin.SimpleListFilter):
    title = 'Verified status'
    parameter_name = 'verified'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Verified'),
            ('no', 'Unverified'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'yes':
            # Treat presence of both website and logo as "verified"
            return queryset.exclude(website='').exclude(website=None).exclude(logo='')
        if val == 'no':
            return queryset.filter(
                Q(website='') | Q(website=None) | Q(logo='')
            )
        return queryset


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'is_verified')
    search_fields = ('company_name', 'user__username', 'user__email')
    list_filter = (VerifiedStatusFilter,)

    fieldsets = (
        ('Company Info', {
            'fields': ('user', 'company_name', 'website', 'logo', 'description')
        }),
        ('Verification', {
            'fields': ('is_verified',),
        }),
    )

    readonly_fields = ('is_verified',)

    def is_verified(self, obj):
        """Derived verification flag for admin convenience.
        Considered verified if a website and logo are provided.
        """
        return bool((obj.website or '').strip()) and bool(obj.logo)

    is_verified.boolean = True
    is_verified.short_description = 'Verified'

