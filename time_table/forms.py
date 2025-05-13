from django.forms import ModelForm

from django import forms

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['r_number', 'seating_capacity']
        labels = {
            "r_number": "Room ID",
            "seating_capacity": "Capacity"
        }

class MeetingTimeForm(ModelForm):
    class Meta:
        model = MeetingTime
        fields = ['time', 'day']
        labels = {
            "time": "Time",
            "day": "Day of the Week"
        }
        widgets = {
            'time': forms.Select(),
            'day': forms.Select(),
        }
