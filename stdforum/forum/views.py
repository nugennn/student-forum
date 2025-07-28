# your_app/views.py
from django.shortcuts import render
from .models import Profile

def home(request):
    return render(request, 'home.html', {})


def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)
    else:
        # Handle anonymous user (e.g., show a message, or return all profiles)
        profiles = Profile.objects.all()

    return render(request, 'profile_list.html', {"profiles": profiles})
