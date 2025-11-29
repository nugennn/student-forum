from django import forms
from .models import CampusUpdate


class CampusUpdateForm(forms.ModelForm):
    """Form for creating and editing campus updates"""
    
    class Meta:
        model = CampusUpdate
        fields = ['title', 'content', 'category', 'priority', 'image', 'is_published', 'expiry_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter notice title',
                'required': True,
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter detailed notice content',
                'rows': 8,
                'required': True,
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'expiry_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
        }
        labels = {
            'title': 'Notice Title',
            'content': 'Notice Content',
            'category': 'Category',
            'priority': 'Priority Level',
            'image': 'Upload Image (Optional)',
            'is_published': 'Publish this notice',
            'expiry_date': 'Expiry Date (Optional)',
        }
