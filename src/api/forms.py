# core/forms.py

from django import forms

class ReportUploadForm(forms.Form):
    data = forms.CharField(widget=forms.Textarea)
    licensekey = forms.CharField(max_length=255)
    hostid = forms.CharField(max_length=255)
    hostid2 = forms.CharField(max_length=255)