from django.urls import path
from . import views
from .views import dashboard

urlpatterns = [
    path('get-started/', views.redirect_to_first_step, name='multi_step_form'),
    path('step/<int:step>/', views.multi_step_form_view, name='profile_step'),
    path('dashboard/', views.dashboard_view, name='dashboard'),  # New!
    path('update/', views.update_profile, name='update_profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('upload-profile-picture/', views.upload_profile_picture, name='upload_profile_picture'),
    path('delete-profile-picture/', views.delete_profile_picture, name='delete_profile_picture'),
    path('', dashboard, name='dashboard'),



]
