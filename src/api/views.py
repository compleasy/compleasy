from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import LicenseKey, Device, FullReport
from .forms import ReportUploadForm
from utils.lynis_report import LynisReport
import os
import logging

logger = logging.getLogger('Compleasy')

def read_config_file():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yml')
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def read_config_envars():
    config = {}
    for key, value in os.environ.items():
        if key.startswith('COMPLEASY_'):
            config[key] = value
    return config

def init_db(request):
    if request.GET.get('delete') and request.GET.get('delete').lower() == 'true':
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'compleasy.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            logging.info('Database deleted')
    # Reinitialize the database (usually handled by migrations)
    return HttpResponse('Database initialized')

@csrf_exempt
def add_license(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        licensekey = request.POST.get('licensekey')

        if token != config.get('token'):
            return HttpResponse('Invalid token', status=401)

        if licensekey:
            LicenseKey.objects.create(licensekey=licensekey)
            return HttpResponse('License key added')
        return HttpResponse('No license key provided', status=400)
    return HttpResponse('Invalid request method', status=405)

@csrf_exempt
def upload_report(request):
    if request.method == 'POST':
        form = ReportUploadForm(request.POST)
        if form.is_valid():
            report = form.cleaned_data['data']
            licensekey = form.cleaned_data['licensekey']
            hostid = form.cleaned_data['hostid']
            hostid2 = form.cleaned_data['hostid2']

            logging.debug(f'License key: {licensekey}')
            logging.debug(f'Host ID: {hostid}')

            if not LicenseKey.objects.filter(licensekey=licensekey).exists():
                return HttpResponse('Invalid license key', status=401)

            lynis_report = LynisReport(report)
            hostid = lynis_report.get('hostid')
            hostid2 = lynis_report.get('hostid2')

            if not hostid or not hostid2:
                logging.error('Host ID not found in the report')
                return HttpResponse('Host ID not found', status=400)

            device, created = Device.objects.get_or_create(hostid=hostid, hostid2=hostid2)
            full_report = lynis_report.get_full_report()
            if not full_report:
                logging.error('Error reading full report')
                return HttpResponse('Error parsing report', status=500)

            FullReport.objects.create(device=device, full_report=full_report)
            logging.info(f'Full report stored for device: {lynis_report.get("hostname")}')

            parsed_report = lynis_report.parse_report()
            # Check if parsed keys are empty: {}
            if not parsed_report:
                logging.error('Error parsing report')
                return HttpResponse('Error parsing report', status=500)

            # Update device information (get most important keys)
            device.hostname = parsed_report.get('hostname')    
            device.os = parsed_report.get('os')
            device.distro = parsed_report.get('os_fullname')
            device.distro_version = parsed_report.get('os_version')
            device.lynis_version = parsed_report.get('lynis_version')
            device.last_update = parsed_report.get('report_datetime_end')
            device.warnings = parsed_report.get('count_warnings')
            device.save()

            logging.info(f'Device updated: {parsed_report.get("hostname")}')
            return HttpResponse('OK')
        return HttpResponse('Invalid form data', status=400)
    return HttpResponse('Invalid request method', status=405)

@csrf_exempt
def check_license(request):
    if request.method == 'POST':
        licensekey = request.POST.get('licensekey')
        collector_version = request.POST.get('collector_version')

        if not licensekey:
            logging.error('No license key provided')
            return HttpResponse('No license key provided', status=400)

        if not collector_version:
            logging.error('No collector version provided')
            return HttpResponse('No collector version provided', status=400)

        if LicenseKey.objects.filter(licensekey=licensekey).exists():
            logging.info('License key is valid')
            return HttpResponse('Response 100')
        else:
            logging.error('License key is invalid')
            return HttpResponse('Response 500', status=401)
    return HttpResponse('Invalid request method', status=405)

@csrf_exempt
def get_licenses(request):
    licenses = LicenseKey.objects.all().values()
    return JsonResponse(list(licenses), safe=False)

@csrf_exempt
def get_reports(request):
    reports = FullReport.objects.all().values()
    return JsonResponse(list(reports), safe=False)

@csrf_exempt
def get_devices(request):
    devices = Device.objects.all().values()
    return JsonResponse(list(devices), safe=False)

'''def index(request):
    devices = Device.objects.all()
    for d in devices:
        logging.info('Device hostname: %s', d.hostname)
    return render(request, 'index.html', {'devices': devices})

'''

def index(request):
    return HttpResponse('Hello, world. You\'re at the Compleasy index.')