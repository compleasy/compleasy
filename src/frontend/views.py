from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from api.models import Device, FullReport, DiffReport, LicenseKey, PolicyRule, PolicyRuleset
from utils.lynis_report import LynisReport
from .forms import PolicyRulesetForm, PolicyRuleForm
import os
import json
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
def ruleset_list(request):
    """Policy list view: show all policy rulesets"""
    policy_rulesets = PolicyRuleset.objects.prefetch_related('rules').all()
    policy_rules = PolicyRule.objects.values()
    if not policy_rulesets:
        return HttpResponse('No policy rulesets found', status=404)
    
    rulesets_data = []
    for ruleset in policy_rulesets:
        # Get the rule count for the ruleset
        ruleset_data = {
            'id': ruleset.id,
            'name': ruleset.name,
            'description': ruleset.description,
            'created_at': ruleset.created_at,
            'updated_at': ruleset.updated_at,
            'rules': list(ruleset.rules.values()),
            'devices': list(ruleset.devices.values()),
            'rules_count': ruleset.rules.count(),
            'devices_count': ruleset.devices.count()
        }
        rulesets_data.append(ruleset_data)
    
    context = {
        'rulesets': rulesets_data,
        'rules': list(policy_rules),
        'rules_count': len(policy_rules)
    }
    
    return render(request, 'policy/ruleset_list.html', context)

@login_required
def ruleset_create(request):
    if request.method == 'POST':
        form = PolicyRulesetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ruleset_list')
    else:
        form = PolicyRulesetForm()
    
    return render(request, 'policy/ruleset_form.html', {'form': form})

@login_required
def ruleset_detail(request, ruleset_id):
    ruleset = get_object_or_404(PolicyRuleset, id=ruleset_id)
    if request.method == 'POST':
        form = PolicyRulesetForm(request.POST, instance=ruleset)
        if form.is_valid():
            form.save()
            return redirect('ruleset_detail', ruleset_id=ruleset.id)
    else:
        form = PolicyRulesetForm(instance=ruleset)
    return render(request, 'policy/ruleset_form.html', {'form': form, 'ruleset': ruleset})


@csrf_protect
@login_required
def ruleset_update(request, ruleset_id):
    """Update the rules of a policy ruleset"""
    if request.method == 'POST':
        selected_rule_ids = request.POST.getlist('rules')
        if not ruleset_id:
            return HttpResponse('No ruleset ID provided', status=400)
        
        # Get the PolicyRuleset object
        ruleset = get_object_or_404(PolicyRuleset, id=ruleset_id)
        # Get the PolicyRule objects for the selected rules
        selected_rules = PolicyRule.objects.filter(id__in=selected_rule_ids)
        if selected_rules:
            ruleset.rules.set(selected_rules)
        ruleset.save()
        return redirect('ruleset_list')
    return HttpResponse('Invalid request method', status=405)

@login_required
def ruleset_add(request):
    """Policy add view: add a new policy ruleset"""
    return render(request, 'policy/ruleset_form.html')

@login_required
def ruleset_delete(request, ruleset_id):
    """Policy delete view: delete a policy ruleset"""
    policy_ruleset = get_object_or_404(PolicyRuleset, id=ruleset_id)
    policy_ruleset.delete()
    return redirect('ruleset_list')

@login_required
def rule_list(request):
    """Rule list view: show all policy rules"""
    policy_rules = PolicyRule.objects.all()
    if not policy_rules:
        return HttpResponse('No policy rules found', status=404)
    
    return render(request, 'policy/rule_list.html', {'rules': policy_rules})

@login_required
def rule_detail(request, rule_id):
    """Rule detail view: show the details of a policy rule"""
    rule = get_object_or_404(PolicyRule, id=rule_id)
    if request.method == 'POST':
        form = PolicyRuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            return redirect('ruleset_detail', ruleset_id=rule.id)
    else:
        form = PolicyRuleForm(instance=rule)
    return render(request, 'policy/rule_detail.html', {'form': form, 'rule': rule})

