from django.urls import path
from . import views

urlpatterns = [
    path('user/', views.user_dashboard, name='user_dashboard'),
    path('employer/', views.employer_dashboard, name='employer_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
]
