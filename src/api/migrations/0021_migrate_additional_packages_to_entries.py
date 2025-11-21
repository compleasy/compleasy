from django.db import migrations


def forwards(apps, schema_editor):
    EnrollmentSettings = apps.get_model('api', 'EnrollmentSettings')
    EnrollmentPackage = apps.get_model('api', 'EnrollmentPackage')

    for settings in EnrollmentSettings.objects.all():
        raw_value = (settings.additional_packages or '').strip()
        if not raw_value:
            continue
        packages = []
        for name in raw_value.split():
            cleaned = name.strip()
            if not cleaned:
                continue
            packages.append(EnrollmentPackage(settings=settings, name=cleaned))
        EnrollmentPackage.objects.bulk_create(packages, ignore_conflicts=True)


def backwards(apps, schema_editor):
    EnrollmentSettings = apps.get_model('api', 'EnrollmentSettings')

    for settings in EnrollmentSettings.objects.all():
        package_entries = settings.additional_packages_entries.order_by('id').values_list('name', flat=True)
        joined = ' '.join(package_entries)
        settings.additional_packages = joined
        settings.save(update_fields=['additional_packages'])


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_enrollmentpackage'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]

