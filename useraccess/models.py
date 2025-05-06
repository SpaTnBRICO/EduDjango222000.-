from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import random
import string
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from decimal import Decimal
from django.contrib import messages

#WhatsApp
import os
#from twilio.rest import Client
from django.conf import settings
import logging
from django.shortcuts import get_object_or_404

from PIL import Image, ImageOps
import os
from io import BytesIO
from django.core.files import File

#Email Stuff
from django.core.mail import send_mail

logger = logging.getLogger(__name__)  # Initialize logger


"""
run in mysql to avoid 
#.OperationalError: (1071, 'Specified key was too long; max key length is 3072 bytes')
ALTER DATABASE proj11 CHARACTER SET = utf8 COLLATE = utf8_general_ci;

"""


class CustomerUserManager(BaseUserManager):
    def create_user(self, username, email, first_name=None, last_name=None, password=None):
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")  # Ensure username is provided
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.is_staff = False  # By default, a regular user is not a staff member
        user.is_active = False 
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, first_name=None, last_name=None, password=None):
        user = self.create_user(username, email, first_name, last_name, password)
        user.is_admin = True
        user.is_staff = True  # Superuser should be staff
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user

class CustomerUser(AbstractBaseUser, PermissionsMixin):
    # Fields
    username = models.CharField(max_length=50, unique=True)  # Reduced max_length for compatibility with utf8mb4
    email = models.EmailField(unique=True, max_length=50)  # Reduced max_length for compatibility with utf8mb4
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now, editable=False, null=True, blank=True)
    is_active = models.BooleanField(default=False)

    # Role flags
    is_admin = models.BooleanField('Is admin', default=False)
    is_customer = models.BooleanField('Is customer', default=False)
    is_employee = models.BooleanField('Is employee', default=False)
    is_student = models.BooleanField('Is student', default=False)
    is_teacher = models.BooleanField('Is teacher', default=False)

    # Staff flag
    is_staff = models.BooleanField('Is staff', default=False)

    # Set the USERNAME_FIELD to the field you want to use as the unique identifier
    USERNAME_FIELD = 'username'  # Or 'email' if you want to use email as the username
    REQUIRED_FIELDS = ['email']  # Added 'username' as a required field

    objects = CustomerUserManager()  # Using custom manager

    def save(self, *args, **kwargs):
        # Ensure only one role is selected at a time
        if self.is_admin:
            self.is_customer = False
            self.is_employee = False
            self.is_student = False
        elif self.is_employee:
            self.is_admin = False
            self.is_customer = False
            self.is_student = False
        elif self.is_customer:
            self.is_admin = False
            self.is_employee = False
            self.is_student = False
        elif self.is_student:
            self.is_admin = False
            self.is_employee = False
            self.is_customer = False

        super(CustomerUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.username

    # Add the is_anonymous property
    @property
    def is_anonymous(self):
        return False  # This is because this user is not anonymous

    # The is_authenticated property is already provided by AbstractBaseUser & PermissionsMixin
    @property
    def is_authenticated(self):
        return True  # This means this user is authenticated


def default_user_instance():
    # Replace this with the logic to return a default user (e.g., the first user in the DB)
    return CustomerUser.objects.first()


class UserProfile(models.Model):
    user = models.OneToOneField(CustomerUser, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    profile_picture = models.ImageField(default="default.jpg", upload_to='profile_pics/')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True)
    address = models.TextField(null=True, blank=True)    
    nationality = models.CharField(max_length=50, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, null=True, blank=True)
    blood_group = models.CharField(max_length=10, null=True, blank=True)
    hobbies = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Student(models.Model):
    name = models.CharField(max_length=50)  # Limited to 191 characters
    course_name = models.CharField(max_length=50)  # Limited to 191 characters
    level_of_study = models.IntegerField()
    period_of_study = models.IntegerField()  # in months
    reporting_date = models.DateTimeField()

    def __str__(self):
        return f"{self.name}'s Admission Letter Info."


class Department(models.Model):
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to="department-images", default="Youth.jpg", null=True, blank=True)
    is_tution = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False, null=True, blank=True)

    # Set the desired width and height
    target_width = 420  # Example width
    target_height = 700  # Example height

    def save(self, *args, **kwargs):
        if self.image:
            # Open the image using Pillow
            img = Image.open(self.image)

            # Get the original dimensions
            original_width, original_height = img.size
            
            # Calculate the aspect ratio
            aspect_ratio = original_width / original_height

            # Calculate the new width and height while maintaining the aspect ratio
            if original_width / self.target_width > original_height / self.target_height:
                # Scale based on width
                new_width = self.target_width
                new_height = int(new_width / aspect_ratio)
            else:
                # Scale based on height
                new_height = self.target_height
                new_width = int(new_height * aspect_ratio)

            # Resize the image to fit within the target dimensions
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create a new image with the desired dimensions and a white (or transparent) background
            new_image = Image.new("RGB", (self.target_width, self.target_height), (255, 255, 255))  # RGB background (white)
            
            # Calculate padding to center the image
            left_padding = (self.target_width - new_width) // 2
            top_padding = (self.target_height - new_height) // 2

            # Paste the resized image into the new image with padding
            new_image.paste(img, (left_padding, top_padding))

            # Save the resized image
            temp_image_path = os.path.join('media', self.image.name)
            new_image.save(temp_image_path)
            
            # Update the image field with the resized image
            self.image.name = self.image.name  # Ensure the image path remains the same

        # Call the original save method to save the model
        super(Department, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


# Course Model
class Course(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="course-images", null=True, blank=True)
    price = models.IntegerField(null=True)
    period_of_study = models.IntegerField(null=True)  # in months
    description = models.TextField(blank=True, null=True)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name="courses")
    code = models.CharField(max_length=10, unique=True, blank=True, null=True, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False, null=True, blank=True)


    # Set the desired width and height
    target_width = 420  # Example width
    target_height = 700  # Example height

    def generate_course_code(self):
        department_code = self.department.name[:3].upper()
        random_digits = ''.join(random.choices(string.digits, k=4))
        course_code = f"{department_code}{random_digits}"

        while Course.objects.filter(code=course_code).exists():
            random_digits = ''.join(random.choices(string.digits, k=4))
            course_code = f"{department_code}{random_digits}"

        return course_code

    def save(self, *args, **kwargs):
        if self.image:
            # Open the image using Pillow
            img = Image.open(self.image)

            # Get the original dimensions
            original_width, original_height = img.size
            
            # Calculate the aspect ratio
            aspect_ratio = original_width / original_height

            # Calculate the new width and height while maintaining the aspect ratio
            if original_width / self.target_width > original_height / self.target_height:
                # Scale based on width
                new_width = self.target_width
                new_height = int(new_width / aspect_ratio)
            else:
                # Scale based on height
                new_height = self.target_height
                new_width = int(new_height * aspect_ratio)

            # Resize the image to fit within the target dimensions
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create a new image with the desired dimensions and a white (or transparent) background
            new_image = Image.new("RGB", (self.target_width, self.target_height), (255, 255, 255))  # RGB background (white)
            
            # Calculate padding to center the image
            left_padding = (self.target_width - new_width) // 2
            top_padding = (self.target_height - new_height) // 2

            # Paste the resized image into the new image with padding
            new_image.paste(img, (left_padding, top_padding))

            # Save the resized image
            temp_image_path = os.path.join('media', self.image.name)
            new_image.save(temp_image_path)
            
            # Update the image field with the resized image
            self.image.name = self.image.name  # Ensure the image path remains the same
        if not self.code:
            self.code = self.generate_course_code()
        super(Course, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Level(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='levels')
    name = models.CharField(max_length=15, blank=True, null=True)
    modified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f"{self.name}--{self.course.name}"

class Unit(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='units')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, blank=True, null=True, related_name='unit_level')
    name = models.CharField(max_length=50, blank=True, null=True)
    teacher = models.CharField(max_length=50, blank=True, null=True)
    unit_code = models.CharField(max_length=50, unique=True, blank=True, null=True, editable=False)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    modified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def generate_unit_code(self):
        course_code = self.course.code.upper()
        random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        self.unit_code = f"{course_code}/{random_suffix}"

        while Unit.objects.filter(unit_code=self.unit_code).exists():
            random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
            self.unit_code = f"{course_code}/{random_suffix}"

    def save(self, *args, **kwargs):
        if not self.unit_code:
            self.generate_unit_code()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}--{self.course.name}--{self.unit_code}"





