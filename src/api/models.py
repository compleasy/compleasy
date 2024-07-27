from django.db import models
from django.contrib.auth.models import User
from .utils.policy_query import evaluate_query

class LicenseKey(models.Model):
    licensekey = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

class Device(models.Model):
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
    policy_ruleset = models.ManyToManyField('PolicyRuleset', related_name='devices', blank=True)
    compliant = models.BooleanField(default=True)

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

class PolicyRule(models.Model):
    name = models.CharField(max_length=255)
    rule_query = models.CharField(max_length=255)
    description = models.TextField()
    enabled = models.BooleanField(default=True)
    alert = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def evaluate(self, report):
        return evaluate_query(report, self.rule_query)

class PolicyRuleset(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    rules = models.ManyToManyField(PolicyRule)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def evaluate(self, report):
        for rule in self.rules.all():
            if not rule.evaluate(report):
                return False
        return True