from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = 'Change the password of the admin user'

    def add_arguments(self, parser):
        parser.add_argument('--password', help='New password for the admin user', required=False)

    def handle(self, *args, **options):
        # Get the admin user
        admin_user = User.objects.get(username='admin')

        if not admin_user:
            self.stdout.write(self.style.ERROR('Admin user not found'))
            return
        
        # Get new password from environment variable
        new_password = os.environ.get('TRIKUSEC_ADMIN_PASSWORD')

        # Get the new password from the command line
        if options['password']:
            new_password = options['password']

        # Change the password of the admin user
        admin_user.set_password(new_password)
        admin_user.save()