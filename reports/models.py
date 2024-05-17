from django.db import models
from django.contrib.auth.models import User
import uuid
import os
from django.utils.deconstruct import deconstructible


class TrafficViolation(models.Model):
    VIOLATIONS = [
        ('Red line parking', 'Red line parking'),
        ('Yellow line parking', 'Yellow line parking'),
        ('Driving on pedestrian path', 'Driving on pedestrian path'),
        ('Failure to yield to pedestrians', 'Failure to yield to pedestrians'),
        ('Changing lanes without signaling', 'Changing lanes without signaling'),
        ('Parking on pedestrian path', 'Parking on pedestrian path'),
        ('Parking on sidewalk', 'Parking on sidewalk'),
        ('Running a red light', 'Running a red light'),
        ('Tailgating', 'Tailgating'),
        ('Failure to yield to oncoming traffic', 'Failure to yield to oncoming traffic'),
        ('Not following lane markings', 'Not following lane markings'),
        ('Other', 'Other'),
    ]
    STATUS = [
        ('Approved', 'Approved'),
        ('Not approved', 'Not approved'),
        ('Other', 'Other'),
    ]
    license_plate = models.CharField(max_length=10)
    date = models.DateField()
    time = models.TimeField()
    violation = models.CharField(max_length=100, choices=VIOLATIONS)
    status = models.CharField(max_length=50, choices=STATUS)
    address = models.CharField(max_length=255, blank=True, null=True)  # Address field
    latitude = models.FloatField()  # Latitude
    longitude = models.FloatField()  # Longitude
    user_input_type = models.CharField(max_length=100, blank=True, null=True)  # User input type
    officer = models.CharField(max_length=255, blank=True, default='')
    traffic_violation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, blank=True, null=True)

@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # Set the new file name as UUID
        filename = '{}.{}'.format(uuid.uuid4(), ext)
        # Return the file name including the new path
        return os.path.join('reports/media', self.sub_path, filename)

# Use PathAndRename in the model to handle 'upload_to'
class MediaFile(models.Model):
    traffic_violation = models.ForeignKey(
        TrafficViolation, on_delete=models.CASCADE, null=True, blank=True
    )
    file = models.FileField(upload_to=PathAndRename(''))
