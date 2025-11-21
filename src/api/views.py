from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit
from django.db import DatabaseError
from django.conf import settings
from .models import LicenseKey, Device, FullReport, DiffReport, DeviceEvent, EnrollmentSettings
from .forms import ReportUploadForm
from api.utils.lynis_report import LynisReport
from api.utils.error_responses import internal_error
from api.utils.license_utils import validate_license, check_license_capacity
#from utils.diff_utils import generate_diff, analyze_diff
import os
import logging
import re
from urllib.parse import urlparse

@csrf_exempt
@ratelimit(key='ip', rate='100/h', method='POST')
def upload_report(request):
    logging.debug('Uploading report...')
    if request.method == 'POST':
        form = ReportUploadForm(request.POST)
        if form.is_valid():
            report_data = form.cleaned_data['data']
            post_licensekey = form.cleaned_data['licensekey']
            post_hostid = form.cleaned_data['hostid']
            post_hostid2 = form.cleaned_data['hostid2']

            logging.debug(f'License key: {post_licensekey}')
            logging.debug(f'Host ID: {post_hostid}')

            # Check if the license key is valid
            # Keep original response format for Lynis compatibility
            try:
                is_valid, error_msg = validate_license(post_licensekey)
                if not is_valid:
                    logging.error(f'License validation failed: {error_msg}')
                    return HttpResponse(error_msg or 'Invalid license key', status=401)
                
                licensekey = LicenseKey.objects.get(licensekey=post_licensekey)
            except LicenseKey.DoesNotExist:
                logging.error('License key does not exist')
                return HttpResponse('Invalid license key', status=401)
            except DatabaseError as e:
                logging.error(f'Database error checking license key: {e}')
                return internal_error('Database error while checking license key')

            if not post_hostid or not post_hostid2:
                logging.error('Host ID not found')
                return HttpResponse('Host ID not found', status=400)
            
            # Check if the report has been correctly uploaded
            if not report_data:
                logging.error('No report found')
                return HttpResponse('No report found', status=400)

            # Check if the device already exists
            try:
                device = Device.objects.filter(hostid=post_hostid, hostid2=post_hostid2, licensekey=licensekey).first()
                created = device is None
                
                # If device doesn't exist, check license capacity before creating
                if created:
                    has_capacity, capacity_error = check_license_capacity(post_licensekey)
                    if not has_capacity:
                        logging.error(f'License capacity check failed: {capacity_error}')
                        return HttpResponse(capacity_error or 'License has reached maximum device limit', status=403)
                    
                    # Create the new device
                    device = Device.objects.create(hostid=post_hostid, hostid2=post_hostid2, licensekey=licensekey)
                    DeviceEvent.objects.create(device=device, event_type='enrolled')
            except DatabaseError as e:
                logging.error(f'Database error creating/retrieving device: {e}')
                return internal_error('Database error while processing device')
            
            try:
                latest_full_report = FullReport.objects.filter(device=device).order_by('-created_at').first()
            except DatabaseError as e:
                logging.error(f'Database error retrieving previous report: {e}')
                return internal_error('Database error while retrieving previous report')
            
            if latest_full_report:
                # Generate the diff and save it
                try:
                    latest_lynis = LynisReport(latest_full_report.full_report)
                    # Don't filter at diff creation time - filter only at display time
                    # This ensures all activities are stored and can be shown/hidden based on current rule state
                    # Filtering happens in the activity view (frontend/views.py) based on active silence rules
                    
                    # Generate structured diff (without ignore_keys - store all activities)
                    diff_data = latest_lynis.compare_reports(report_data, [])
                    DiffReport.objects.create(device=device, diff_report=diff_data)
                    logging.info(f'Diff created for device {post_hostid}')
                    logging.debug('Changed items: %s', diff_data)
                except DatabaseError as e:
                    logging.error(f'Database error creating diff report: {e}')
                    return internal_error('Database error while creating diff report')
            else:
                logging.info(f'No previous reports found for device {post_hostid}')
            
            # Save the new full report
            try:
                FullReport.objects.create(device=device, full_report=report_data)
            except DatabaseError as e:
                logging.error(f'Database error saving full report: {e}')
                return internal_error('Database error while saving report')

            # Parse the new report
            try:
                report = LynisReport(report_data)
            except Exception as e:
                logging.error(f'Error parsing report: {e}')
                return internal_error('Error parsing report data')
            
            # Update device information (get most important keys)
            try:
                device.licensekey = licensekey
                device.hostname = report.get('hostname')    
                device.os = report.get('os')
                device.distro = report.get('os_fullname')
                device.distro_version = report.get('os_version')
                device.lynis_version = report.get('lynis_version')
                device.last_update = report.get('report_datetime_end')
                device.warnings = report.get('warning_count')
                device.save()
            except DatabaseError as e:
                logging.error(f'Database error updating device: {e}')
                return internal_error('Database error while updating device')

            logging.info(f'Device updated: {report.get("hostname")}')
            return HttpResponse('OK')
        return HttpResponse('Invalid form data', status=400)
    return HttpResponse('Invalid request method', status=405)

