from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard.views import dashboard_redirect
from profiles.views import public_profile_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('jobs/', include('job_list.urls')),
    path('<str:username>/', public_profile_view, name='public_profile'),
    path('resume/', include(('resumes.urls', 'resumes'), namespace='resumes')),
    path('accounts/', include('allauth.urls')),
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),
    path("resources/", include("resources.urls")),
    path('profile/', include('profiles.urls')),
    path("blog/", include("blog.urls")),

    # ✅ Only one skills-related route needed (API)
    path('api/', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)