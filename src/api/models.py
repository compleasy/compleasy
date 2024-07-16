from django.db import models

class LicenseKey(models.Model):
    licensekey = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class Device(models.Model):
    hostid = models.CharField(max_length=255)
    hostid2 = models.CharField(max_length=255)
    hostname = models.CharField(max_length=255, blank=True, null=True)
    os = models.CharField(max_length=255, blank=True, null=True)
    distro = models.CharField(max_length=255, blank=True, null=True)
    distro_version = models.CharField(max_length=255, blank=True, null=True)
    lynis_version = models.CharField(max_length=255, blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)
    warnings = models.IntegerField(blank=True, null=True)

class FullReport(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    full_report = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