@login_required
def rule_update(request, rule_id):
    """Rule update view: update a policy rule"""
    policy_rule = get_object_or_404(PolicyRule, id=rule_id)
    if request.method == 'POST':
        logging.debug('Request POST: %s', request.POST)
        policy_rule.name = request.POST.get('name')
        policy_rule.description = request.POST.get('description')
        policy_rule.rule_query = request.POST.get('rule_query')
        policy_rule.save()
        return redirect('rule_list')
    return render(request, 'policy/rule_detail.html', {'rule': policy_rule})

@login_required
def rule_create(request):
    """Rule create view: create a new policy rule"""
    if request.method == 'POST':
        form = PolicyRuleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('rule_list')
    else:
        form = PolicyRuleForm()
    return render(request, 'policy/rule_detail.html', {'form': form})

@login_required
def rule_add(request):
    """Rule add view: add a new policy rule"""
    return render(request, 'policy/rule_form.html')


@login_required
def activity(request):
    """Activity view: show the activity of the devices (from DiffReport)"""

    # TODO: adapt activities to the template's needs

    # My activity list with the devices and the changelog (added lines, removed lines and changed lines)
    activities = []
    max_activities = 50

    # Get all diff reports (from most recent to oldest)
    diff_reports = DiffReport.objects.all().order_by('-created_at')

    if not diff_reports:
        return HttpResponse('No activity found', status=404)
    
    # Let's humanize the diff reports to show them in the template
    for diff_report in diff_reports:
        if len(activities) >= max_activities:
            break
        
        diff = diff_report.diff_report

        # Ignore some noisy or irrelevant keys
        ignore_keys = [
            'report_datetime_start',
            'report_datetime_end',
            'slow_test',
            'uptime_in_seconds',
            'uptime_in_days',
            'deleted_file',
            'lynis_timer_next_trigger',
            'clamav_last_update',
            'tests_executed',
            'tests_skipped',
            'installed_packages_array',
            'vulnerable_package',
            'suggestion',
        ]

        lynis_diff = LynisReport.Diff(diff)
        # Generate a LynisReport object with the diff
        diff_analysis = lynis_diff.analyze(ignore_keys)

        # Check if 'added' and 'removed' keys are in the diff_analysis
        if 'added' in diff_analysis and 'removed' in diff_analysis:
            for change_type in ['added', 'removed']:
                logging.debug('Change type: %s', change_type)
                for key in diff_analysis[change_type]:
                    logging.debug('Added/removed Key: %s', key)
                    values = diff_analysis[change_type][key]
                    # For every value in the list of values, append a new activity

                    for value in values:
                        activities.append({
                            'device': diff_report.device,
                            'created_at': diff_report.created_at,
                            'key': key,
                            'value': value,
                            'type': change_type
                        })

        if 'changed' in diff_analysis:
            for change in diff_analysis['changed']:
                # change = {'slow_test': {'old': [['DEB-0001', '17.179738'], ['PKGS-7392', '22.329404'], ['CRYP-7902', '28.998732']], 'new': [['DEB-0001', '19.197790'], ['PKGS-7345', '11.064739'], ['PKGS-7392', '17.606281'], ['CRYP-7902', '31.913178']]}}
                key = list(change.keys())[0]
                logging.debug('Changed key: %s', key)
                
                old_value = change[key]['old']
                new_value = change[key]['new']

                activities.append({
                    'device': diff_report.device,
                    'created_at': diff_report.created_at,
                    'key': key,
                    'old_value': old_value,
                    'new_value': new_value,
                    'type': 'changed'
                })

        # Order activities by date (most recent first) and type (added, removed, changed)
        activities = sorted(activities, key=lambda x: (x['created_at'], x['type']), reverse=True)
        
    return render(request, 'activity.html', {'activities': activities})