from django.db import models
from django.contrib.auth.models import User

class LicenseKey(models.Model):
    licensekey = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

class Device(models.Model):
    report = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    licensekey = models.ForeignKey(LicenseKey, on_delete=models.CASCADE)
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

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super(FullReport, self).save(*args, **kwargs)
        # Keep only the latest 2 reports for each device
        reports = FullReport.objects.filter(device=self.device).order_by('-created_at')
        if reports.count() > 2:
            # Delete older reports except the latest 2
            for report in reports[2:]:
                report.delete()

class DiffReport(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    diff_report = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)