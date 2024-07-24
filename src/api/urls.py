# api/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('lynis/upload/', views.upload_report, name='upload_report'),
    path('lynis/license/', views.check_license, name='check_license'),
]
