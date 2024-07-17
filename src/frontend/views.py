from django.shortcuts import render, redirect
from django.http import HttpResponse
from api.models import Device, FullReport
from utils.lynis_report import LynisReport
import os

def index(request):
    devices = Device.objects.all()
    if not devices:
        return redirect('onboarding')
    return render(request, 'index.html', {'devices': devices})

def onboarding(request):
    compleasy_url = os.getenv('COMPLEASY_URL')
    return render(request, 'onboarding.html', {'compleasy_url': compleasy_url})

def device_list(request):
    return render(request, 'device_list.html')

def report_list(request):
    return render(request, 'report_list.html')

def device_detail(request, device_id):
    warnings = {}
    suggestions = {}
    device = Device.objects.get(id=device_id)
    # Get last report for the device
    report = FullReport.objects.filter(device=device).order_by('-created_at').first()

    # If no report found, error message
    if not report:
        return HttpResponse('No report found for the device', status=404)
    
    report = LynisReport(report.full_report)
    report = report.parse_report()

    if not report:
        return HttpResponse('Failed to parse the report', status=500)
    
    # Print suggestions
    suggestions = report.get('suggestion', [])
    print('Suggestions:')
    for suggestion in suggestions:
        print(f'  - {suggestion}')

    return render(request, 'device_detail.html', {'device': device, 'report': report})

def report_detail(request, report_id):
    return render(request, 'report_detail.html')

def enroll_sh(request):
    # Get the server url from environment variable
    compleasy_url = os.getenv('COMPLEASY_URL')
    return render(request, 'enroll.html', {'compleasy_url': compleasy_url})