from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.core.exceptions import ValidationError

def validate_khec_email(email):
    """Validate that email ends with khec.edu.np"""
    if not email.endswith('@khec.edu.np'):
        raise ValidationError('Email must end with @khec.edu.np')

class SignUpForm(UserCreationForm):
    """Admin-only form for creating new student accounts"""
    email = forms.EmailField(max_length=200, validators=[validate_khec_email])
    password1 = forms.CharField(widget=forms.PasswordInput())
    username = forms.CharField(help_text=False)
    
    class Meta:
        model = User
        fields = (
            'email',            
        	'username',
        )

class EmailAuthenticationForm(AuthenticationForm):
    """Custom authentication form using email instead of username"""
    username = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your institutional email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
    
    def clean_username(self):
        """Validate email format"""
        email = self.cleaned_data.get('username')
        if email and not email.endswith('@khec.edu.np'):
            raise ValidationError('Please use your institutional email address (@khec.edu.np)')
        return email

class ForcePasswordChangeForm(SetPasswordForm):
    """Form for students to change their temporary password on first login"""
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')
