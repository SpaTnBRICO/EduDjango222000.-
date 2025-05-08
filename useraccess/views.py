from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import HttpResponse, JsonResponse

import csv
import pyotp
from datetime import datetime
from django.template.loader import render_to_string  # <-- Add this import here
from .models import CustomerUser, Student, UserProfile, Course, StudentApp, Teacher, Department, Level
from loging.models import Contact
from django.core.exceptions import ObjectDoesNotExist

from .forms import UserUpdateForm, UserProfileUpdateForm
from .utils import send_otp, send_otp_activate_account, redirect_if_authenticated
import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

#Pagination stuff
from django.core.paginator import Paginator

#WhatsApp
import os
#from twilio.rest import Client
from django.conf import settings

#Email Sending stuff
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site

from django.contrib.auth.hashers import make_password
from django.db import transaction




# Get the User model
CustomerUser = get_user_model()


def custom_page_not_found_view(request, exception):
    if request.user.is_authenticated:
        logout(request)
    return render(request, "custom_404.html", status=404)

# User Registration View
#@redirect_if_authenticated
def user_register(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if not request.user.is_admin:
        return redirect('/')

    if request.method == "POST":
        # Collect data from the registration form
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        role = request.POST.get('role')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        password = pass1
        phone_number = request.POST.get('phone_number')  # Collect phone number

        # Validation checks (same as before)
        if CustomerUser.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect('/auth_access/signup/')

        if CustomerUser.objects.filter(email=email).exists():
            messages.warning(request, "Email is already registered.")
            return redirect('/auth_access/signup/')

        if CustomerUser.objects.filter(userprofile__phone_number=phone_number).exists():
            messages.warning(request, "Phone number is already registered.")
            return redirect('/auth_access/signup/')

        if len(pass1) < 8:
            messages.info(request, "Password must be at least 8 characters.")
            return redirect('/auth_access/signup/')
        
        if pass1 != pass2:
            messages.info(request, "Passwords do not match.")
            return redirect('/auth_access/signup/')

        if not re.search(r"[A-Z]", pass1):
            messages.info(request, "Password must contain an uppercase letter.")
            return redirect('/auth_access/signup/')
        
        if not re.search(r"[a-z]", pass1):
            messages.info(request, "Password must contain a lowercase letter.")
            return redirect('/auth_access/signup/')

        if not re.search(r"[0-9]", pass1):
            messages.info(request, "Password must contain a number.")
            return redirect('/auth_access/signup/')

        if not re.search(r"[^a-zA-Z0-9]", pass1):
            messages.info(request, "Password must have a special character.")
            return redirect('/auth_access/signup/')

        try:
            validate_email(email)
        except ValidationError:
            messages.info(request, "Invalid email format.")
            return redirect('/auth_access/signup/')

        if role not in ['admin', 'employee', 'customer']:
            messages.error(request, "Invalid role selected.")
            return redirect('/auth_access/signup/')

        # Create user
        user = CustomerUser.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)

        # Set user roles
        if role == 'admin':
            user.is_admin = True
        elif role == 'employee':
            user.is_employee = True
        else:
            user.is_customer = True
        
        user.is_active = False  # Inactive until OTP verification
        user.save()

        # Create UserProfile with phone number
        # **Update UserProfile (Signal ensures it's already created)**:
        user_profile = user.userprofile  # Access the profile created by the signal
        user_profile.phone_number = phone_number
        user_profile.save()  # Save updated phone number
        # Store username in session for OTP
        request.session['username'] = username

        # Send OTP
        send_otp_activate_account(request)

        messages.success(request, "Account created. OTP sent for activation.")
        return redirect('/auth_access/otp_view_activate_account/')
    
    return render(request, "register.html", {
        'user_profile':user_profile,
    })



