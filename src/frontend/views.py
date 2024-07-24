from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from api.models import Device, FullReport, DiffReport, LicenseKey
from utils.lynis_report import LynisReport
from utils.diff_utils import apply_diff
import os

@login_required
def index(request):
    devices = Device.objects.all()
    if not devices:
        return redirect('onboarding')
    return render(request, 'index.html', {'devices': devices})

@login_required
def onboarding(request):
    compleasy_url = os.getenv('COMPLEASY_URL')
    return render(request, 'onboarding.html', {'compleasy_url': compleasy_url})

@login_required
def device_list(request):
    return render(request, 'device_list.html')

@login_required
def report_list(request):
    return render(request, 'report_list.html')

@login_required
def device_detail(request, device_id):
    warnings = {}
    suggestions = {}
    device = Device.objects.get(id=device_id)
    # Get last report for the device
    #report = FullReport.objects.filter(device=device).order_by('-created_at').first()
    report = FullReport.objects.filter(device=device).order_by('-created_at').first()

    # If no report found, error message
    if not report:
        return HttpResponse('No report found for the device', status=404)
    
    report = LynisReport(report.full_report)
    report = report.parse_report()

    if not report:
        return HttpResponse('Failed to parse the report', status=500)

    return render(request, 'device_detail.html', {'device': device, 'report': report})

@login_required
def get_full_report(request, device_id):
    device = get_object_or_404(Device, pk=device_id)
    
    # Get the latest full report
    full_report = FullReport.objects.filter(device=device).order_by('-created_at').first()
    if not full_report:
        return None
    
    full_report_data = full_report.full_report
    
    # Apply diffs to reconstruct the latest report
    diffs = DiffReport.objects.filter(device=device).order_by('created_at')
    for diff in diffs:
        full_report_data = apply_diff(full_report_data, diff.diff_report)
    
    return full_report_data

@login_required
def report_detail(request, report_id):
    return render(request, 'report_detail.html')

#TODO: require login, add csrf token or license key
def enroll_sh(request):
    # Get the server url from environment variable
    compleasy_url = os.getenv('COMPLEASY_URL')
    return render(request, 'enroll.html', {'compleasy_url': compleasy_url})

#TODO: require login, add csrf token or license key
def download_lynis_custom_profile(request):
    server_address_without_proto = os.getenv('COMPLEASY_URL').split('://')[1]
    compleasy_upload_server = f'{server_address_without_proto}/api/lynis'
    license_key = LicenseKey.objects.last().licensekey
    upload_options = "--insecure"
    return render(request, 'lynis_custom_profile.html',
                    {
                      'compleasy_upload_server': compleasy_upload_server,
                      'license_key': license_key,
                      'upload_options': upload_options
                    },
                    content_type='text/plain')