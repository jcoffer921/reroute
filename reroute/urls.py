from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # App mounts
    path('', include('main.urls')),
    path('jobs/', include('job_list.urls')),
    path('resume/', include(('resumes.urls', 'resumes'), namespace='resumes')),
    path('accounts/', include('allauth.urls')),
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),
    path('resources/', include('resources.urls')),
    path('profile/', include('profiles.urls')),   # <-- keep this
    path('blog/', include('blog.urls')),

    # API
    path('api/', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