#@redirect_if_authenticated
def otp_view_activate_account(request):
    if not request.user.is_admin:
        return redirect('/')
    """
    Handles OTP verification for user account activation. If OTP expires, the account is deleted.
    """
    if request.method == "POST":
        # Get the OTP entered by the user and the username from the session
        otp = request.POST.get('otp')  
        username = request.session.get('username')

        # Retrieve the OTP secret key and expiration date from the session
        otp_secret_key = request.session.get('otp_secret_key')
        otp_valid_until = request.session.get('otp_valid_date')

        if otp_secret_key and otp_valid_until:
            # Convert expiration date from ISO format to datetime
            valid_until = datetime.fromisoformat(otp_valid_until)
            
            # Check if the OTP has expired
            if valid_until > datetime.now():  # OTP is still valid
                # Create TOTP object and verify the OTP entered by the user
                totp = pyotp.TOTP(otp_secret_key, interval=600)
                if totp.verify(otp):  # Verify the OTP
                    # OTP is valid, activate the user's account
                    user = get_object_or_404(CustomerUser, username=username)
                    user.is_active = True  # Activate the user's account
                    user.save()  # Save changes to the database

                    # Clear OTP-related session data after successful activation
                    del request.session['otp_secret_key']
                    del request.session['otp_valid_date']

                    # Show success message and redirect to signup page
                    messages.success(request, "Account activated successfully. You can login now.")
                    return redirect('/auth_access/signup/')
                else:
                    # Invalid OTP entered by the user
                    messages.error(request, "Invalid OTP! Try again.")
                    return redirect('/auth_access/otp_view_activate_account/')
            else:
                # OTP expired, delete the user account from the database
                user = get_object_or_404(CustomerUser, username=username)
                user.delete()  # Delete the user from the database

                # Clear OTP-related session data
                del request.session['otp_secret_key']
                del request.session['otp_valid_date']

                # Show warning message and redirect to signup page
                messages.warning(request, "OTP has expired. Your account has been deleted.")
                return redirect('/auth_access/signup/')
        else:
            # If OTP secret or expiration time is not found in the session, something went wrong
            messages.error(request, "Something went wrong.")
            return redirect('/')

    # Render the OTP activation page
    return render(request, "otp_view_activate_account.html", {})
# User Login View
@redirect_if_authenticated
def user_login(request):
    """
    Handles the user login process, including OTP generation.
    """
    if request.method == "POST":
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        
        # Authenticate user
        user = authenticate(email=email, password=pass1)

        if user is not None and not user.is_active:
            messages.warning(request, "Your account is deactivated. Contact the admin to activate.")
            return redirect('/auth_access/signin/')

        elif user is not None and user.is_active:
            # Store username in session before calling send_otp
            request.session['email'] = email
            
            # Generate OTP for the user
            send_otp(request)
            
            return redirect('/auth_access/otp/')

        else:
            messages.warning(request, "Invalid credentials! Try again or Account is not activated.")
            return redirect('/auth_access/signin/')

    return render(request, "login.html", {})



# OTP Verification View
#@redirect_if_authenticated
def otp_view(request):
    """
    Handles OTP verification for user login.
    """
    if request.method == "POST":
        otp = request.POST.get('otp')
        email = request.session.get('email')

        # Retrieve OTP secret key and expiration date from the session
        otp_secret_key = request.session.get('otp_secret_key')
        otp_valid_until = request.session.get('otp_valid_date')

        if otp_secret_key and otp_valid_until:
            valid_until = datetime.fromisoformat(otp_valid_until)
            
            if valid_until > datetime.now():
                totp = pyotp.TOTP(otp_secret_key, interval=600)
                if totp.verify(otp):  # Verify OTP
                    user = get_object_or_404(CustomerUser, email=email)

                    user.backend = 'useraccess.auth_backends.EmailAuthBackend'
                    login(request, user)  # Log in the user

                    # Clear OTP data from session after successful login
                    del request.session['otp_secret_key']
                    del request.session['otp_valid_date']

                    # Redirect based on user role
                    if user.is_admin:
                        return redirect('/auth_access/admin_dashboard/')
                    elif user.is_employee:
                        return redirect('/auth_access/staff_dashboard/')
                    elif user.is_customer:
                        return redirect('/auth_access/customer_dashboard/')
                    elif user.is_student:
                        return redirect('/auth_access/student_dashboard/')
                    elif user.is_teacher:
                        return redirect('/auth_access/teacher_dashboard/')
                    else:
                        messages.warning(request, "Your role is not defined.")
                        return redirect('/auth_access/signin/')
                else:
                    messages.error(request, "Invalid OTP! Try again.")
                    return redirect('/auth_access/otp/')
            else:
                messages.warning(request, "OTP has expired. The code is only valid for 60 seconds.")
                return redirect('/auth_access/signin/')
        else:
            messages.error(request, "Something went wrong. Try logging in again.")
            return redirect('/auth_access/signin/')

    return render(request, "otp.html", {})



