from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate,update_session_auth_hash
from . forms import SignUpForm, ForcePasswordChangeForm, EmailAuthenticationForm, CustomPasswordResetForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from profile.models import Profile
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

def signup_view(request):
    """Admin-only view for creating new student accounts"""
    # Restrict to admin users only
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "Only administrators can create new accounts.")
        return redirect('profile:home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            getFormEmail = form.cleaned_data['email']
            user.email = getFormEmail
            user.save()
            
            # Determine user type and verification based on email domain
            if getFormEmail.endswith('@khwopa.edu.np'):
                user.profile.user_type = 'Teacher'
                user.profile.is_verified = True  # Auto-verify teachers
            else:
                user.profile.user_type = 'Student'
                user.profile.is_verified = False
            
            # Set password_change_required to True for new accounts
            user.profile.password_change_required = True
            user.profile.email = getFormEmail
            user.profile.save()
            
            user_type_label = "Teacher" if getFormEmail.endswith('@khwopa.edu.np') else "Student"
            messages.success(request, f"Account created for {user.username} ({user_type_label}). Must change password on first login.")
            return redirect('profile:home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_request(request):
    """Email-based login view"""
    if request.method == 'POST':
        form = EmailAuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # Email is stored in username field
            password = form.cleaned_data.get('password')
            
            # Find user by email
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                messages.error(request, "Invalid email or password.")
                return render(request=request,
                            template_name="registration/login.html",
                            context={"form": form})
            
            if user is not None:
                # Verify email ends with @khec.edu.np or @khwopa.edu.np
                if not (user.email.endswith('@khec.edu.np') or user.email.endswith('@khwopa.edu.np')):
                    messages.error(request, "Only users with institutional email addresses can login.")
                    return render(request=request,
                                template_name="registration/login.html",
                                context={"form": form})
                
                login(request, user)
                request.user.profile.logout_on_all_devices = False
                request.user.profile.save()
                
                # Check if user needs to change password on first login
                if request.user.profile.password_change_required:
                    messages.info(request, "You must change your temporary password before continuing.")
                    return redirect('users:force_password_change')
                
                messages.info(request, f"You are now logged in.")
                return redirect('/')
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = EmailAuthenticationForm()
    return render(request=request,
                    template_name="registration/login.html",
                    context={"form": form})

def logout_view(request):
    logout(request)
    return redirect('profile:home')

@login_required(login_url='users:login_request')
def force_password_change(request):
    """View to force password change on first login"""
    # Check if password change is required
    if not request.user.profile.password_change_required:
        return redirect('profile:setup_profile_first_time')
    
    if request.method == 'POST':
        form = ForcePasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Mark that password change is no longer required
            user.profile.password_change_required = False
            user.profile.save()
            # Keep user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully. Now let's complete your profile.")
            return redirect('profile:setup_profile_first_time')
    else:
        form = ForcePasswordChangeForm(request.user)
    
    return render(request, 'registration/force_password_change.html', {'form': form})

# Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view with institutional email validation"""
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.txt'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')
    
    def form_valid(self, form):
        """Override to add custom success message"""
        messages.success(self.request, 'Password reset email has been sent to your email address.')
        return super().form_valid(form)

class CustomPasswordResetDoneView(PasswordResetDoneView):
    """View shown after password reset email is sent"""
    template_name = 'registration/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """View for confirming password reset with token"""
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')
    
    def form_valid(self, form):
        """Override to add custom success message"""
        messages.success(self.request, 'Your password has been reset successfully.')
        return super().form_valid(form)

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """View shown after password reset is complete"""
    template_name = 'registration/password_reset_complete.html'

