from django.db.models.signals import post_migrate
from django.dispatch import receiver
from api.models import LicenseKey
from django.core.management import call_command
import random
import string

@receiver(post_migrate)
def populate_data(sender, **kwargs):
    if sender.name == 'api':  # Make sure this is only run for the 'api' app
        if not LicenseKey.objects.exists():
            # Run populate_db command
            call_command('populate_db_licensekey')
