import pyotp
from datetime import datetime, timedelta
import random
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from .models import CustomerUser, UserProfile
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

#WhatsApp Stuff
import os
#from twilio.rest import Client
from django.conf import settings
import time

#Email Stuff
from django.core.mail import send_mail






def send_otp(request):
    # Generate secret key if not in session
    if 'otp_secret_key' not in request.session:
        secret_key = pyotp.random_base32()
        request.session['otp_secret_key'] = secret_key

    # Create OTP with 10-minute validity
    totp = pyotp.TOTP(request.session['otp_secret_key'], interval=600)
    otp = totp.now()

    # Set OTP expiry
    valid_until = datetime.now() + timedelta(seconds=600)
    request.session['otp_valid_date'] = valid_until.isoformat()

    print(f"Generated OTP: {otp}, Valid until: {valid_until.isoformat()}")

    username = request.session.get('username')
    
    if not username:
        messages.error(request, "Username not found in session.")
        return None

    try:
        # Retrieve user and profile
        user_obj = get_object_or_404(CustomerUser, username=username)

        # Prepare the email content
        subject = "Your OTP for TechSols"
        message = (
            f"Hello {user_obj.username},\n\n"
            f"Your OTP is: {otp}. It expires at {valid_until.strftime('%H:%M:%S')}.\n\n"
            "Thank you,\nTechSols"
        )
        from_email = settings.DEFAULT_FROM_EMAIL  # This is defined in settings.py
        recipient_list = [user_obj.email]  # The user's email address from the profile

        # Send OTP via email
        send_mail(subject, message, from_email, recipient_list)

        # Success message for the user
        messages.success(request, "OTP sent successfully via email!")

    except Exception as e:
        # Error message for the user
        messages.error(request, "Failed to send OTP. Please check the logs for details.")
        print(f"Error sending OTP via email: {e}")

    return otp





def send_otp_activate_account(request):
    """
    Generates a Time-Based OTP (TOTP) and sends it to the user's email for account activation.
    """
    # Check if the OTP secret key exists in the session; if not, generate one
    if 'otp_secret_key' not in request.session:
        secret_key = pyotp.random_base32()  # Generate a random base32 secret key for the OTP
        request.session['otp_secret_key'] = secret_key  # Save the secret key to the session

    # Create TOTP object using the secret key from the session
    totp = pyotp.TOTP(request.session['otp_secret_key'], interval=600)  # OTP valid for 600 seconds
    
    # Generate the OTP using the TOTP object
    otp = totp.now()  # Get the current OTP based on the time and secret key

    # Set expiration date for OTP (valid for 1 minute)
    valid_until = datetime.now() + timedelta(minutes=10)  # Set OTP expiry time (10 minutes)
    request.session['otp_valid_date'] = valid_until.isoformat()  # Store expiry in ISO format in session

    # Debugging: Print the OTP and expiration date to the console for testing purposes
    print(f"Generated OTP: {otp}, Valid until: {valid_until.isoformat()}")  # Remove this in production

    username = request.session.get('username')
    
    if not username:
        messages.error(request, "Username not found in session.")
        return None

    try:
        # Retrieve user and profile
        user_obj = get_object_or_404(CustomerUser, username=username)

        # Prepare the email content
        subject = "Your OTP for TechSols"
        message = (
            f"Hello {user_obj.username},\n\n"
            f"Your OTP is: {otp}. It expires at {valid_until.strftime('%H:%M:%S')}.\n\n"
            "Thank you,\nTechSols"
        )
        from_email = settings.DEFAULT_FROM_EMAIL  # This is defined in settings.py
        recipient_list = [user_obj.email]  # The user's email address from the profile

        # Send OTP via email
        send_mail(subject, message, from_email, recipient_list)

        # Success message for the user
        messages.success(request, "OTP sent successfully via email!")

    except Exception as e:
        # Error message for the user
        messages.error(request, "Failed to send OTP. Please check the logs for details.")
        print(f"Error sending OTP via email: {e}")
    return otp



# Generate a random 6-digit OTP for other use cases (e.g., password reset)
def generate_otp():
    return str(random.randint(100000, 999999))


# Example function for sending OTP via email (currently commented out)
# def send_otp_email(otp, email):
#     subject = 'Your OTP Code'
#     message = f'Your OTP code is {otp}. Please use it to log in.'
#     from_email = settings.DEFAULT_FROM_EMAIL  # Ensure this is set in settings
#     send_mail(subject, message, from_email, [email])

#     print(f"Sent OTP email to {email}.")  # Commented out

def redirect_if_authenticated(view_func):
    """
    Redirects logged-in users to a specified page if they try to access
    pages like login, registration, etc.
    """
    def _wrapped_view(request, *args, **kwargs):
        #print(f"User is authenticated: {request.user.is_authenticated}")  # Debugging line
        if request.user.is_authenticated:
            return redirect(reverse('home'))  # Redirect to the home page or dashboard
        return view_func(request, *args, **kwargs)

    return _wrapped_view