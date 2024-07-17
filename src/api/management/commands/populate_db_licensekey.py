from django.core.management.base import BaseCommand
from api.models import LicenseKey  # Import your models here
import random
import string

class Command(BaseCommand):
    help = 'Generate a random license key and add it to the database'

    def handle(self, *args, **kwargs):
        if LicenseKey.objects.exists():
            self.stdout.write(self.style.SUCCESS('License key already exists in the database'))
            return
        
        # Generate a random license key
        license_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))

        # Add the license key to the database
        LicenseKey.objects.create(licensekey=license_key)

        self.stdout.write(self.style.SUCCESS('Successfully generated and added a license key to the database'))
