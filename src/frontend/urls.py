from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('onboarding/', views.onboarding, name='onboarding'),
    path('devices/', views.device_list, name='device_list'),
    path('device/<int:device_id>/', views.device_detail, name='device_detail'),
    path('reports/', views.report_list, name='report_list'),
    path('report/<int:report_id>/', views.report_detail, name='report_detail'),
]