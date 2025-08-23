from django.urls import path
from . import views

# Namespaced so templates can call {% url 'dashboard:home' %}
app_name = 'dashboard'

urlpatterns = [
    # ===== Router (decides user/employer/admin) =====
    path('', views.dashboard_router, name='my_dashboard'),  # /dashboard/

    # ===== Role dashboards =====
    path('user/', views.user_dashboard, name='user'),
    path('employer/', views.employer_dashboard, name='employer'),
    path('admin/', views.admin_dashboard, name='admin'),

    # ===== User features =====
    path('saved-jobs/', views.saved_jobs_view, name='saved_jobs'),
    path('matches/', views.matched_jobs_view, name='matched_jobs'),

    # ===== Employer analytics =====
    path('employer/analytics/', views.employer_analytics, name='employer_analytics'),
]
