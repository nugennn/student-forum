from django import forms
from .models import Community


class CommunityForm(forms.ModelForm):
    """Form for creating and editing communities"""
    
    class Meta:
        model = Community
        fields = ['name', 'description', 'icon', 'banner', 'is_private']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Community name',
                'maxlength': '200',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Community description and guidelines',
                'rows': 6,
            }),
            'icon': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'banner': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'is_private': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'name': 'Community Name',
            'description': 'Description & Guidelines',
            'icon': 'Community Icon',
            'banner': 'Community Banner',
            'is_private': 'Private Community',
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 3:
                raise forms.ValidationError('Community name must be at least 3 characters long')
        return name
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description) < 10:
            raise forms.ValidationError('Description must be at least 10 characters long')
        return description
