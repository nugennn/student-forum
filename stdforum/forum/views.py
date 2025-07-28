# your_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Post
from django.contrib import messages
from .forms import PostForm
from django import forms

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Post
from .forms import PostForm

def home(request):
    if request.user.is_authenticated:
        form = PostForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                post = form.save(commit=False)
                post.user = request.user
                post.save()
                messages.success(request, "Your post has been published!")
                return redirect('home')
        posts = Post.objects.all().order_by("-created_at")
        return render(request, 'home.html', {'posts': posts, 'form': form})
    else:
        posts = Post.objects.all().order_by("-created_at")
        return render(request, 'home.html', {'posts': posts})




def profile_list(request):
	if request.user.is_authenticated:
		profiles = Profile.objects.exclude(user=request.user)
		return render(request, 'profile_list.html', {"profiles":profiles})
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')

def profile(request, pk):
    if request.user.is_authenticated:
        profile = get_object_or_404(Profile, user_id=pk)

        if request.method == "POST":
            current_user_profile = request.user.profile
            action = request.POST.get('follow')

            if action == "unfollow":
                current_user_profile.follows.remove(profile)
            elif action == "follow":
                current_user_profile.follows.add(profile)

            current_user_profile.save()

        # Get all posts by the profile's user
        posts = Post.objects.filter(user=profile.user).order_by('-created_at')

        return render(request, 'profile.html', {
            "profile": profile,
            "posts": posts,
        })
    else:
        messages.success(request, "You must be logged in to view this page.")
        return redirect('home')

          

        
            
		



	