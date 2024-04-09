# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLES = (
        ('user', 'User'),
        ('administrator', 'Administrator'),
        ('moderator', 'Moderator'),
    )
    
    role = models.CharField(max_length=20, choices=ROLES, default='user')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    license_plate_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.username

