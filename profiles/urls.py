from django.urls import path
from . import views
from .views import public_profile_view, remove_profile_picture, update_personal_info
from .views import update_profile_picture



urlpatterns = [
    path('view/<str:username>/', public_profile_view, name='public_profile'),
    path('profile/<str:username>/', views.public_profile_view, name='profile'),


    path('step/<int:step>/', views.multi_step_form_view, name='profile_step'),


    path('update/', views.update_profile, name='update_profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('update-picture/', update_profile_picture, name='update_profile_picture'),
    path('update/personal-info/', update_personal_info, name='update_personal_info'),
    path('update/employment/', views.update_employment_info, name='update_employment_info'),
    path('profile/update/emergency/', views.update_emergency_contact, name='update_emergency_contact'),
    path('profile/update/demographics/', views.update_demographics, name='update_demographics'),
    path('profile/remove-picture/', remove_profile_picture, name='remove_profile_picture'),
    path('profile/update/bio/', views.update_bio, name='update_bio'),




    #path('delete-picture/', views.delete_profile_picture, name='delete_profile_picture'),



]
