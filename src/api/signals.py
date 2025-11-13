from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from api.models import LicenseKey, FullReport
from django.core.management import call_command
from django.db import connection
import random
import string

'''
This signal is used to populate the database with a license key when the application is first run.
It will only if the database is SQLite and there are no tables in the database.
'''
@receiver(post_migrate)
def first_run(sender, **kwargs):
    if sender.name == 'api':
        if connection.settings_dict['ENGINE'] == 'django.db.backends.sqlite3':
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()

                if not tables:
                    call_command('migrate')
                    call_command('populate_db_licensekey')

@receiver(post_save, sender=FullReport)
def cleanup_old_reports(sender, instance, created, **kwargs):
    """
    Keep only the latest 2 reports for each device.
    This signal fires after a FullReport is saved.
    """
    if created:  # Only run for new reports
        reports = FullReport.objects.filter(device=instance.device).order_by('-created_at')
        if reports.count() > 2:
            # Delete older reports except the latest 2
            for report in reports[2:]:
                report.delete()
