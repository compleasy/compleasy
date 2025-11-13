"""
Legacy API URLs for backward compatibility with Lynis clients.
DO NOT REMOVE - These endpoints are used by external Lynis installations.
"""
from django.urls import path
from . import views

# No app_name here - legacy endpoints have no namespace
urlpatterns = [
    path('', views.index, name='api_index_legacy'),
    path('lynis/upload/', views.upload_report, name='upload_report'),
    path('lynis/license/', views.check_license, name='check_license'),
]

