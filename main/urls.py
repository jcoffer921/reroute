from django.urls import path, include 
from django.urls import path
from . import views
from .views import signup_view
from django.contrib.auth import views as auth_views
from .views import signup_view, home  # Add your custom views as needed
from .views import signup_view, home, dashboard_view
from . import views
from .forms import Step1Form, Step2Form, Step3Form, Step4Form


urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', include('profiles.urls')),
    #path('get-started/', GetStartedWizard.as_view([Step1Form, Step2Form, Step3Form, Step4Form]), name='get_started'),
    path('opportunities/', views.job_list, name='job_list'),
    path('match/<int:seeker_id>/', views.match_jobs, name='match_jobs'),
    path('signup/', signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('resume/create/', views.create_resume_redirect, name='create_resume'),
    path('profile/', include('profiles.urls')),  # leads to /profile/update/



]
