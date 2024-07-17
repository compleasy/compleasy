from django.shortcuts import render
from django.http import HttpResponse
from api.models import Device, FullReport
from utils.lynis_report import LynisReport

def index(request):
    devices = Device.objects.all()
    return render(request, 'index.html', {'devices': devices})

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

    '''for warning in report['warnings']:
        # Warning format: TIME-3185|systemd-timesyncd did not synchronized the time recently.
        try:
            warning = warning.split('|')
            warnings[warning[0]] = warning[1]
        except:
            warnings[warning] = ''
    
    for suggestion in report['suggestions']:
        try:
            suggestion = suggestion.split('|')
            suggestions[suggestion[0]] = suggestion[1]
        except:
            suggestions[suggestion] = '''''

    return render(request, 'device_detail.html', {'device': device, 'report': report})

def report_detail(request, report_id):
    return render(request, 'report_detail.html')