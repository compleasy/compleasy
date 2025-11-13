# core/forms.py

import re
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class ReportUploadForm(forms.Form):
    licensekey = forms.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_-]+$',
                message='License key must contain only alphanumeric characters, hyphens, and underscores'
            )
        ],
        error_messages={
            'required': 'License key is required',
            'max_length': 'License key too long'
        }
    )
    
    hostid = forms.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_-]+$',
                message='Host ID must contain only alphanumeric characters, hyphens, and underscores'
            )
        ],
        error_messages={'required': 'Host ID is required'}
    )
    
    hostid2 = forms.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_-]+$',
                message='Host ID2 must contain only alphanumeric characters, hyphens, and underscores'
            )
        ],
        error_messages={'required': 'Host ID2 is required'}
    )
    
    data = forms.CharField(
        widget=forms.Textarea,
        error_messages={'required': 'Report data is required'}
    )
    
    def clean_data(self):
        data = self.cleaned_data.get('data', '')
        
        # Reasonable size limit: 10MB
        max_size = 10 * 1024 * 1024
        if len(data.encode('utf-8')) > max_size:
            raise ValidationError('Report data too large (max 10MB)')
        
        # Basic format validation: should contain Lynis report structure
        if 'report_version_major=' not in data:
            raise ValidationError('Invalid Lynis report format')
        
        return data