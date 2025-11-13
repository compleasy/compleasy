from django.contrib import admin
from django.utils.html import format_html
from .models import LicenseKey, Device, FullReport, DiffReport, PolicyRule, PolicyRuleset

@admin.register(LicenseKey)
class LicenseKeyAdmin(admin.ModelAdmin):
    list_display = ('licensekey', 'created_by', 'created_at', 'device_count')
    list_filter = ('created_at', 'created_by')
    search_fields = ('licensekey', 'created_by__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def device_count(self, obj):
        return obj.device_set.count()
    device_count.short_description = 'Devices'

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'hostid', 'os_display', 'lynis_version', 'warnings', 'compliance_status', 'last_update')
    list_filter = ('compliant', 'os', 'created_at', 'last_update', 'licensekey')
    search_fields = ('hostname', 'hostid', 'hostid2', 'os', 'distro')
    readonly_fields = ('created_at', 'updated_at', 'hostid', 'hostid2')
    date_hierarchy = 'last_update'
    filter_horizontal = ('rulesets',)
    
    fieldsets = (
        ('Identification', {
            'fields': ('hostname', 'hostid', 'hostid2', 'licensekey')
        }),
        ('System Information', {
            'fields': ('os', 'distro', 'distro_version', 'lynis_version')
        }),
        ('Compliance', {
            'fields': ('warnings', 'compliant', 'rulesets')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_update'),
            'classes': ('collapse',)
        }),
    )
    
    def os_display(self, obj):
        if obj.distro:
            return f"{obj.os} - {obj.distro}"
        return obj.os
    os_display.short_description = 'Operating System'
    
    def compliance_status(self, obj):
        if obj.compliant:
            return format_html('<span style="color: green;">✓ Compliant</span>')
        return format_html('<span style="color: red;">✗ Non-compliant</span>')
    compliance_status.short_description = 'Status'

@admin.register(FullReport)
class FullReportAdmin(admin.ModelAdmin):
    list_display = ('device', 'created_at', 'report_preview')
    list_filter = ('created_at', 'device__licensekey')
    search_fields = ('device__hostname', 'device__hostid')
    readonly_fields = ('created_at', 'full_report')
    date_hierarchy = 'created_at'
    
    def report_preview(self, obj):
        preview = obj.full_report[:100] + '...' if len(obj.full_report) > 100 else obj.full_report
        return preview
    report_preview.short_description = 'Preview'

@admin.register(DiffReport)
class DiffReportAdmin(admin.ModelAdmin):
    list_display = ('device', 'created_at', 'diff_preview')
    list_filter = ('created_at', 'device__licensekey')
    search_fields = ('device__hostname', 'device__hostid')
    readonly_fields = ('created_at', 'diff_report')
    date_hierarchy = 'created_at'
    
    def diff_preview(self, obj):
        preview = obj.diff_report[:100] + '...' if len(obj.diff_report) > 100 else obj.diff_report
        return preview
    diff_preview.short_description = 'Preview'

@admin.register(PolicyRule)
class PolicyRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'rule_query', 'enabled', 'alert', 'rule_status', 'created_at', 'updated_at')
    list_filter = ('enabled', 'alert', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'rule_query')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Rule Configuration', {
            'fields': ('rule_query', 'enabled', 'alert')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rule_status(self, obj):
        if obj.enabled:
            status = '<span style="color: green;">● Active</span>'
            if obj.alert:
                status += ' <span style="color: orange;">[Alert]</span>'
            return format_html(status)
        return format_html('<span style="color: gray;">○ Disabled</span>')
    rule_status.short_description = 'Status'

@admin.register(PolicyRuleset)
class PolicyRulesetAdmin(admin.ModelAdmin):
    list_display = ('name', 'rule_count', 'device_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('rules',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Rules', {
            'fields': ('rules',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rule_count(self, obj):
        return obj.rules.count()
    rule_count.short_description = 'Rules'
    
    def device_count(self, obj):
        return obj.devices.count()
    device_count.short_description = 'Devices'