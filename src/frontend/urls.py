from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('devices/', views.device_list, name='device_list'),
    path('reports/', views.report_list, name='report_list'),
]