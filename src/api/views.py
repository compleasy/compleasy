from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import LicenseKey, Device, FullReport, DiffReport
from .forms import ReportUploadForm
from utils.lynis_report import LynisReport
from utils.diff_utils import generate_diff, analyze_diff
import os
import logging

'''def read_config_envars():
    config = {}
    for key, value in os.environ.items():
        if key.startswith('COMPLEASY_'):
            config[key] = value
    return config'''

def init_db(request):
    if request.GET.get('delete') and request.GET.get('delete').lower() == 'true':
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'compleasy.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            logging.info('Database deleted')
    # Reinitialize the database (usually handled by migrations)
    return HttpResponse('Database initialized')

@csrf_exempt
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
            if not LicenseKey.objects.filter(licensekey=post_licensekey).exists():
                return HttpResponse('Invalid license key', status=401)
            else:
                licensekey = LicenseKey.objects.get(licensekey=post_licensekey)

            if not post_hostid or not post_hostid2:
                logging.error('Host ID not found')
                return HttpResponse('Host ID not found', status=400)
            
            # Check if the report has been correctly uploaded
            if not report_data:
                logging.error('No report found')
                return HttpResponse('No report found', status=400)

            # Check if the device already exists. If not, create it
            device, created = Device.objects.get_or_create(hostid=post_hostid, hostid2=post_hostid2, licensekey=licensekey)
            
            latest_full_report = FullReport.objects.filter(device=device).order_by('-created_at').first()
            
            if latest_full_report:
                # Generate diff and save it
                diff = generate_diff(latest_full_report.full_report, report_data)
                DiffReport.objects.create(device=device, diff_report=diff)
                logging.info(f'Diff created for device {post_hostid}')

                # Analyze the diff (debugging purposes)
                changed_items = analyze_diff(diff)
                logging.debug('Changed items: %s', changed_items)
            else:
                logging.info(f'No previous reports found for device {post_hostid}')
            
            # Save the new full report
            FullReport.objects.create(device=device, full_report=report_data)

            # Parse the new report
            report = LynisReport(report_data)
            
            # Update device information (get most important keys)
            device.licensekey = licensekey
            device.hostname = report.get('hostname')    
            device.os = report.get('os')
            device.distro = report.get('os_fullname')
            device.distro_version = report.get('os_version')
            device.lynis_version = report.get('lynis_version')
            device.last_update = report.get('report_datetime_end')
            device.warnings = report.get('count_warnings')
            device.save()

            logging.info(f'Device updated: {report.get("hostname")}')
            return HttpResponse('OK')
        return HttpResponse('Invalid form data', status=400)
    return HttpResponse('Invalid request method', status=405)

@csrf_exempt
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

        if LicenseKey.objects.filter(licensekey=post_licensekey).exists():
            logging.info('License key is valid')
            return HttpResponse('Response 100')
        else:
            logging.error('License key is invalid')
            return HttpResponse('Response 500', status=401)
    return HttpResponse('Invalid request method', status=405)

def index(request):
    return HttpResponse('Hello, world. You\'re at the Compleasy index.')