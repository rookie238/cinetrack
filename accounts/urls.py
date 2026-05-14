"""Accounts URL routing — auth + profile + AJAX follow endpoint'leri."""
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_self_view, name='profile_self'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('u/<str:username>/', views.profile_detail_view, name='profile_detail'),
    path('u/<str:username>/follow/', views.toggle_follow_view, name='follow_toggle'),
]
