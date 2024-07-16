from django.shortcuts import render
from api.models import Device

def index(request):
    devices = Device.objects.all()
    return render(request, 'index.html', {'devices': devices})

def device_list(request):
    return render(request, 'frontend/device_list.html')

def report_list(request):
    return render(request, 'frontend/report_list.html')