def default_user_instance():
    # Replace this with the logic to return a default user (e.g., the first user in the DB)
    return CustomerUser.objects.first()

class StudentApp(models.Model):
    stud = models.OneToOneField(CustomerUser, on_delete=models.CASCADE, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    student_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    is_approved = models.BooleanField(default=False)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)
    total_fees = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='students')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='levels', null=True, blank=True)
    application_year = models.IntegerField(default=timezone.now().year, editable=False)
    registration_number = models.CharField(max_length=50, blank=True, null=True, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def generate_registration_number(self):
        department_code = self.course.department.name[:3].upper()
        course_code = self.course.code.upper()
        year = str(self.application_year)
        random_suffix = ''.join(random.choices(string.digits, k=5))

        reg_num = f'{department_code}/{course_code}/{random_suffix}/{year}'

        # Ensure uniqueness
        while StudentApp.objects.filter(registration_number=reg_num).exists():
            random_suffix = ''.join(random.choices(string.digits, k=5))
            reg_num = f'{department_code}/{course_code}/{random_suffix}/{year}'

        self.registration_number = reg_num

    def save(self, *args, **kwargs):
        if not self.registration_number:
            self.generate_registration_number()

        # Set default fee fields if needed
        if self.total_paid is None:
            self.total_paid = Decimal('0.00')

        if self.total_fees is None or self.total_fees == Decimal('0.00'):
            self.total_fees = self.course.price

        if self.remaining_balance is None:
            self.remaining_balance = self.total_fees

        super().save(*args, **kwargs)

    def create_user_account(self):
        user = CustomerUser.objects.create_user(username=self.registration_number,
                                                 email=self.email,
                                                 password=self.student_id,
                                                 first_name=self.first_name,
                                                 last_name=self.last_name)
        user.is_student = True
        user.is_active = False
        user.save()

        # Link the user to the student instance
        self.stud = user
        self.save(update_fields=['stud'])  # Save only the user field

        user_profile = user.userprofile  # Access the profile created by the signal
        user_profile.phone_number = self.phone_number
        user_profile.save()  # Save updated phone number
        self.send_confirmation_email(user)

    def send_confirmation_email(self, user):
        try:
            token = PasswordResetTokenGenerator().make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_link = f"{settings.BASE_URL}/auth_access/activate/{uid}/{token}/"
            print(activation_link)

            email_address = user.email
            if not email_address:
                logger.error("Missing user email.")
                return

            subject = f"Your Registration for {self.course} is Successful!"
            message = (
                f"Dear {user.first_name} {user.last_name},\n\n"
                f"Congratulations! Your application for the {self.course.name} course in the "
                f"{self.course.department.name} Department has been successfully processed.\n\n"
                f"Your registration number is: {self.registration_number}\n\n"
                f"Login Info:\n"
                f" - Username: {self.registration_number}\n"
                f" - Password: Your student ID\n\n"
                f"Activate your account here:\n{activation_link}\n\n"
                f"If you need help, contact the admissions team.\n\n"
                f"Best regards,\n"
                f"TechSols Admissions Team"
            )

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email_address])
            logger.info("Registration email sent successfully.")

        except Exception as e:
            logger.error(f"Error sending registration email: {e}")

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Reg: {self.registration_number})"


