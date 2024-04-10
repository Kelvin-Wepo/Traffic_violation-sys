from rest_framework import viewsets
from .models import CustomUser
from .serializers import CustomUserSerializer
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to the 'home' URL after successful login
            return redirect('home')  # Replace 'home' with the actual URL name for your home page
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


@login_required
def home(request):
    return render(request, 'base.html')  # Replace 'login.html' with your login template path
