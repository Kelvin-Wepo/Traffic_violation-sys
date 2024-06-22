from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.response import Response
from .forms import CustomUserCreationForm, EmailChangeForm
from .models import UserProfile
import datetime

def login(request, *args, **kwargs):
    """
    Login view. Redirects to the home page if the user is already authenticated.
    """
    if request.user.is_authenticated:
        return redirect('home')
    return LoginView.as_view(template_name='accounts/login.html')(request, *args, **kwargs)

def validate_username_email(request):
    """
    AJAX request to validate whether a username and email already exist.
    """
    username = request.GET.get('username', None)
    email = request.GET.get('email', None)
    data = {
        'username_error': 'This username is already in use' if User.objects.filter(username=username).exists() else None,
        'email_error': 'This email address is already in use' if User.objects.filter(email=email).exists() else None,
    }
    return JsonResponse(data)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            create_user_profile(user)

            # Log in the user using authenticate and login functions
            user = authenticate(username=user.username, password=form.cleaned_data['password1'])
            if user is not None:
                auth_login(request, user)

            return redirect('home')  # Redirect to home after successful registration
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

def create_user_profile(user):
    """
    Create a user profile for the newly registered user.
    """
    UserProfile.objects.create(
        user=user, 
    )

@login_required
def account_view(request):
    """
    Display the user's account information.
    """
    return render(request, 'accounts/account.html', {'user': request.user})

@login_required
def email_change(request):
    if request.method == 'POST':
        form = EmailChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your email has been updated.')
            return redirect('profile')
    else:
        form = EmailChangeForm(instance=request.user)
    return render(request, 'account/email_change_form.html', {'form': form})

@login_required
def custom_password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been updated successfully!')
            return redirect('accounts:password_change_done')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/password_change_form.html', {'form': form})

@login_required
def password_change_done(request):
    # Display a message indicating that the password change was successful.
    return render(request, 'accounts/password_change_done.html')

@login_required
def social_account_connections(request):
    # The implementation here will depend on how you handle social account connections
    # If you're using django-allauth, it already provides views to handle social account connections
    # Below is a hypothetical implementation
    return render(request, 'accounts/social_connections.html')

@login_required
def account_delete(request):
    if request.method == 'POST':
        # Confirm that the user really wants to delete their account
        # You can add a form here to allow the user to confirm the deletion operation
        request.user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('home')
    return render(request, 'accounts/account_delete_confirm.html')
