from django import forms
from django.contrib.auth import get_user_model
from urllib.parse import urlparse
from api.models import Device, PolicyRuleset, PolicyRule, LicenseKey, ActivityIgnorePattern, EnrollmentSettings, EnrollmentPlugin, EnrollmentSkipTest
from django.forms import inlineformset_factory
import jmespath

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['rulesets']
        widgets = {
            'rulesets': forms.SelectMultiple(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
            }),
        }

class PolicyRulesetForm(forms.ModelForm):
    class Meta:
        model = PolicyRuleset
        fields = ['name', 'description', 'rules']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
                'placeholder': 'Enter ruleset name',
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full h-20 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
                'placeholder': 'Enter description',
            }),
            'rules': forms.SelectMultiple(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        read_only = kwargs.pop('read_only', False)
        super().__init__(*args, **kwargs)
        # Make description optional (it's optional in the UI)
        self.fields['description'].required = False
        if read_only:
            for field in self.fields.values():
                field.widget.attrs['disabled'] = 'disabled'


class PolicyRuleForm(forms.ModelForm):
    class Meta:
        model = PolicyRule
        fields = ['enabled', 'name', 'description', 'rule_query']
        widgets = {
            'enabled': forms.CheckboxInput(attrs={
                'class': 'mt-1 block border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
            }),
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
                'placeholder': 'Enter rule name',
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full h-20 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
                'placeholder': 'Enter description',
            }),
            'rule_query': forms.Textarea(attrs={
                'class': 'mt-1 block w-full h-20 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
                'placeholder': "e.g., os == 'Linux' && hardening_index > `70`",
            }),
        }
    
    def clean_rule_query(self):
        """Validate that the rule_query is a valid JMESPath expression."""
        rule_query = self.cleaned_data.get('rule_query')
        if not rule_query:
            return rule_query
        
        # Strip whitespace
        rule_query = rule_query.strip()
        
        # Validate JMESPath syntax by attempting to compile it
        try:
            jmespath.compile(rule_query)
        except jmespath.exceptions.JMESPathError as e:
            raise forms.ValidationError(
                f'Invalid JMESPath query syntax: {str(e)}. '
                'Please check your query expression. Examples: '
                'os == \'Linux\', hardening_index > `70`, '
                'vulnerable_packages_found == `0`'
            )
        except Exception as e:
            raise forms.ValidationError(
                f'Error validating JMESPath query: {str(e)}'
            )
        
        return rule_query


class LicenseKeyForm(forms.ModelForm):
    class Meta:
        model = LicenseKey
        fields = ['name', 'max_devices', 'expires_at', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
                'placeholder': 'Enter license name (e.g., "Production servers" or "web-01")',
            }),
            'max_devices': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
                'placeholder': 'Leave empty for unlimited',
                'min': 1,
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
                'type': 'datetime-local',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'mt-1 block border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make max_devices optional (null means unlimited)
        self.fields['max_devices'].required = False
        self.fields['expires_at'].required = False


class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
            'placeholder': 'name@example.com',
        })
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm bg-gray-100 text-gray-500 cursor-not-allowed',
                'readonly': True,
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
                'placeholder': 'First name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
                'placeholder': 'Last name',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].disabled = True
        self.fields['username'].help_text = 'Usernames cannot be changed.'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            return email

        User = get_user_model()
        exists = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists()
        if exists:
            raise forms.ValidationError('This email address is already being used by another account.')
        return email


class ActivityIgnorePatternForm(forms.ModelForm):
    class Meta:
        model = ActivityIgnorePattern
        fields = ['key_pattern', 'event_type', 'host_pattern', 'is_active']
        widgets = {
            'key_pattern': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
                'placeholder': 'e.g., slow_test or test_*',
            }),
            'event_type': forms.Select(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
            }),
            'host_pattern': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
                'placeholder': 'e.g., * or web-*',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'mt-1 block border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['key_pattern'].help_text = 'Key name pattern (supports wildcards: *, ?)'
        self.fields['host_pattern'].help_text = 'Hostname pattern (supports wildcards: *, ?). Use * for all hosts.'
        self.fields['event_type'].help_text = 'Event type to silence. Select "All" to silence all event types for this key.'
    
    def clean_key_pattern(self):
        key_pattern = self.cleaned_data.get('key_pattern')
        if not key_pattern or not key_pattern.strip():
            raise forms.ValidationError('Key pattern cannot be empty.')
        return key_pattern.strip()
    
    def clean_host_pattern(self):
        host_pattern = self.cleaned_data.get('host_pattern')
        if not host_pattern or not host_pattern.strip():
            raise forms.ValidationError('Host pattern cannot be empty. Use * for all hosts.')
        return host_pattern.strip()


class EnrollmentSettingsForm(forms.ModelForm):
    class Meta:
        model = EnrollmentSettings
        fields = ['ignore_ssl_errors', 'overwrite_lynis_profile', 'additional_packages']
        widgets = {
            'ignore_ssl_errors': forms.CheckboxInput(attrs={
                'class': 'mt-1 block border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
            }),
            'overwrite_lynis_profile': forms.CheckboxInput(attrs={
                'class': 'mt-1 block border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
            }),
            'additional_packages': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
                'placeholder': 'e.g., rkhunter auditd',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ignore_ssl_errors'].help_text = 'Skip downloading and trusting the server certificate. Enable this only if the servers certificate is self-signed and you don\'t want to install the certificate into the system truststore.'
        self.fields['overwrite_lynis_profile'].help_text = 'Allow the installer to replace /etc/lynis/custom.prf even if it already exists.'
        self.fields['additional_packages'].help_text = 'Space-separated list of packages to install alongside Lynis (leave empty to install only curl and lynis).'

class EnrollmentPluginForm(forms.ModelForm):
    class Meta:
        model = EnrollmentPlugin
        fields = ['url']
        widgets = {
            'url': forms.URLInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
                'placeholder': 'https://example.com/plugins/trikusec-plugin',
            }),
        }
        help_texts = {
            'url': 'Provide the HTTPS URL for the plugin file.',
        }

    def clean_url(self):
        url = self.cleaned_data.get('url')
        if not url:
            return url
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            raise forms.ValidationError('Only HTTP/HTTPS plugin URLs are supported.')
        return url.strip()


EnrollmentPluginFormSet = inlineformset_factory(
    parent_model=EnrollmentSettings,
    model=EnrollmentPlugin,
    form=EnrollmentPluginForm,
    fields=['url'],
    extra=1,
    can_delete=True,
    validate_min=False,
    validate_max=False,
)


class EnrollmentSkipTestForm(forms.ModelForm):
    class Meta:
        model = EnrollmentSkipTest
        fields = ['test_id']
        widgets = {
            'test_id': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800 uppercase tracking-wide',
                'placeholder': 'e.g., CRYP-7902',
            }),
        }

    def clean_test_id(self):
        test_id = self.cleaned_data.get('test_id', '')
        test_id = test_id.strip().upper()
        if not test_id:
            raise forms.ValidationError('Test ID cannot be empty.')
        return test_id


EnrollmentSkipTestFormSet = inlineformset_factory(
    parent_model=EnrollmentSettings,
    model=EnrollmentSkipTest,
    form=EnrollmentSkipTestForm,
    fields=['test_id'],
    extra=1,
    can_delete=True,
    validate_min=False,
    validate_max=False,
)