from django.core.management.base import BaseCommand
from api.models import LicenseKey  # Import your models here
import random
import string

class Command(BaseCommand):
    help = 'Generate a random license key and add it to the database'

    def generate_random_string(self, length):
        characters = 'abcdef0123456789'
        random_string = ''.join(random.choices(characters, k=length))
        return random_string

    def handle(self, *args, **kwargs):
        if LicenseKey.objects.exists():
            self.stdout.write(self.style.SUCCESS('License key already exists in the database'))
            return
        
        # Generate a random license key in the format XXXXXXXX-XXXXXXXX-XXXXXXXX
        # with the following criteria: [a-f0-9-]
        license_key = self.generate_random_string(8) + '-' + self.generate_random_string(8) + '-' + self.generate_random_string(8)
        

        # Add the license key to the database
        LicenseKey.objects.create(licensekey=license_key)

        self.stdout.write(self.style.SUCCESS('Successfully generated and added a license key to the database'))
