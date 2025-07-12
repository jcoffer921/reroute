from django.urls import path
from .views import blog_detail

urlpatterns = [
    path('<slug:slug>/', blog_detail, name='blog_detail'),
]
