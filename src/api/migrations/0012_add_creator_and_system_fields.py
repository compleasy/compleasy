# Generated migration for creator tracking and system rules

from django.db import migrations, models
import django.db.models.deletion


def create_system_user_and_migrate_data(apps, schema_editor):
    """Create system user, migrate existing data, and create system rules"""
    User = apps.get_model('auth', 'User')
    PolicyRule = apps.get_model('api', 'PolicyRule')
    PolicyRuleset = apps.get_model('api', 'PolicyRuleset')
    
    # Get or create system user
    system_user, created = User.objects.get_or_create(
        username='system',
        defaults={
            'is_active': False,
            'is_staff': False,
            'is_superuser': False,
            'email': '',
            'password': '!',  # Unusable password hash (historical models don't have set_unusable_password)
        }
    )
    if created:
        # Update password to unusable format (historical models)
        system_user.password = '!'  # Django's unusable password marker
        system_user.save()
    
    # Migrate existing rules and rulesets
    # Set created_by to first user if available, otherwise null
    first_user = User.objects.filter(is_active=True).first()
    default_creator = first_user if first_user else None
    
    # Update existing rules
    for rule in PolicyRule.objects.all():
        if rule.created_by is None:
            rule.created_by = default_creator
        if rule.is_system is None:
            rule.is_system = False
        rule.save()
    
    # Update existing rulesets
    for ruleset in PolicyRuleset.objects.all():
        if ruleset.created_by is None:
            ruleset.created_by = default_creator
        if ruleset.is_system is None:
            ruleset.is_system = False
        ruleset.save()
    
    # Create system rules (only if they don't exist)
    system_rules = [
        {
            'name': 'High Hardening Index',
            'rule_query': 'hardening_index > `70`',
            'description': 'System requires a hardening index greater than 70',
            'enabled': True,
            'alert': False,
        },
        {
            'name': 'Linux Operating System',
            'rule_query': 'os == \'Linux\'',
            'description': 'System requires Linux operating system',
            'enabled': True,
            'alert': False,
        },
        {
            'name': 'No Vulnerable Packages',
            'rule_query': 'vulnerable_packages_found == `0`',
            'description': 'System should have no vulnerable packages detected',
            'enabled': True,
            'alert': True,
        },
        {
            'name': 'Recent Audit',
            'rule_query': 'days_since_audit < `7`',
            'description': 'System should have been audited within the last 7 days',
            'enabled': True,
            'alert': False,
        },
    ]
    
    created_rules = []
    for rule_data in system_rules:
        rule, created = PolicyRule.objects.get_or_create(
            name=rule_data['name'],
            defaults={
                'rule_query': rule_data['rule_query'],
                'description': rule_data['description'],
                'enabled': rule_data['enabled'],
                'alert': rule_data['alert'],
                'created_by': system_user,
                'is_system': True,
            }
        )
        # If rule already exists but is not a system rule, update it to be system
        if not created and not rule.is_system:
            rule.created_by = system_user
            rule.is_system = True
            rule.save()
        created_rules.append(rule)
    
    # Create default ruleset "Default baseline" with High Hardening Index, No Vulnerable Packages, and Recent Audit
    baseline_ruleset, _ = PolicyRuleset.objects.get_or_create(
        name='Default baseline',
        defaults={
            'description': 'Default baseline ruleset with essential security checks',
            'created_by': system_user,
            'is_system': True,
        }
    )
    
    # Find the three rules for the baseline ruleset
    baseline_rule_names = ['High Hardening Index', 'No Vulnerable Packages', 'Recent Audit']
    baseline_rules = [rule for rule in created_rules if rule.name in baseline_rule_names]
    
    # Add rules to the ruleset (only if they exist)
    if baseline_rules:
        baseline_ruleset.rules.set(baseline_rules)
        baseline_ruleset.save()


def reverse_migration(apps, schema_editor):
    """Reverse migration - remove system user and reset fields"""
    User = apps.get_model('auth', 'User')
    PolicyRule = apps.get_model('api', 'PolicyRule')
    PolicyRuleset = apps.get_model('api', 'PolicyRuleset')
    
    # Delete system rulesets
    PolicyRuleset.objects.filter(is_system=True).delete()
    
    # Delete system rules
    PolicyRule.objects.filter(is_system=True).delete()
    
    # Reset created_by and is_system for remaining records
    PolicyRule.objects.all().update(created_by=None, is_system=False)
    PolicyRuleset.objects.all().update(created_by=None, is_system=False)
    
    # Delete system user
    User.objects.filter(username='system').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_alter_licensekey_name'),
    ]

    operations = [
        # Add created_by and is_system to PolicyRule
        migrations.AddField(
            model_name='policyrule',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='created_rules',
                to='auth.user'
            ),
        ),
        migrations.AddField(
            model_name='policyrule',
            name='is_system',
            field=models.BooleanField(default=False),
        ),
        # Add created_by and is_system to PolicyRuleset
        migrations.AddField(
            model_name='policyruleset',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='created_rulesets',
                to='auth.user'
            ),
        ),
        migrations.AddField(
            model_name='policyruleset',
            name='is_system',
            field=models.BooleanField(default=False),
        ),
        # Data migration: create system user, migrate data, create system rules
        migrations.RunPython(create_system_user_and_migrate_data, reverse_migration),
    ]

