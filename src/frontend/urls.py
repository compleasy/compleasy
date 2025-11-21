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
    path('profile/', views.profile, name='profile'),
    path('onboarding/', views.onboarding, name='onboarding'),
    path('devices/', views.device_list, name='device_list'),
    path('device/<int:device_id>/', views.device_detail, name='device_detail'),
    path('device/<int:device_id>/edit/', views.device_update, name='device_update'),
    path('device/<int:device_id>/export-pdf/', views.device_export_pdf, name='device_export_pdf'),
    path('device/<int:device_id>/delete/', views.device_delete, name='device_delete'),
    path('device/<int:device_id>/report/', views.device_report, name='device_report'),
    path('device/<int:device_id>/report/json/', views.device_report_json, name='device_report_json'),
    path('device/<int:device_id>/rule/<int:rule_id>/evaluate/', views.rule_evaluate_for_device, name='rule_evaluate_for_device'),
    path('device/<int:device_id>/report/changelog/', views.device_report_changelog, name='device_report_changelog'),
    path('policies/', views.policy_list, name='policy_list'),
    # Backward compatibility redirect
    path('rulesets/', views.policy_list, name='ruleset_list'),
    path('ruleset/<int:ruleset_id>/', views.ruleset_detail, name='ruleset_detail'),
    path('ruleset/create/', views.ruleset_create, name='ruleset_create'),
    path('ruleset/<int:ruleset_id>/edit/', views.ruleset_update, name='ruleset_update'),
    path('ruleset/<int:ruleset_id>/delete/', views.ruleset_delete, name='ruleset_delete'),
    path('rules/', views.rule_list, name='rule_list'),
    path('rule/<int:rule_id>/', views.rule_detail, name='rule_detail'),
    path('rule/create/', views.rule_create, name='rule_create'),
    path('rule/<int:rule_id>/edit/', views.rule_update, name='rule_update'),
    path('rule/<int:rule_id>/delete/', views.rule_delete, name='rule_delete'),
    path('activity/', views.activity, name='activity'),
    path('activity/silence/', views.silence_rule_list, name='silence_rule_list'),
    path('activity/silence/create/', views.silence_rule_create, name='silence_rule_create'),
    path('activity/silence/<int:rule_id>/edit/', views.silence_rule_edit, name='silence_rule_edit'),
    path('activity/silence/<int:rule_id>/delete/', views.silence_rule_delete, name='silence_rule_delete'),
    path('activity/silence/<int:rule_id>/toggle/', views.silence_rule_toggle, name='silence_rule_toggle'),
    path('licenses/', views.license_list, name='license_list'),
    path('licenses/create/', views.license_create, name='license_create'),
    path('license/<int:license_id>/', views.license_detail, name='license_detail'),
    path('license/<int:license_id>/edit/', views.license_edit, name='license_edit'),
    path('license/<int:license_id>/delete/', views.license_delete, name='license_delete'),
    path('enroll/', views.enroll_device, name='enroll_device'),
]