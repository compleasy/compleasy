from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('', views.index, name='index'),
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('onboarding/', views.onboarding, name='onboarding'),
    path('download/enroll.sh', views.enroll_sh, name='enroll_sh'),
    path('download/lynis_custom_profile', views.download_lynis_custom_profile, name='download_lynis_custom_profile'),
    path('devices/', views.device_list, name='device_list'),
    path('device/<int:device_id>/', views.device_detail, name='device_detail'),
    path('device/<int:device_id>/report/', views.device_report, name='device_report'),
    path('device/<int:device_id>/report/changelog/', views.device_report_changelog, name='device_report_changelog'),
    path('policies/', views.ruleset_list, name='ruleset_list'),
    path('policy/<int:ruleset_id>/', views.ruleset_edit, name='ruleset_edit'),
    path('activity/', views.activity, name='activity'),
]