@csrf_exempt
@ratelimit(key='ip', rate='50/h', method='POST')
def check_license(request):
    if request.method == 'POST':
        post_licensekey = request.POST.get('licensekey')
        post_collector_version = request.POST.get('collector_version')

        if not post_licensekey:
            logging.error('No license key provided')
            return HttpResponse('No license key provided', status=400)

        if not post_collector_version:
            logging.error('No collector version provided')
            return HttpResponse('No collector version provided', status=400)

        # Keep original response format for Lynis compatibility
        try:
            is_valid, error_msg = validate_license(post_licensekey)
            if is_valid:
                logging.info('License key is valid')
                return HttpResponse('Response 100')
            else:
                logging.error(f'License key is invalid: {error_msg}')
                return HttpResponse('Response 500', status=401)
        except DatabaseError as e:
            logging.error(f'Database error checking license: {e}')
            return internal_error('Database error while checking license')
    return HttpResponse('Invalid request method', status=405)

@csrf_exempt
def enroll_sh(request):
    """Generate enroll bash script to install the agent on a new device."""
    licensekey = request.GET.get('licensekey', '').strip()
    if not licensekey:
        return HttpResponse('No license key provided', status=400)
    if not re.match(r'^[a-zA-Z0-9_-]+$', licensekey) or len(licensekey) > 255:
        return HttpResponse('Invalid license key format', status=400)
    if not LicenseKey.objects.filter(licensekey=licensekey).exists():
        return HttpResponse('Invalid license key', status=401)

    trikusec_lynis_api_url = settings.TRIKUSEC_LYNIS_API_URL
    parsed_lynis_api_url = urlparse(trikusec_lynis_api_url)
    trikusec_lynis_upload_server = parsed_lynis_api_url.netloc
    enrollment_settings = EnrollmentSettings.get_settings()
    additional_packages = enrollment_settings.additional_packages.strip()
    skip_tests = ','.join(enrollment_settings.skip_test_ids)
    plugin_urls = [url.strip() for url in enrollment_settings.plugin_urls if url.strip()]

    context = {
        'trikusec_lynis_upload_server': trikusec_lynis_upload_server,
        'licensekey': licensekey,
        'ignore_ssl_errors': enrollment_settings.ignore_ssl_errors,
        'overwrite_lynis_profile': enrollment_settings.overwrite_lynis_profile,
        'additional_packages': additional_packages,
        'skip_tests': skip_tests,
        'plugin_urls': plugin_urls,
    }
    return render(request, 'api/enroll.sh', context, content_type='text/x-shellscript')

def index(request):
    return HttpResponse('Hello, world. You\'re at the TrikuSec index.')