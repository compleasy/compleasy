from django.contrib import admin
from .models import LicenseKey, Device, FullReport

@admin.register(LicenseKey)
class LicenseKeyAdmin(admin.ModelAdmin):
    list_display = ('licensekey', 'created_at')


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('hostid', 'hostid2', 'hostname', 'os', 'distro', 'distro_version', 'lynis_version', 'last_update', 'warnings')

@admin.register(FullReport)
class FullReportAdmin(admin.ModelAdmin):
    list_display = ('device', 'full_report', 'created_at')