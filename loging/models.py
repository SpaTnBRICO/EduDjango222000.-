from django.db import models
from useraccess.models import StudentApp, CustomerUser, Course, Level
from decimal import Decimal
import random
import string
from django.template.defaultfilters import timesince
from django.utils import timezone
from datetime import datetime

from PIL import Image, ImageOps
import os
from io import BytesIO
from django.core.files import File

class Contact(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=50, null=True, blank=True)
    subject = models.CharField(max_length=50, null=True, blank=True)
    message = models.TextField()
    read = models.BooleanField(default=False)
    create_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.email

class SiteLogo(models.Model):
    logo_name = models.CharField(max_length=100, default="My Website")
    logo = models.ImageField(upload_to='logos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)  # Allows you to switch logos if needed

    def __str__(self):
        return f"{self.logo_name} Logo"

    def save(self, *args, **kwargs):
        # Save the model first to ensure `self.logo.path` exists
        super().save(*args, **kwargs)

        try:
            img = Image.open(self.logo.path)

            max_size = (500, 500)
            if img.height > 500 or img.width > 500:
                img.thumbnail(max_size)  # Resize while maintaining aspect ratio
                img.save(self.logo.path)
        except Exception as e:
            # Optional: log or print error if resizing fails
            print(f"Error resizing logo image: {e}")

class Slider(models.Model):
    title = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to="slider_images/", default="Youth.jpg")
    sub_title = models.CharField(max_length=50, null=True, blank=True)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    
    # Set the desired width and height
    target_width = 1125  # Example width
    target_height = 2000  # Example height

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
        super(Slider, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Event(models.Model):
    # Event Name (string, can be up to 200 characters)
    name = models.CharField(max_length=200)

    image = models.ImageField(upload_to="Events_images/", blank=True, null=True)
    
    # Event Description (optional text field)
    description = models.TextField(blank=True, null=True)

    is_approved = models.BooleanField(default=False)
    
    # Event Start Date (using DateTimeField for full date)
    start_date = models.DateField()

    # Event End Date
    end_date = models.DateField()

    # Event Start Month (Full month name)
    start_month = models.CharField(max_length=20, blank=True, null=True)

    # Event End Month (Full month name)
    end_month = models.CharField(max_length=20, blank=True, null=True)
    
    # Event Start Year (Year as an integer)
    start_year = models.IntegerField(blank=True, null=True)

    # Event End Year (Year as an integer)
    end_year = models.IntegerField(blank=True, null=True)

    # Event Start Day (Day of the month as an integer)
    start_day = models.IntegerField(blank=True, null=True)

    # Event End Day (Day of the month as an integer)
    end_day = models.IntegerField(blank=True, null=True)

    # Event Start Time (Time only, stored as a TimeField)
    start_time = models.TimeField()

    # Event End Time (Time only, stored as a TimeField)
    end_time = models.TimeField()

    # Event Location (string, can be up to 200 characters)
    location = models.CharField(max_length=200)

    # Set the desired width and height
    target_width = 300  # Example width
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

        # Automatically populate start_date related fields
        if self.start_date:
            if isinstance(self.start_date, datetime):
                self.start_month = self.start_date.strftime('%B')  # Full month name
            elif isinstance(self.start_date, str):
                self.start_date = datetime.strptime(self.start_date, '%Y-%m-%d').date()
                self.start_month = self.start_date.strftime('%B')
            self.start_year = self.start_date.year
            self.start_day = self.start_date.day  # Store the day of the month (1 to 31)
        
        # Automatically populate end_date related fields
        if self.end_date:
            if isinstance(self.end_date, datetime):
                self.end_month = self.end_date.strftime('%B')  # Full month name
            elif isinstance(self.end_date, str):
                self.end_date = datetime.strptime(self.end_date, '%Y-%m-%d').date()
                self.end_month = self.end_date.strftime('%B')
            self.end_year = self.end_date.year
            self.end_day = self.end_date.day  # Store the day of the month (1 to 31)

        # Call the original save method to save the model
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['start_date']


class News(models.Model):
    # News Title (string, can be up to 200 characters)
    title = models.CharField(max_length=200)

    # News Content (text field to store the full article)
    content = models.TextField()

    # Author of the news article (optional, could be a ForeignKey to a User model)
    author = models.CharField(max_length=100, blank=True, null=True)

    # Date of Publication
    published_date = models.DateTimeField(auto_now_add=True)

    # Date of Last Modification (optional)
    modified_date = models.DateTimeField(auto_now=True)

    # Status of the article (whether the article is published or not)
    is_published = models.BooleanField(default=False)

    # Image for the news article (optional, for adding an image with the news)
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)

    # Category (optional, to categorize the news like "Politics", "Sports", etc.)
    category = models.CharField(max_length=100, blank=True, null=True)

    # Set the desired width and height
    target_width = 500  # Example width
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
        super(News, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_preview(self):
        return self.content[:50]  # Preview first 50 characters

    class Meta:
        # Ordering the news articles by publication date (newest first)
        ordering = ['-published_date']


class Blog(models.Model):
    # Title of the blog (string, can be up to 100 characters)
    title = models.CharField(max_length=100, blank=True, null=True)

    # Author of the blog (string, can be up to 100 characters)
    author = models.CharField(max_length=100, blank=True, null=True)

    # Content or body of the blog (text field, for the main content)
    content = models.TextField(blank=True, null=True)

    # Date of Creation (automatically set when the blog is created)
    created_date = models.DateTimeField(auto_now_add=True)

    # Date of Last Modification (automatically updated every time the blog is updated)
    modified_date = models.DateTimeField(auto_now=True)

    # Status of the blog article (whether the article is approved or not)
    is_approved = models.BooleanField(default=False)

    # Image for the blog (optional, for adding an image to the blog)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)

    # Tags for the blog (optional, could be useful for SEO and filtering)
    tags = models.CharField(max_length=255, blank=True, null=True)

    # Published date (optional: allow the blog to be scheduled for a future date)
    published_date = models.DateTimeField(blank=True, null=True)

    # A brief summary (for previews or listings)
    summary = models.CharField(max_length=300, blank=True, null=True)


    # Set the desired width and height
    target_width = 500  # Example width
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
        super(Blog, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    # Custom method to get a preview of the blog content
    def get_preview(self):
        return self.content[:50]  # Preview first 50 characters

    class Meta:
        ordering = ['-created_date']  # Display the most recent blogs first


class Reply(models.Model):
    contact = models.ForeignKey(Contact, related_name='replies', on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True, null=True)
    reply_message = models.TextField()
    replied_at = models.DateTimeField(auto_now_add=True)
    replied_by = models.CharField(max_length=100, blank=True, null=True)  # Can be the name of the person replying
    attachment = models.FileField(upload_to='replies/attachments/', null=True, blank=True)

    def __str__(self):
        return f"Reply to {self.contact.email}"

class Forward(models.Model):
    contact = models.ForeignKey(Contact, related_name='forwards', on_delete=models.CASCADE, null=True, blank=True)
    forwarded_to = models.EmailField()  # Or could be a CharField for a name or system
    forwarded_at = models.DateTimeField(auto_now_add=True)
    forwarded_by = models.CharField(max_length=100)  # Who forwarded the message or reply
    message = models.TextField(null=True, blank=True)  # Optional message explaining the forward

    def __str__(self):
        if self.contact:
            return f"Forwarded contact from {self.contact.email} to {self.forwarded_to}"
        return f"Forwarded reply to {self.forwarded_to}"

class ComposeEmail(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    recipients = models.TextField(help_text="Comma-separated list of email addresses")
    sender = models.EmailField()  # Email address of the sender
    cc = models.TextField(null=True, blank=True, help_text="Comma-separated list of CC email addresses")
    bcc = models.TextField(null=True, blank=True, help_text="Comma-separated list of BCC email addresses")
    attachments = models.FileField(upload_to='emails/attachments/', null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)  # If the email has been sent, this will store the sent time
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True, blank=True)  # Associated user

    def __str__(self):
        return f"Email to {self.recipients} - {self.subject}"

class FeePayment(models.Model):
    student = models.ForeignKey(StudentApp, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_phone_number = models.CharField(max_length=50, null=True, blank=True)
    fees_payment_for = models.CharField(max_length=50, null=True, blank=True)
    new_remaining_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    receipt_number = models.CharField(max_length=50, null=True, blank=True)
    registration_number = models.CharField(max_length=50, null=True, blank=True)
    mode_of_payment = models.CharField(max_length=50, null=True, blank=True)
    payment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.registration_number} - {self.amount} paid on {self.payment_date}"

    def generate_receipt_number(self):
        # Generate a registration number prefix
        registration_number = self.mode_of_payment.upper()

        # Generate a random string of 8 characters consisting of both digits and uppercase letters
        rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        # Combine the registration number prefix with the random string
        self.receipt_number = f'{registration_number}-{rand}'

        # Ensure the receipt number is unique
        while FeePayment.objects.filter(receipt_number=self.receipt_number).exists():
            rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            self.receipt_number = f'{registration_number}-{rand}'

    def save(self, *args, **kwargs):
        # Initialize student's total_paid and remaining_balance if None
        if self.student.total_paid is None:
            self.student.total_paid = Decimal('0.00')
        if self.student.remaining_balance is None:
            self.student.remaining_balance = self.student.course.price if self.student.course else Decimal('0.00')

        if self.amount is None:
            self.amount = Decimal('0.00')

        # Calculate the new remaining balance before updating the student's balance
        if self.new_remaining_balance is None:
            self.new_remaining_balance = self.student.remaining_balance - self.amount

        # Generate receipt number if not provided
        if not self.receipt_number:
            self.generate_receipt_number()

        # Update the student's remaining balance and total paid
        self.student.remaining_balance -= self.amount
        self.student.total_paid += self.amount

        # Save the updated student object
        self.student.save()

        # Call the parent class's save method to save the FeePayment instance
        super().save(*args, **kwargs)

		# Set remaining_balance to the course price by default if it's None
		

		# Ensure the amount is not None
		

		# Ensure remaining_balance and total_paid are not None before performing operatio

class GoogleFormAssignment(models.Model):
    user = models.ForeignKey(CustomerUser, related_name='googleform', on_delete=models.CASCADE)
    title = models.CharField(max_length=50, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    link = models.URLField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.name} googleform assignment on {self.title}"



class Notes(models.Model):
    user = models.ForeignKey(CustomerUser, related_name='notes', on_delete=models.CASCADE)
    title = models.CharField(max_length=50, null=True, blank=True)
    thumbnail = models.ImageField(upload_to='notes_thumbnails/')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='notes_docs/')
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.name} notes on {self.title}"


class Tutorial(models.Model):
    user = models.ForeignKey(CustomerUser, related_name='tutorials', on_delete=models.CASCADE)
    title = models.CharField(max_length=50, null=True, blank=True)
    thumbnail = models.ImageField(upload_to='tutorial_thumbnails/')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, null=True, blank=True)
    video_file = models.FileField(upload_to='tutorial_videos/')  # To upload videos to a folder
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.name} video on {self.title}"


class Quiz(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, null=True, blank=True)
    teacher = models.CharField(max_length=255, null=False, blank=True)
    is_exam = models.BooleanField(default=False)  # True for exam, False for quiz
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    total_marks = models.PositiveIntegerField()
    text = models.TextField()

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class QuizAttempt(models.Model):
    student = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField(null=True, blank=True)
    registration_number = models.CharField(max_length=50, null=True, blank=True)
    attempt_number = models.PositiveIntegerField(default=1)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'quiz', 'attempt_number')