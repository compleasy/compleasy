from django.db import migrations


def add_default_plugin(apps, schema_editor):
    """Add the default TrikuSec plugin URL to enrollment settings."""
    EnrollmentSettings = apps.get_model('api', 'EnrollmentSettings')
    EnrollmentPlugin = apps.get_model('api', 'EnrollmentPlugin')
    
    # Get or create the settings instance (following the same pattern as get_settings)
    settings_instance = EnrollmentSettings.objects.first()
    if settings_instance is None:
        settings_instance = EnrollmentSettings.objects.create()
    
    # Default plugin URL
    default_plugin_url = 'https://raw.githubusercontent.com/TrikuSec/trikusec/refs/heads/main/trikusec-lynis-plugin/plugin_trikusec_phase1'
    
    # Check if the plugin already exists to avoid duplicates
    if not EnrollmentPlugin.objects.filter(settings=settings_instance, url=default_plugin_url).exists():
        EnrollmentPlugin.objects.create(
            settings=settings_instance,
            url=default_plugin_url
        )


def remove_default_plugin(apps, schema_editor):
    """Remove the default TrikuSec plugin URL from enrollment settings."""
    EnrollmentSettings = apps.get_model('api', 'EnrollmentSettings')
    EnrollmentPlugin = apps.get_model('api', 'EnrollmentPlugin')
    
    settings_instance = EnrollmentSettings.objects.first()
    if settings_instance:
        default_plugin_url = 'https://raw.githubusercontent.com/TrikuSec/trikusec/refs/heads/main/trikusec-lynis-plugin/plugin_trikusec_phase1'
        EnrollmentPlugin.objects.filter(
            settings=settings_instance,
            url=default_plugin_url
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_migrate_additional_packages_to_entries'),
    ]

    operations = [
        migrations.RunPython(add_default_plugin, remove_default_plugin),
    ]

