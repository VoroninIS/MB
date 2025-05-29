from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth import logout
from django.core.files import File
from .forms import CustomUserCreationForm
from django.contrib import messages
from .forms import ProfileUpdateForm
from django.conf import settings
import os


def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            default_avatar_path = os.path.join(
                settings.BASE_DIR,
                "main",
                "static",
                "main",
                "img",
                "default_avatar.png",
            )
            with open(default_avatar_path, "rb") as f:
                user.avatar.save("default_avatar.png", File(f), save=False)
            user = form.save()
            login(request, user)
            return redirect("/")
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, "registration/profile.html", {"form": form})


def custom_logout(request):
    logout(request)
    return redirect("/")
