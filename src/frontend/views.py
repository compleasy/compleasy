from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from api.models import Device, FullReport, DiffReport, LicenseKey, PolicyRule, PolicyRuleset
from utils.lynis_report import LynisReport
import os
import logging

@login_required
def index(request):
    """Index view: redirect to the device list"""
    return redirect('device_list')

@login_required
def onboarding(request):
    """Onboarding view: show when no devices are found to help the user to enroll a new device"""
    compleasy_url = os.getenv('COMPLEASY_URL')
    #TODO: allow license management. By now, we just get the last license key from the user
    user_license = LicenseKey.objects.filter(created_by=request.user).last()
    if not user_license:
        return HttpResponse('No license key found', status=404)
    
    user_licensekey = user_license.licensekey
    return render(request, 'onboarding.html', {'compleasy_url': compleasy_url, 'licensekey': user_licensekey})

@login_required
def device_list(request):
    """Device list view: show all devices"""
    devices = Device.objects.all()
    if not devices:
        return redirect('onboarding')
    
    
    for device in devices:
        logging.debug('Checking compliance for device %s', device)

        # Get the PolicyRulesets that Device must comply with
        policy_rulesets = device.policy_ruleset.all()
        policy_rulesets = list(policy_rulesets)
        logging.debug('Policy rulesets: %s', policy_rulesets)

        device.compliant = True
        for policy_ruleset in policy_rulesets:
            logging.info("Checking compliance for device %s with policy ruleset %s", device, policy_ruleset)
            report = FullReport.objects.filter(device=device).order_by('-created_at').first()
            report = LynisReport(report.full_report)
            if not report:
                logging.error('No report found for device %s', device)
                continue

            if not policy_ruleset.evaluate(report):
                # Mark the device as non-compliant
                device.compliant = False
                logging.debug(f'Device {device} is not compliant with policy ruleset {policy_ruleset}')
                break
        device.save()

        # Order devices by last updated (most recent first)
        devices = Device.objects.all().order_by('-last_update')

    return render(request, 'device_list.html', {'devices': devices})

@login_required
def device_detail(request, device_id):
    """Device detail view: show the details of a device"""
    warnings = {}
    suggestions = {}
    device = Device.objects.get(id=device_id)
    
    # Get last report for the device
    report = FullReport.objects.filter(device=device).order_by('-created_at').first()

    # If no report found, error message
    if not report:
        return HttpResponse('No report found for the device', status=404)
    
    report = LynisReport(report.full_report)
    report = report.get_parsed_report()

    if not report:
        return HttpResponse('Failed to parse the report', status=500)
    
    # Get the PolicyRulesets that Device must comply with
    evaluated_rulesets = []
    policy_rulesets = device.policy_ruleset.all()
    for policy_ruleset in policy_rulesets:
        ruleset_dict = {
            'name': policy_ruleset.name,
            'description': policy_ruleset.description,
            'rules': []
        }
        
        for rule in policy_ruleset.rules.all():
            rule_dict = {
                'name': rule.name,
                'description': rule.description,
                'enabled': rule.enabled,
                'alert': rule.alert,
                'compliant': rule.evaluate(report)
            }
            ruleset_dict['rules'].append(rule_dict)
        # If any rule is not compliant, the ruleset is not compliant
        ruleset_dict['compliant'] = all([rule['compliant'] for rule in ruleset_dict['rules']])
        # Add the ruleset to the evaluated rulesets
        evaluated_rulesets.append(ruleset_dict)
    logging.debug('Evaluated rulesets: %s', evaluated_rulesets)

    return render(request, 'device_detail.html', {'device': device, 'report': report, 'evaluated_rulesets': evaluated_rulesets})

@login_required
def device_report(request, device_id):
    """Device report view: show the full report of a device"""
    device = get_object_or_404(Device, id=device_id)
    report = FullReport.objects.filter(device=device).order_by('-created_at').first()
    if not report:
        return HttpResponse('No report found for the device', status=404)
    report = LynisReport(report.full_report)

    # Get the parsed report in key=value format, one key per line
    parsed_report = report.get_parsed_report()
    parsed_report = '\n'.join([f'{key}={value}' for key, value in parsed_report.items()])
    return HttpResponse(parsed_report, content_type='text/plain')

