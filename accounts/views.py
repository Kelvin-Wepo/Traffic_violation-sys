from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login as auth_login
from django.core.mail import send_mail
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from rest_framework.response import Response
from .forms import CustomUserCreationForm, EmailChangeForm
from .models import UserProfile
# from utils.utils import generate_random_code
from django.utils import timezone
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

            return redirect('accounts:verify')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

def create_user_profile(user):
    """
    Create a user profile for the newly registered user.
    """
    code = generate_random_code()
    verification_code_expiry = timezone.now() + datetime.timedelta(minutes=30)
    UserProfile.objects.create(
        user=user, 
        email_verified_code=code, 
        verification_code_expiry=verification_code_expiry
    )
    send_verification_email(user.email, code)

def send_verification_email(email, code):
    """
    Send an email containing the verification code.
    """
    subject = "Verify Your Account"
    message = f"Your verification code is: {code}"
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

def verify(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        if not code:
            messages.error(request, 'Please enter a verification code.')
            return render(request, 'accounts/verify.html')

        try:
            profile = UserProfile.objects.get(email_verified_code=code)
            if profile.is_verification_code_expired():
                messages.error(request, 'The verification code has expired.')
                return render(request, 'accounts/verify.html')

            profile.email_verified = True
            profile.email_verified_code = ''
            profile.save()

            user = profile.user
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            messages.success(request, 'Your account has been successfully verified.')
            return redirect('home')
        except UserProfile.DoesNotExist:
            messages.error(request, 'Invalid verification code.')
            return render(request, 'accounts/verify.html')
    else:
        return render(request, 'accounts/verify.html')

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
