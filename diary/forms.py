from django import forms
from .models import GlucoseEntry

class GlucoseEntryForm(forms.ModelForm):
    class Meta:
        model = GlucoseEntry
        fields = ['value', 'note']
        widgets = {
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
        }
