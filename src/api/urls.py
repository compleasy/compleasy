# api/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('lynis/upload/', views.upload_report, name='upload_report'),
    path('lynis/license/', views.check_license, name='check_license'),
    path('reports/', views.get_reports, name='get_reports'),
    path('devices/', views.get_devices, name='get_devices'),
]
