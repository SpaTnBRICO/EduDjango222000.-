from django import forms
#from django.contrib.auth.forms import UserCreationForm
from .models import CustomerUser, UserProfile


class UserUpdateForm(forms.ModelForm):
	email = forms.EmailField()
	class Meta:
		model = CustomerUser
		fields = ['username', 'email']

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'profile_picture']