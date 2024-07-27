from django.contrib import admin
from .models import LicenseKey, Device, FullReport, DiffReport, PolicyRule, PolicyRuleset

@admin.register(LicenseKey)
class LicenseKeyAdmin(admin.ModelAdmin):
    list_display = ('licensekey', 'created_at')


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'licensekey', 'created_at', 'updated_at', 'warnings')


@admin.register(FullReport)
class FullReportAdmin(admin.ModelAdmin):
    list_display = ('device', 'full_report', 'created_at')


@admin.register(DiffReport)
class DiffReportAdmin(admin.ModelAdmin):
    list_display = ('device', 'diff_report', 'created_at')

@admin.register(PolicyRule)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('name', 'rule_query', 'description', 'enabled', 'alert', 'created_at', 'updated_at')

@admin.register(PolicyRuleset)
class PolicyRulesetAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')