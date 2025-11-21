from django.db import migrations


def forwards(apps, schema_editor):
    EnrollmentSettings = apps.get_model('api', 'EnrollmentSettings')
    EnrollmentSkipTest = apps.get_model('api', 'EnrollmentSkipTest')

    for settings in EnrollmentSettings.objects.all():
        raw_value = (settings.skip_tests or '').strip()
        if not raw_value:
            continue
        entries = []
        for test_id in raw_value.split(','):
            test_id = test_id.strip()
            if not test_id:
                continue
            entries.append(EnrollmentSkipTest(settings=settings, test_id=test_id))
        EnrollmentSkipTest.objects.bulk_create(entries, ignore_conflicts=True)


def backwards(apps, schema_editor):
    EnrollmentSettings = apps.get_model('api', 'EnrollmentSettings')

    for settings in EnrollmentSettings.objects.all():
        skip_tests_entries = settings.skip_tests_entries.order_by('id').values_list('test_id', flat=True)
        settings.skip_tests = ','.join(skip_tests_entries)
        settings.save(update_fields=['skip_tests'])


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_enrollmentskiptest'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]

