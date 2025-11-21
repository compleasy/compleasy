from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .utils.policy_query import evaluate_query

class Organization(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class LicenseKey(models.Model):
    licensekey = models.CharField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    max_devices = models.IntegerField(null=True, blank=True)  # null=unlimited
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def device_count(self):
        return self.device_set.count()
    
    def has_capacity(self):
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        if self.max_devices is None:
            return True
        return self.device_count() < self.max_devices
    
    def __str__(self):
        return f"{self.name} ({self.licensekey[:8]}...)"

class Device(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    licensekey = models.ForeignKey(LicenseKey, on_delete=models.CASCADE)
    hostid = models.CharField(max_length=255, db_index=True)
    hostid2 = models.CharField(max_length=255, db_index=True)
    hostname = models.CharField(max_length=255, blank=True, null=True)
    os = models.CharField(max_length=255, blank=True, null=True)
    distro = models.CharField(max_length=255, blank=True, null=True)
    distro_version = models.CharField(max_length=255, blank=True, null=True)
    lynis_version = models.CharField(max_length=255, blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)
    warnings = models.IntegerField(blank=True, null=True)
    rulesets = models.ManyToManyField('PolicyRuleset', related_name='devices', blank=True)
    compliant = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['licensekey', 'hostid']),
            models.Index(fields=['licensekey', 'hostid2']),
            models.Index(fields=['last_update']),
        ]

class FullReport(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    full_report = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super(FullReport, self).save(*args, **kwargs)

class DiffReport(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    diff_report = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

class DeviceEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('enrolled', 'Device Enrolled'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device', '-created_at']),
            models.Index(fields=['event_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.device.hostname or self.device.hostid} - {self.get_event_type_display()}"

class ActivityIgnorePattern(models.Model):
    EVENT_TYPE_CHOICES = [
        ('all', 'All'),
        ('added', 'Added'),
        ('changed', 'Changed'),
        ('removed', 'Removed'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    key_pattern = models.CharField(max_length=255)
    event_type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES, default='all')
    host_pattern = models.CharField(max_length=255, default='*')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['organization', 'key_pattern', 'event_type', 'host_pattern']]
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['organization', 'event_type', 'is_active']),
        ]
    
    def __str__(self):
        event_type_label = dict(self.EVENT_TYPE_CHOICES).get(self.event_type, self.event_type)
        return f"{self.organization.name}: {self.key_pattern} ({event_type_label}, {self.host_pattern})"

class PolicyRule(models.Model):
    name = models.CharField(max_length=255)
    rule_query = models.CharField(max_length=255)
    description = models.TextField()
    enabled = models.BooleanField(default=True)
    alert = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_rules')
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def evaluate(self, report):
        return evaluate_query(report, self.rule_query)
    
    def __str__(self):
        return self.name

class PolicyRuleset(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    rules = models.ManyToManyField(PolicyRule)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_rulesets')
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def evaluate(self, report):
        for rule in self.rules.all():
            if rule.enabled and not rule.evaluate(report):
                return False
        return True
    
    def __str__(self):
        return self.name


class EnrollmentSettings(models.Model):
    """Singleton model storing global enrollment script configuration."""

    ignore_ssl_errors = models.BooleanField(default=False)
    overwrite_lynis_profile = models.BooleanField(default=False)
    additional_packages = models.CharField(max_length=255, default='rkhunter auditd')
    skip_tests = models.CharField(max_length=255, blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Enrollment Settings'
        verbose_name_plural = 'Enrollment Settings'

    def __str__(self):
        return 'Enrollment Settings'

    @classmethod
    def get_settings(cls):
        settings_instance = cls.objects.first()
        if settings_instance is None:
            settings_instance = cls.objects.create()
        return settings_instance