# Admin Dashboard - Accessible only by admin users
@login_required
def admin_dashboard(request):
    """
    Displays the admin dashboard. Accessible only by admin users.
    If the user is not an admin, they will be redirected to the home page.
    """
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('home')  # Redirect to the home page
    else:
        total_students = StudentApp.objects.count()
        messages = Contact.objects.all().order_by('-create_at')
        inst = Teacher.objects.count()
        courses = Course.objects.count()
        total_users = CustomerUser.objects.count()
        departments = Department.objects.count()
    return render(request, "admins.html", {
        'total_students':total_students,
        'inst':inst,
        'courses':courses,
        'total_users':total_users,
        'departments':departments,
        'messages':messages,
        })

# Staff Dashboard - Accessible only by staff users
@login_required
def staff_dashboard(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    """
    Displays the staff dashboard. Accessible only by staff users (employees).
    If the user is not a staff member, they will be redirected to the home page.
    """
    if not request.user.is_employee:  # Check if the user is an employee
        messages.error(request, "You do not have permission to view this page.")
        return redirect('home')  # Redirect to a safe page
    return render(request, "staff.html", {
        'user_profile':user_profile,
    })

@login_required
def baseadmin(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    unread_messages_count = Contact.objects.filter(read=False).count()
    print(f"email:{user_profile.user.email}")
    return render(request, "baseadmin.html", {
        'user_profile': user_profile,
        'unread_messages_count': unread_messages_count,
    })

# Customer Dashboard - Accessible only by customer users
@login_required
def customer_dashboard(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    """
    Displays the customer dashboard. Accessible only by customer users.
    If the user is not a customer, they will be redirected to the home page.
    """
    if not request.user.is_customer:  # Check if the user is a customer
        messages.error(request, "You do not have permission to view this page.")
        return redirect('home')  # Redirect to a safe page
    return render(request, "customer.html", {
        'user_profile':user_profile,
    })

# User Logout
@login_required
def user_logout(request):
    """
    Logs the user out and redirects them to the home page with a success message.
    """
    logout(request)
    messages.success(request, "You were logged out successfully.")
    return redirect('/')



@redirect_if_authenticated
def forgot_password(request):
    """
    Handles the forgot password functionality.
    The user enters their email to receive a password reset link.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        user = CustomerUser.objects.filter(email=email)

        if user.exists():
            user_instance = user[0]  # Assuming only one user is returned

            # Generate reset URL and token
            token_generator = PasswordResetTokenGenerator()
            uid = urlsafe_base64_encode(force_bytes(user_instance.pk))
            token = token_generator.make_token(user_instance)

            # Get the current domain (this will automatically use the domain from the request)
            domain = get_current_site(request).domain

            # Create the password reset message content
            reset_link = f"http://{domain}/reset/{uid}/{token}/"
            email_subject = '[Reset Your Password]'
            message = render_to_string('reset_user_password.html', {
                'domain': domain,
                'uid': uid,
                'token': token,
                'user': user_instance,
                'reset_link': reset_link,
            })

            # Send the email with HTML content
            send_mail(
                email_subject,
                message,  # The plain text version of the email
                settings.DEFAULT_FROM_EMAIL,  # The 'From' email address from settings
                [email],  # The recipient's email address
                fail_silently=False,  # Raise an exception if email fails
                html_message=message  # The HTML content of the email
            )

            # Inform the user
            messages.info(request, "We have sent a link to your email to reset your password.")
            return render(request, 'password_reset_done.html')

        else:
            messages.error(request, "No user found with that email.")
            return render(request, 'forgot_password.html')

    return render(request, 'forgot_password.html')  # GET method rendering the forgot password page


# Set New Password View
@redirect_if_authenticated
def set_new_password(request, uidb64, token):
    """
    Handles the process of setting a new password after the user clicks the reset link.
    """
    context = {'uidb64': uidb64, 'token': token}
    
    # Handle GET request
    if request.method == 'GET':
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomerUser.objects.get(pk=user_id)

            # Verify the token
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.warning(request, "Invalid reset link.")
                return render(request, 'forgot_password.html')
        except DjangoUnicodeDecodeError:
            messages.error(request, "The reset link is invalid or expired.")
            return redirect('signin')

        return render(request, 'password_reset_confirm.html', context)

    # Handle POST request
    if request.method == 'POST':
        new_password = request.POST.get('pass1')
        confirm_new_password = request.POST.get('pass2')

        # Validate password length
        if len(new_password) < 8:
            messages.error(request, "Password is too short. It must be at least 8 characters.")
            return render(request, 'password_reset_confirm.html', context)

        # Check if passwords match
        if new_password != confirm_new_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'password_reset_confirm.html', context)

        # Password complexity checks
        if not re.search(r"[A-Z]", new_password):  # Uppercase letter check
            messages.error(request, "Password must contain at least one uppercase letter.")
            return render(request, 'password_reset_confirm.html', context)

        if not re.search(r"[a-z]", new_password):  # Lowercase letter check
            messages.error(request, "Password must contain at least one lowercase letter.")
            return render(request, 'password_reset_confirm.html', context)

        if not re.search(r"[0-9]", new_password):  # Number check
            messages.error(request, "Password must contain at least one number.")
            return render(request, 'password_reset_confirm.html', context)

        if not re.search(r"[^a-zA-Z0-9]", new_password):  # Special character check
            messages.error(request, "Password must contain at least one special character.")
            return render(request, 'password_reset_confirm.html', context)

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = CustomerUser.objects.get(pk=user_id)
            user.set_password(new_password)  # Set the new password
            user.save()

            messages.success(request, 'Your password has been reset successfully. You can log in now.')
            return redirect('signin')  # Redirect to login after success
        except DjangoUnicodeDecodeError:
            messages.error(request, 'Something went wrong. Please try again.')
            return render(request, 'password_reset_confirm.html', context)




# Password Reset Done View
@redirect_if_authenticated
def password_reset_done(request):
    """
    Renders the password reset done page after the password reset link is clicked.
    """
    return render(request, 'password_reset_done.html')

# Profile View - Accessible only by authenticated users
@login_required
def profile(request):
    """
    Displays the user's profile page. Only accessible by logged-in users.
    Redirects to the login page if the user is not authenticated.
    """
    if not request.user.is_authenticated:
        messages.warning(request, 'Login to access this page.')
        return redirect('/auth_access/signin/')  # Redirect to login if not authenticated

    return render(request, 'profile.html')

# User Profile Update View - Accessible only by authenticated users

# View to display the user profile
@login_required
def user_profile(request):
    if not request.user.is_authenticated:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('home')
    # Ensure that 'request.user' is a student
    if request.user.is_student:
        student = request.user
        # Use first() to return a single student or None if no match is found
        stud = StudentApp.objects.filter(registration_number=student).first()

    else:
        stud = None  # If the user is not a student, set 'stud' to None

    # Fetch the user profile object
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    context = {
        'user_profile': user_profile,
        'stud': stud,
    }

    return render(request, 'user_profile.html', context)


# View to edit the user profile
@login_required
def edit_user_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)  # Get the profile of the logged-in user
    
    if request.method == 'POST':
        # Get the updated values from the form
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        nationality = request.POST.get('nationality')
        emergency_contact_name = request.POST.get('emergency_contact_name')
        emergency_contact_phone = request.POST.get('emergency_contact_phone')
        blood_group = request.POST.get('blood_group')
        hobbies = request.POST.get('hobbies')
        profile_picture = request.FILES.get('profile_picture')

        # Update the username if it's changed
        if username and username != request.user.username:
            if CustomerUser.objects.filter(username=username).exists():
                messages.error(request, 'Username is already taken. Please choose a different one.')
                return redirect('userprofile')
            else:
                request.user.username = username
                request.user.save()
                messages.success(request, 'Username updated successfully!')

        elif first_name and first_name != request.user.first_name:
            request.user.first_name = first_name
            request.user.save()
        
        elif last_name and last_name != request.user.last_name:
            request.user.last_name = last_name
            request.user.save()
        
        elif email and email != request.user.email:
            request.user.email = email
            request.user.save()

        # Check if the phone number already exists (excluding the current user's profile)
        if phone_number:
            if UserProfile.objects.filter(phone_number=phone_number).exclude(user=request.user).exists():
                messages.warning(request, 'Phone number already exists. Please provide a different one.')
                return redirect('/auth_access/userprofile/')
            else:
                user_profile.phone_number = phone_number

        # Update other fields if they are provided
        if profile_picture:
            user_profile.profile_picture = profile_picture
        if date_of_birth:
            user_profile.date_of_birth = date_of_birth
        if gender: 
            user_profile.gender = gender
        if address:
            user_profile.address = address
        if nationality:
            user_profile.nationality = nationality
        if emergency_contact_name:
            user_profile.emergency_contact_name = emergency_contact_name
        if emergency_contact_phone:
            user_profile.emergency_contact_phone = emergency_contact_phone
        if blood_group:   
            user_profile.blood_group = blood_group
        if hobbies:
            user_profile.hobbies = hobbies

        user_profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('/auth_access/userprofile/')  # Redirect back to the profile page after saving
    
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'edit_user_profile.html', context)


@login_required
def UserProfileUpdate(request):
    """
    Handles the update of the user's profile information, including the user form and user profile form.
    Only accessible by logged-in users.
    """
    # Initialize the forms with the POST data (if any) and the current user's data
    u_form = UserUpdateForm(request.POST, instance=request.user)
    p_form = UserProfileUpdateForm(request.POST, instance=request.user.userprofile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }

    # If the forms are valid, save the changes
    if request.method == 'POST':
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')  # Redirect to the profile page after updating

    return render(request, 'profile.html', context)

# Export user profiles to a CSV file
@login_required
def profile_csv(request):
    if not request.user.is_admin:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('home')
    """
    Exports all user profiles to a CSV file for download.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=profiles.csv'

    writer = csv.writer(response)
    
    # Query all CustomerUser instances
    profiles = CustomerUser.objects.all()

    # Write the header row for the CSV file
    writer.writerow(['Username', 'Email', 'Phone_Number', 'Profile_Image'])

    # Write data for each user profile
    for profile in profiles:
        writer.writerow([profile.username, profile.email, profile.userprofile.phone_number, profile.userprofile.profile_picture.url])

    return response

# Confirm Letter View - Handles creating admission letters for students
@login_required
def confirm_letter(request):
    if not request.user.is_admin:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('home')
    """
    Handles the creation of an admission letter for students.
    Accepts POST requests with student details and saves the student record.
    """
    if request.method == "POST":
        # Get form data from the POST request
        name = request.POST.get('name')
        course_name = request.POST.get('course_name')
        level = request.POST.get('level')
        period = request.POST.get('period')
        reporting_date = request.POST.get('reporting_date')

        # Validate required fields
        if not name or not course_name or not level or not period or not reporting_date:
            messages.error(request, "All fields are required!")
            return render(request, 'kmet.html')

        # Validate that level and period are integers
        try:
            level = int(level)
            period = int(period)
        except ValueError:
            messages.error(request, "Level and Period must be valid integers.")
            return render(request, 'kmet.html')

        # Create and save the student record
        try:
            letter = Student(
                name=name,
                course_name=course_name,
                level_of_study=level,
                period_of_study=period,
                reporting_date=reporting_date,
            )
            letter.save()
            messages.success(request, "Admission Letter created successfully.")
            return redirect('/auth_access/confirm_letter/')  # Redirect after success
        except Exception as e:
            messages.error(request, f"Error creating admission letter: {str(e)}")
            return render(request, 'kmet.html')

    return render(request, 'kmet.html')

# Export admission letters to a CSV file
@login_required
def letter_csv(request):
    if not request.user.is_admin:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('home')
    """
    Exports all admission letters (student records) to a CSV file for download.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=letter.csv'

    writer = csv.writer(response)

    # Query all Student instances
    letters = Student.objects.all()

    # Write the header row for the CSV file
    writer.writerow(['Student Name', 'Course', 'Level', 'Period of Study', 'Reporting Date'])

    # Write data for each student record
    for letter in letters:
        writer.writerow([letter.name, letter.course_name, letter.level_of_study, letter.period_of_study, letter.reporting_date])

    return response

@login_required
def ShowUsers(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('/')  # Redirect to the home page
    else:
        myusers = CustomerUser.objects.all()
        # Setup pagination
        p = Paginator(CustomerUser.objects.all(), 5)
        page = request.GET.get('page')
        techusers = p.get_page(page)
        nums = "a" * techusers.paginator.num_pages
    
    context = {
    'myusers':myusers,
    'techusers':techusers,
    'nums':nums,
    'user_profile':user_profile,
    }
    return render(request, 'view_users.html', context)


@login_required
def update_user(request, id):
    if not request.user.is_admin:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('home')
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.user.is_admin:
        d = CustomerUser.objects.get(id=id)
        
        # Prevent action if the user is a superuser
        if d.is_superuser:
            messages.error(request, "You cannot update a superuser.")
            return redirect('/auth_access/techusers/')
        
        if request.method == "POST":
            # Collect data from the update form
            username = request.POST.get('username')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            profile_picture = request.FILES.get('profile_picture')
            role = request.POST.get('role')

            # Validate email format
            try:
                validate_email(email)
            except ValidationError:
                messages.info(request, "Invalid email format.")
                return redirect('/auth_access/techusers/')

            # Validate role
            if role not in ['admin', 'employee', 'customer', 'teacher', 'student']:
                messages.error(request, "Invalid role selected.")
                return redirect('/auth_access/techusers/')

            else:
                edit = CustomerUser.objects.get(id=id)
                edit.username = username
                edit.email = email
                edit.userprofile.phone_number = phone_number

                if profile_picture:
                    # Save the new profile picture (this will overwrite the old one)
                    edit.userprofile.profile_picture = profile_picture

                # Assign roles
                if role == 'admin':
                    edit.is_admin = True
                    edit.is_employee = False
                    edit.is_teacher = False
                    edit.is_student = False
                    edit.is_customer = False
                elif role == 'employee':
                    edit.is_employee = True
                    edit.is_teacher = False
                    edit.is_student = False
                    edit.is_customer = False
                    edit.is_admin = False
                elif role == 'teacher':
                    edit.is_teacher = True
                    edit.is_student = False
                    edit.is_customer = False
                    edit.is_admin = False
                    edit.is_employee = False
                elif role == 'student':
                    edit.is_student = True
                    edit.is_teacher = False
                    edit.is_customer = False
                    edit.is_admin = False
                    edit.is_employee = False
                else:
                    edit.is_customer = True
                    edit.is_admin = False
                    edit.is_employee = False
                    edit.is_student = False
                    edit.is_teacher = False

                edit.save()  # Save the user changes to the database

                # Optionally, you can also save the user profile if it's a separate model
                edit.userprofile.save()

                messages.success(request, f'{username} updated successfully!')
                return redirect('/auth_access/techusers/')
        
        context = {'d': d, 'user_profile': user_profile,}
        return render(request, 'edit.html', context)
    else:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('home')  # Redirect to the home page

        
        
@login_required
def delete_user(request, id):
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('/')  # Redirect to the home page
    else:
        myuser = CustomerUser.objects.get(id=id)
        
        # Prevent action if the user is a superuser
        if myuser.is_superuser:
            messages.error(request, "You cannot delete a superuser.")
            return redirect('/auth_access/techusers/')
        
        myuser.delete()
        return redirect('/auth_access/techusers/')


@login_required
def deactivate_user(request, id):
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('/')  # Redirect to the home page
    else:
        myuser = CustomerUser.objects.get(id=id)
        
        # Prevent action if the user is a superuser
        if myuser.is_superuser:
            messages.error(request, "You cannot deactivate a superuser.")
            return redirect('/auth_access/techusers/')
        
        myuser.is_active = False
        myuser.save()
        return redirect('/auth_access/techusers/')


@login_required
def activate_user(request, id):
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('/')  # Redirect to the home page
    else:
        myuser = CustomerUser.objects.get(id=id)
        
        # Prevent action if the user is a superuser
        if myuser.is_superuser:
            messages.error(request, "You cannot activate a superuser.")
            return redirect('/auth_access/techusers/')
        
        myuser.is_active = True
        myuser.save()
        return redirect('/auth_access/techusers/')


@login_required
def view_full_profile(request, id):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('/')  # Redirect to the home page
    else:
        acc = CustomerUser.objects.get(id=id)

    context = {'acc':acc, 'user_profile': user_profile, }
    return render(request, 'full_profile.html', context)


# View to handle course application
def apply_for_course(request):
    if not request.user.is_admin:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('home')

    if request.method == 'POST':
        student_id = request.POST['student_id']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        course_id = request.POST['course_id']
        level_id = request.POST.get('level_id')

        # Validations
        if StudentApp.objects.filter(student_id=student_id).exists():
            messages.warning(request, "The identification number provided is already registered")
            return redirect('/auth_access/apply/')

        if CustomerUser.objects.filter(email=email).exists():
            messages.warning(request, "The email address provided is already registered")
            return redirect('/auth_access/apply/')

        if UserProfile.objects.filter(phone_number=phone_number).exists():
            messages.warning(request, "The phone number provided is already registered")
            return redirect('/auth_access/apply/')

        course = Course.objects.get(id=course_id)
        level = Level.objects.get(id=level_id) if level_id else None

        # Create a StudentApplication object with the form data
        application = StudentApp(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            course=course,
            level=level,
            phone_number=phone_number
        )
        application.save()  # This triggers the generation of the registration number
        
        # After saving the application, create the user account for the student
        application.create_user_account()

        return redirect('apply_success')

    departments = Department.objects.all()
    user_profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'apply_for_course.html', {
        'departments': departments,
        'user_profile': user_profile,
    })

# View to fetch courses based on department
def get_courses_by_department(request, department_id):
    try:
        courses = Course.objects.filter(department_id=department_id)
        course_list = [{"id": course.id, "name": course.name} for course in courses]
        return JsonResponse({"courses": course_list})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# View to fetch levels based on course
def get_levels_by_course(request, course_id):
    levels = Level.objects.filter(course_id=course_id)
    level_list = [{"id": level.id, "name": level.name} for level in levels]
    return JsonResponse({"levels": level_list})


# View to handle course application
@redirect_if_authenticated
def apply_for_cos(request):
    if request.method == 'POST':
        # Extract data from the form
        student_id = request.POST['student_id']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        course_id = request.POST['course_id']


        if StudentApp.objects.filter(student_id=student_id).exists():
            messages.warning(request, "The identification number provided is already registered")
            return redirect('/auth_access/apply/')

        if CustomerUser.objects.filter(email=email).exists():
            messages.warning(request, "The email address provided is already registered")
            return redirect('/auth_access/apply/')
        
        if UserProfile.objects.filter(phone_number=phone_number).exists():
            messages.warning(request, "The phone_number provided is already registered")
            return redirect('/auth_access/apply/')

        # Get the course based on the selected course ID
        course = Course.objects.get(id=course_id)
        
        # Create a StudentApplication object with the form data
        application = StudentApp(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            course=course,
            phone_number=phone_number
        )
        application.save()  # This triggers the generation of the registration number
        
        # After saving the application, create the user account for the student
        application.create_user_account()
        
        return redirect('apply_success')  # Redirect to success page after the application is submitted
    
    # Retrieve all available courses to show in the form
    courses = Course.objects.all()
    user_profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'apply_for_course.html', {'courses': courses, 'user_profile':user_profile})

@login_required
def add_teacher(request):
    if not request.user.is_admin:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('home')
    if request.method == 'POST':
        # Extract data from the form
        id_number = request.POST['id_number']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        course_id = request.POST['course_id']


        if Teacher.objects.filter(id_number=id_number).exists():
            messages.warning(request, "The identification number provided is already registered")
            return redirect('/auth_access/apply/')

        if CustomerUser.objects.filter(email=email).exists():
            messages.warning(request, "The email address provided is already registered")
            return redirect('/auth_access/apply/')

        # Get the course based on the selected course ID
        course = Course.objects.get(id=course_id)
        
        # Create a StudentApplication object with the form data
        application = Teacher(
            id_number=id_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            course=course
        )
        application.save()  # This triggers the generation of the staff number
        
        # After saving the application, create the user account for the teacher
        application.create_user_account()
        
        return redirect('apply_success')  # Redirect to success page after the application is submitted
    
    # Retrieve all available courses to show in the form
    departments = Department.objects.all()
    user_profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'add_teacher.html', {'departments': departments, 'user_profile':user_profile})

class ActivateAccountView(View):
    """
    Handles the process of activating user account  after the user clicks the reset link.
    """
    def get(self, request, uidb64, token):

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomerUser.objects.get(pk=user_id)

        except Exception as identifier:
            user = None

            # Verify the token
        
        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            print(f"Token valid for user: {user.username}")  # Debugging output
            user.is_active = True  # Set the user as active
            user.save()  # Save the user after activation
            
            user.backend = 'useraccess.auth_backends.EmailAuthBackend'
            login(request, user)# Log the user in

            if user.is_student == True:
                # Redirect to the student dashboard after successful login
                return redirect('/auth_access/student_dashboard/')  # Adjust to the actual name of your student dashboard view

            if user.is_teacher == True:
                return redirect('/auth_access/teacher_dashboard/')

            if user.is_employee == True:
                return redirect('/auth_access/staff_dashboard/')

            if user.is_admin == True:
                return redirect('/auth_access/admin_dashboard/')

        else:
            messages.warning(request, "Invalid reset link.")
            return redirect('/')


# Student Dashboard View (only accessible after login)
@login_required
def student_dashboard(request):
    if not request.user.is_student:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('home')
    user_profile = get_object_or_404(UserProfile, user=request.user)
    student = request.user  # Assuming 'request.user' is a logged-in student (StudentApp)
    
    # Check if user is a student, based on your 'is_student' flag
    if student.is_student:
        # Assuming 'registration_number' is a field in the 'StudentApp' model
        # Retrieve the student using registration_number
        try:
            stud = StudentApp.objects.get(registration_number=student.username)
        except StudentApp.DoesNotExist:
            stud = None  # In case there's no student with the given registration_number
            messages.warning(request, "Student data not found")

        bio_data = get_object_or_404(UserProfile, user=student)

    
    return render(request, 'student_dashboard.html', {
        'stud':stud,
        'bio_data':bio_data,
        'user_profile':user_profile,
    })

# Success view after application
def apply_success(request):
    return render(request, 'apply_success.html')


@login_required
def teacher_dashboard(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if not request.user.is_teacher:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('/')  # Redirect to the home page
    else:
        teacher = request.user
        try:
            stud = Teacher.objects.get(staff_number=teacher.username)
            total_students = StudentApp.objects.count()
        except Teacher.DoesNotExist:
            stud = None  # In case there's no student with the given registration_number
            messages.warning(request, "Teacher data not found")

        bio_data = get_object_or_404(UserProfile, user=teacher)
            
    return render(request, 'teacher_dashboard.html', {
        'bio_data':bio_data,
        'stud':stud,
        'total_students':total_students,
        'user_profile':user_profile,

    })