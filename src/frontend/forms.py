from django import forms
from api.models import PolicyRuleset

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
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
                'placeholder': 'Enter description',
            }),
            'rules': forms.SelectMultiple(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-gray-800',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        read_only = kwargs.pop('read_only', False)
        super().__init__(*args, **kwargs)
        if read_only:
            for field in self.fields.values():
                field.widget.attrs['disabled'] = 'disabled'