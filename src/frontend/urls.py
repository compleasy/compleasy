from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('onboarding/', views.onboarding, name='onboarding'),
    path('download/enroll.sh', views.enroll_sh, name='enroll_sh'),
    path('download/lynis_custom_profile', views.download_lynis_custom_profile, name='download_lynis_custom_profile'),
    path('devices/', views.device_list, name='device_list'),
    path('device/<int:device_id>/', views.device_detail, name='device_detail'),
]