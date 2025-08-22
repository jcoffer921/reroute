from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from profiles.views import user_profile_view   


# project urls.py (add these imports)
from main import views as main_views                   # for dashboard view
from profiles.views import user_profile_view           # for owner profile
from profiles.views import user_profile_view, update_profile_picture, remove_profile_picture


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),

    path('profile/', user_profile_view, name='my_profile'),  # exact-path alias
    path('profile/update-picture/', update_profile_picture, name='update_profile_picture'),
    path('profile/remove-picture/', remove_profile_picture, name='remove_profile_picture'),

    # --- EXACT-PATH ALIASES (these create the names your templates use) ---
    path('profile/',   user_profile_view,         name='my_profile'),  # /profile/ resolves by name
    path('dashboard/', main_views.dashboard_view, name='dashboard'),   # /dashboard/ resolves by name

    # --- APP INCLUDES (handle deeper paths under same prefixes) ---
    path('profile/',   include('profiles.urls')),                           # /profile/update/..., /profile/view/<username>/
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),

    # (the rest you already have)
    path('jobs/',      include('job_list.urls')),
    path('resume/',    include(('resumes.urls', 'resumes'), namespace='resumes')),
    path('accounts/',  include('allauth.urls')),
    path('resources/', include('resources.urls')),
    path('blog/',      include('blog.urls')),
    path('api/',       include('core.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
