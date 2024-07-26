from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from api.models import Device, FullReport, DiffReport, LicenseKey
from utils.lynis_report import LynisReport
from utils.diff_utils import apply_diff
import os
import logging

@login_required
def index(request):
    devices = Device.objects.all()
    if not devices:
        return redirect('onboarding')
    return render(request, 'index.html', {'devices': devices})

@login_required
def onboarding(request):
    compleasy_url = os.getenv('COMPLEASY_URL')
    #TODO: allow license management. By now, we just get the last license key from the user
    user_license = LicenseKey.objects.filter(created_by=request.user).last()
    if not user_license:
        return HttpResponse('No license key found', status=404)
    
    user_licensekey = user_license.licensekey
    return render(request, 'onboarding.html', {'compleasy_url': compleasy_url, 'licensekey': user_licensekey})

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

#TODO: require login, add csrf token or license key
def enroll_sh(request):
    # Get license key from the URL
    licensekey = request.GET.get('licensekey')
    if not licensekey:
        return HttpResponse('No license key provided', status=400)
    # Should we check licensekey is valid?
    # By now we just render the enroll page with the license key

    # Get the server url from environment variable
    compleasy_url = os.getenv('COMPLEASY_URL')
    return render(request, 'enroll.html', {'compleasy_url': compleasy_url, 'licensekey': licensekey})

def download_lynis_custom_profile(request):
    # TODO: get Lynis version from the URL, so we can generate the profile for the specific version
    lynis_version = request.GET.get('lynis_version')
    if not lynis_version:
        # Assume version 2.7.5
        lynis_version = '2.7.5'
    logging.debug('Lynis version: %s', lynis_version)

    # Get the licensekey from the URL
    licensekey = request.GET.get('licensekey')
    if not licensekey:
        return HttpResponse('No license key provided', status=400)
    # Should we check licensekey is valid?
    # By bow we just generate a profile with the indicated license key
    
    server_address_without_proto = os.getenv('COMPLEASY_URL').split('://')[1]
    compleasy_upload_server = f'{server_address_without_proto}/api/lynis'
    return render(request, 'lynis_custom_profile.html',
                    {
                      'compleasy_upload_server': compleasy_upload_server,
                      'license_key': licensekey,
                      'lynis_version': lynis_version
                    },
                    content_type='text/plain')