class Teacher(models.Model):
    user = models.OneToOneField(CustomerUser, on_delete=models.CASCADE, null=True, blank=True)
    id_number = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    is_approved = models.BooleanField(default=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    staff_number = models.CharField(max_length=50, unique=True)
    year_joined = models.IntegerField(default=timezone.now().year, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def generate_staff_number(self):
        staff_code = 'LEC'
        course_code = self.course.code.upper()
        year = str(self.year_joined)
        random_suffix = ''.join(random.choices(string.digits, k=5))
        self.staff_number = f'{staff_code}/{course_code}/{random_suffix}/{year}'

        while Teacher.objects.filter(staff_number=self.staff_number).exists():
            random_suffix = ''.join(random.choices(string.digits, k=5))
            self.staff_number = f'{staff_code}/{course_code}/{random_suffix}/{year}'

    def save(self, *args, **kwargs):
        if not self.staff_number:
            self.generate_staff_number()
        super().save(*args, **kwargs)

    def create_user_account(self):
        user = CustomerUser.objects.create_user(username=self.staff_number,
                                                 email=self.email,
                                                 password=self.id_number,
                                                 first_name=self.first_name,
                                                 last_name=self.last_name)
        user.is_teacher = True
        user.is_active = False
        user.save()

        # Link the user to the teacher instance
        self.user = user
        self.save(update_fields=['user'])  # Save only the user field

        self.send_confirmation_email(user)

    def send_confirmation_email(self, user):
        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = f"{settings.BASE_URL}/auth_access/activate/{uid}/{token}/"
        print(f"Activation Link: {activation_link}")

        try:
            # Retrieve the user profile
            user_profile = get_object_or_404(UserProfile, user=user)
            email_address = user_profile.user.email  # Ensure the email is available

            if not email_address:
                logger.error("Email address is missing.")
                return

            # Prepare the email content
            subject = f"Congratulations on Your Successful Registration for {self.course} Course as an instructor."
            message = (
                f"Dear {user.first_name} {user.last_name},\n\n"
                f"Congratulations! You been selected as an instructor for {self.course} course in {self.course.department.name} Department "
                f"Your staff number is: {self.staff_number}\n\n"
                f"To access the teacher dashboard, use your staff number "
                f"and the identification number you provided as your password.\n\n"
                f"To activate your account, click the link below:\n"
                f"{activation_link}\n\n"
                f"Should you have any questions, contact us.\n\n"
                f"Best regards,\n"
                f"TechSols Admissions Team"
            )
            from_email = settings.DEFAULT_FROM_EMAIL  # From email address (configured in settings.py)
            recipient_list = [email_address]  # List of recipient emails

            # Send the email
            send_mail(subject, message, from_email, recipient_list)

            logger.info("Email sent successfully.")

        except Exception as e:
            logger.error(f"Failed to send email: {e}")

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Registration: {self.staff_number})"


class CAT(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='cats')
    title = models.CharField(max_length=50)
    created_by = models.CharField(max_length=50, null=True, blank=True)
    attendance_sheet = models.FileField(upload_to='test_attendance/cats/', null=True, blank=True)
    mark_sheet = models.FileField(upload_to='marksheets/cats/', null=True, blank=True)
    pc_waiting = models.FileField(upload_to='pc_waiting/cats/', null=True, blank=True)
    is_submitted = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(editable=False, blank=True, null=True )
    

    def __str__(self):
        return f"{self.title} - {self.unit.name}"

class CATScore(models.Model):
    cat = models.ForeignKey(CAT, on_delete=models.CASCADE, related_name='catmark')
    student = models.ForeignKey(StudentApp, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='cats', null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)




    def __str__(self):
        return f"{self.student.registration_number}'s {self.cat.title} - {self.score}"

class Practical(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='pracs')
    title = models.CharField(max_length=50)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.unit.name}"

class PRACScore(models.Model):
    prac = models.ForeignKey(Practical, on_delete=models.CASCADE, related_name='pracmark')
    student = models.ForeignKey(StudentApp, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='pracs', null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.student.stud.username}'s {self.cat.title} - {self.score}"