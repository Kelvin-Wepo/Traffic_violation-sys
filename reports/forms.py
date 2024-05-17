from django import forms
from django.conf import settings
from multiupload.fields import MultiFileField
from datetime import datetime
import pytz
from .models import TrafficViolation

    
class ReportForm(forms.Form):
    VIOLATIONS = TrafficViolation.VIOLATIONS
    STATUS = TrafficViolation.STATUS

    HOUR_CHOICES = [(i, f'{i:02}') for i in range(24)]
    MINUTE_CHOICES = [(i, f'{i:02}') for i in range(60)]

    tz = pytz.timezone('Africa/Nairobi')  # Changed timezone to Nairobi, Africa
    current_time = datetime.now(tz)

    license_plate = forms.CharField(label="License Plate", max_length=10)  
    date = forms.DateField(label="Date", widget=forms.SelectDateWidget, initial=current_time.date(), required=False)  
    hour = forms.ChoiceField(choices=HOUR_CHOICES, initial=current_time.hour, label="Hour") 
    minute = forms.ChoiceField(choices=MINUTE_CHOICES, initial=current_time.minute, label="Minute") 
    violation = forms.ChoiceField(label="Violation", choices=VIOLATIONS, initial='Other')  
    status = forms.ChoiceField(label="Report Result", choices=STATUS, initial='Other')  
    location = forms.CharField(label="Location", max_length=100)  
    officer = forms.CharField(label="Officer", max_length=100, required=False)  
    media = MultiFileField(label="Media", min_num=1, max_num=5, max_file_size=settings.FILE_UPLOAD_MAX_MEMORY_SIZE, required=False)  # Changed label to English

    def clean(self):
        cleaned_data = super().clean()
        hour = cleaned_data.get("hour")
        minute = cleaned_data.get("minute")

        # Validate hour and minute values
        if hour is None or minute is None:
            raise forms.ValidationError("You must select a valid hour and minute.")
        
        # Combine hour and minute into a time string
        time_string = f"{hour}:{minute}"
        cleaned_data['time'] = datetime.strptime(time_string, "%H:%M").time()
        
        return cleaned_data
