from django import forms
from .models import GlucoseEntry, UserProfile, Entry, Medicine

class GlucoseEntryForm(forms.ModelForm):
    class Meta:
        model = GlucoseEntry
        fields = ['value', 'note']
        widgets = {
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'birth_date', 'phone', 'address']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['datetime', 'glucose', 'height', 'weight']
        widgets = {
            'datetime': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'glucose': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'height': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ["name", "dose"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Название"
            }),
            "dose": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Дозировка"
            }),
        }