@login_required
def device_report_changelog(request, device_id):
    """Device report changelog view: show all the changelogs of a device"""
    device = get_object_or_404(Device, id=device_id)
    changelog = DiffReport.objects.filter(device=device).order_by('-created_at')
    if not changelog:
        return HttpResponse('No changelog found for the device', status=404)
    return HttpResponse(changelog.values_list('diff_report', flat=True), content_type='text/plain')

def enroll_sh(request):
    """Enroll view: generate enroll bash script to install the agent on a new device"""
    # Get license key from the URL
    licensekey = request.GET.get('licensekey')
    if not licensekey:
        return HttpResponse('No license key provided', status=400)
    # Should we check licensekey is valid?
    # By now we just render the enroll page with the license key provided
    # If the license is not valid, the agent will not be able to send the reports

    # Get the server url from environment variable
    compleasy_url = os.getenv('COMPLEASY_URL')
    return render(request, 'enroll.html', {'compleasy_url': compleasy_url, 'licensekey': licensekey})

def download_lynis_custom_profile(request):
    """Generate a custom Lynis profile with the provided license key"""
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

@login_required
def activity(request):
    """Activity view: show the activity of the devices (from DiffReport)"""

    # TODO: adapt activities to the template's needs

    # My activity list with the devices and the changelog (added lines, removed lines and changed lines)
    activities = []
    max_activities = 30

    # Get all diff reports (from most recent to oldest)
    diff_reports = DiffReport.objects.all().order_by('-created_at')

    if not diff_reports:
        return HttpResponse('No activity found', status=404)
    
    # Let's humanize the diff reports to show them in the template
    for diff_report in diff_reports:
        if len(activities) >= max_activities:
            break
        
        diff = diff_report.diff_report
        ignore_keys = [
            'report_datetime_start',    # It's always different
            'report_datetime_end',      # It's always different
            'slow_test[]',              # It will repeat the same line every audit
            'uptime_in_seconds',        # It's always different
            'uptime_in_days',           # It's always different
            'deleted_file[]',           # Very noisy, is not relevant for the user
            'lynis_timer_next_trigger', # It's always different
            'clamav_last_update',       # It's always different (or should be)
            'tests_executed',           # Fix this
            'tests_skipped',             # Fix this
        ]
        #diff_analysis = analyze_diff(diff, ignore_keys=ignore_keys)
        lynis_diff = LynisReport.Diff(diff)
        diff_analysis = lynis_diff.analyze(ignore_keys)

        # Get the device
        device = diff_report.device

        for keyvalue in diff_analysis['added']:
            for key, value in keyvalue.items():
                value = LynisReport.LynisData(value).get()
                logging.debug('Added key: %s, value: %s', key, value)
                
                activities.append({
                    'device': device,
                    'created_at': diff_report.created_at,
                    'line': keyvalue,
                    'key': key,
                    'value': value,
                    'type': 'added'
                })
        
        for keyvalue in diff_analysis['removed']:
            for key, value in keyvalue.items():
                value = LynisReport.LynisData(value).get()
                logging.debug('Removed key: %s, value: %s', key, value)
                
                activities.append({
                    'device': device,
                    'created_at': diff_report.created_at,
                    'line': keyvalue,
                    'key': key,
                    'value': value,
                    'type': 'removed'
                })
        
        for keyvalue in diff_analysis['changed']:
            # Changed, keyvalue is a tuple with the key, old value and new value
            logging.debug('Keyvalue is: %s', keyvalue)

            # Get the key, old value and new value
            key, old_value, new_value = keyvalue
                
            activities.append({
                'device': device,
                'created_at': diff_report.created_at,
                'line': keyvalue,
                'key': key,
                'old_value': LynisReport.LynisData(old_value).get(),
                'new_value': LynisReport.LynisData(new_value).get(),
                'type': 'changed'
            })

        # Order activities by date (most recent first) and type (added, removed, changed)
        activities = sorted(activities, key=lambda x: (x['created_at'], x['type']), reverse=True)
        
    return render(request, 'activity.html', {'activities': activities})