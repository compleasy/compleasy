# Generated migration for diff system refactor

from django.db import migrations, models
import django.db.models.deletion


def create_default_ignore_patterns(apps, schema_editor):
    """Create default ignore patterns for all existing organizations"""
    Organization = apps.get_model('api', 'Organization')
    ActivityIgnorePattern = apps.get_model('api', 'ActivityIgnorePattern')
    
    default_patterns = [
        'report_datetime_start',
        'report_datetime_end',
        'slow_test',
        'uptime_in_seconds',
        'uptime_in_days',
        'deleted_file',
        'lynis_timer_next_trigger',
        'clamav_last_update',
        'tests_executed',
        'tests_skipped',
        'installed_packages_array',
        'vulnerable_package',
        'suggestion',
    ]
    
    # Create patterns for all organizations
    for org in Organization.objects.all():
        for pattern in default_patterns:
            ActivityIgnorePattern.objects.get_or_create(
                organization=org,
                pattern=pattern,
                defaults={'is_active': True}
            )


def reverse_migration(apps, schema_editor):
    """Reverse migration - remove all ignore patterns"""
    ActivityIgnorePattern = apps.get_model('api', 'ActivityIgnorePattern')
    ActivityIgnorePattern.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_add_creator_and_system_fields'),
    ]

    operations = [
        # Create ActivityIgnorePattern model
        migrations.CreateModel(
            name='ActivityIgnorePattern',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pattern', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.organization')),
            ],
        ),
        # Add unique constraint
        migrations.AlterUniqueTogether(
            name='activityignorepattern',
            unique_together={('organization', 'pattern')},
        ),
        # Add index
        migrations.AddIndex(
            model_name='activityignorepattern',
            index=models.Index(fields=['organization', 'is_active'], name='api_activi_organiz_idx'),
        ),
        # Convert DiffReport.diff_report from TextField to JSONField
        migrations.AlterField(
            model_name='diffreport',
            name='diff_report',
            field=models.JSONField(default=dict),
        ),
        # Populate default ignore patterns
        migrations.RunPython(create_default_ignore_patterns, reverse_migration),
    ]

