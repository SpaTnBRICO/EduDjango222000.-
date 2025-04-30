from django.shortcuts import render, redirect, get_object_or_404
from useraccess.models import Course, Department, StudentApp, Teacher, UserProfile, CustomerUser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import FeePayment, SiteLogo, GoogleFormAssignment, Tutorial, Notes, Quiz, Question, Answer, QuizAttempt, Contact, Reply, ComposeEmail, Event, Blog, News, Slider
from decimal import Decimal
from useraccess.utils import send_otp, send_otp_activate_account, redirect_if_authenticated
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from django.views.decorators.csrf import csrf_exempt
import base64
from django.http import JsonResponse
import requests

from .genrateAcesstoken import get_access_token
from .stkPush import initiate_stk_push
from .query import query_stk_status


# Create your views here.
def home(request):
    slides = Slider.objects.all()
    eventss = Event.objects.all()
    courses = Course.objects.all()
    course = Course.objects.count()
    total_students = StudentApp.objects.count()
    news=News.objects.all()
    return render(request, "index.html", {
        'slides': slides,
        'eventss': eventss,
        'courses': courses,
        'course': course,
        'total_students': total_students,
        'news': news,
        })

def create_slides(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        name = request.POST.get('title')
        sub_title = request.POST.get('stitle')
        description = request.POST.get('description')
        image = request.FILES.get('simage')

        slide = Slider(
            title=name,
            image=image,
            content=description,
            is_approved=False,
            sub_title=sub_title
        )

        slide.save()
        messages.success(request, f"{name} Slide is created successfully. Add another one if needed.")
        messages.info(request, "Refresh the homepage to view the added slide")
        return redirect("/create_slides/")
    return render(request, "logs/create_slides.html", {
        "user_profile": user_profile
        })

def manage_slides(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    slides = Slider.objects.all()
    return render(request, "logs/manage_slides.html", {
        'slides': slides,
        'user_profile': user_profile,
    })

def create_logos(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        name = request.POST.get('title')
        image = request.FILES.get('simage')

        slide = SiteLogo(
            logo_name=name,
            logo=image,
            is_active=False
        )

        slide.save()
        messages.success(request, f"{name} Logo is created successfully. Add another one if needed.")
        return redirect("/create_logos/")
    return render(request, "logs/create_logo.html", {
        "user_profile": user_profile
        })

def logo(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    logos = SiteLogo.objects.all()
    return render(request, "logs/logo.html", {
        'logos': logos,
        'user_profile': user_profile,
    })


def set_active_logo(request, logo_id):
    logo_to_activate = get_object_or_404(SiteLogo, id=logo_id)

    # Deactivate all logos
    SiteLogo.objects.update(is_active=False)

    # Activate the selected one
    logo_to_activate.is_active = True
    logo_to_activate.save()

    return redirect('/logos/')

def deactivate_logo(request, logo_id):
    logo_to_deactivate = get_object_or_404(SiteLogo, id=logo_id)

    # Activate the selected one
    logo_to_deactivate.is_active = False
    logo_to_deactivate.save()

    return redirect('/logos/')

def delete_logo(request, logo_id):
    logo_to_activate = get_object_or_404(SiteLogo, id=logo_id)

    # delete the selected one
    logo_to_activate.delete()
    return redirect('/logos/')

def events(request):
    eventss = Event.objects.all()
    return render(request, "logs/events.html", {
        'eventss': eventss,
    })

def create_events(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        name = request.POST.get('title')
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('end_date')
        end_time = request.POST.get('end_time')
        description = request.POST.get('description')
        image = request.FILES.get('photo')
        location = request.POST.get('location')

        event = Event(
            name=name,
            image=image,
            description=description,
            is_approved=False,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            location=location
        )

        event.save()
        return redirect("/events/")
    return render(request, "logs/create_events.html", {
        'user_profile': user_profile,
    })

def news(request):
    news=News.objects.all()
    return render(request, "logs/news.html", {
        'news': news,
        })

def news_details(request, id):
    news=News.objects.get(id=id)
    return render(request, "logs/news_details.html", {
        'news': news,
        })

def create_news(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        name = request.POST.get('title')
        category = request.POST.get('category')
        description = request.POST.get('description')
        image = request.FILES.get('photo')

        new = News(
            title=name,
            image=image,
            author=request.user.first_name,
            content=description,
            is_published=False,
            category=category
        )

        new.save()
        return redirect("/news/")
    return render(request, "logs/create_news.html", {
        'user_profile': user_profile,
    })

def blogs(request):
    blogs=Blog.objects.all()
    return render(request, "logs/blogs.html", {
        'blogs': blogs,
        })

def blog_details(request, id):
    blog=Blog.objects.get(id=id)
    return render(request, "logs/blog_details.html", {
        'blog': blog,
        })

def create_blogs(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        name = request.POST.get('title')
        tags = request.POST.get('tags')
        summary = request.POST.get('summary')
        description = request.POST.get('description')
        image = request.FILES.get('photo')

        blog = Blog(
            title=name,
            image=image,
            author=request.user.first_name,
            content=description,
            is_approved=False,
            tags=tags,
            summary=summary
        )

        blog.save()
        return redirect("/blogs/")
    return render(request, "logs/create_blog.html", {
        'user_profile': user_profile,
    })

def contact(request):
    if request.method == "POST":
        # Safely get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message_content = request.POST.get('message')

        new_message = Contact(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message_content
            )
        new_message.save()



        # Create a reply message
        reply_message = f"""
        <h3>Dear {name},</h3>
        <p>Thank you for reaching out to TechSols. We have received your message and our team will get back to you as soon as possible.</p>
        <p>If you have any urgent queries, feel free to contact us at any time.</p>
        <p>Best regards, <br> The TechSols Team</p>
        """

        # Send the email with HTML content
        send_mail(
            '[TechSols Reply] Thank you for contacting us',
            'This is a placeholder for plain-text email content',  # Plain text version (you can leave it as is)
            settings.DEFAULT_FROM_EMAIL,  # The 'From' email address from settings
            [email],  # The recipient's email address
            fail_silently=False,  # Raise an exception if email fails
            html_message=reply_message  # HTML content of the email
        )

        # Optionally render a response page
        messages.success(request, "Your Message is successfully to TechSols")
        return redirect('/contact/us/')

    # Handle GET request or if POST data is missing
    return render(request, "logs/contact.html", {})



@login_required
def email_inbox(request):
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('/')  # Redirect to the home page
    user_profile = get_object_or_404(UserProfile, user=request.user)
    messages = Contact.objects.all().order_by('-create_at')
    unread_messages_count = Contact.objects.filter(read=False).count()
    return render(request, "logs/email_inbox.html", {
        'user_profile': user_profile,
        'messages': messages,
        'unread_messages_count': unread_messages_count,
    })

@login_required
def email_sentbox(request):
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('/')  # Redirect to the home page
    user_profile = get_object_or_404(UserProfile, user=request.user)
    sent = ComposeEmail.objects.all().order_by('-created_at')
    unread_messages_count = Contact.objects.filter(read=False).count()
    return render(request, "logs/email_sentbox.html", {
        'user_profile': user_profile,
        'sent': sent,
        'unread_messages_count': unread_messages_count,
    })

@login_required
def email_compose(request):
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('/')  # Redirect to the home page
    user_profile = get_object_or_404(UserProfile, user=request.user)
    unread_messages_count = Contact.objects.filter(read=False).count()

    if request.method == "POST":
        # Get form data from POST request
        email = request.POST.get('email')
        cc = request.POST.get('cc')
        bcc = request.POST.get('bcc')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        file = request.FILES.get('attachment')

        # Email validation
        try:
            # Validate the "To" email address
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid 'To' email address.")
            return redirect('email_compose')

        # Validate CC and BCC email addresses, if provided
        if cc:
            try:
                for cc_email in cc.split(','):
                    validate_email(cc_email.strip())
            except ValidationError:
                messages.error(request, "Invalid CC email address.")
                return redirect('email_compose')

        if bcc:
            try:
                for bcc_email in bcc.split(','):
                    validate_email(bcc_email.strip())
            except ValidationError:
                messages.error(request, "Invalid BCC email address.")
                return redirect('email_compose')

        # Save the email message to the database (ComposeEmail model)
        new_email = ComposeEmail(
            body=message,
            subject=subject,
            recipients=[email] + [cc] + [bcc],  # Combine the email addresses
            sender=request.user.email,
            cc=cc,
            bcc=bcc,
            sent_at=timezone.now(),
            created_by=request.user,
            attachments=file if file else None
        )

        new_email.save()

        # Prepare the email content to send
        email_subject = subject
        email_message = message
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        # Add CC and BCC recipients to the list
        if cc:
            recipient_list.extend([email.strip() for email in cc.split(',')])
        
        if bcc:
            recipient_list.extend([email.strip() for email in bcc.split(',')])

        # Create the email message
        email = EmailMessage(
            email_subject,
            email_message,
            from_email,
            recipient_list
        )

        # Attach the file if provided
        if file:
            email.attach(file.name, file.read(), file.content_type)

        # Send the email
        try:
            email.send()
            # Success message
            messages.success(request, f"Email sent successfully to {', '.join(recipient_list)}")
        except Exception as e:
            # If email fails to send, handle the exception
            messages.error(request, f"Failed to send email. Error: {str(e)}")
            return redirect('email_compose')

        # Redirect to inbox after sending
        return redirect('/email_sentbox/')

    return render(request, "logs/email_compose.html", {
        'user_profile': user_profile,
        'unread_messages_count': unread_messages_count,
    })

@login_required
def email_reply(request, id):
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('/')  # Redirect to the home page
    # Get the user profile for the current logged-in user
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Get the specific Contact message by ID
    contact_message = get_object_or_404(Contact, id=id)

    # Count the number of unread messages
    unread_messages_count = Contact.objects.filter(read=False).count()

    if request.method == "POST":
        # Get form data from POST request
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        reply_message = request.POST.get('message')
        file = request.FILES.get('attachment')

        # Ensure you're passing the correct Contact instance to the reply
        reply = Reply(
            contact=contact_message,  # Correctly assigning the Contact instance
            subject=subject,
            reply_message=reply_message,
            replied_by=request.user.username,
            attachment=file if file else None
        )

        reply.save()

        # Prepare the email content
        email_subject = subject
        email_message = reply_message
        from_email = settings.DEFAULT_FROM_EMAIL  # This is defined in settings.py
        recipient_list = [email]

        # Create the email message
        email = EmailMessage(
            email_subject,  # Subject of the email
            email_message,  # Body of the email
            from_email,  # From email
            recipient_list  # To email addresses
        )

        # Add attachment if it's provided
        if file:
            email.attach(file.name, file.read(), file.content_type)

        # Send the email
        email.send()

        # Display a success message
        messages.success(request, f"Reply Sent Successfully to {contact_message.name}")

        # Redirect to the email inbox after sending the reply
        return redirect('/email_inbox/')

    # Render the email reply template with the necessary context
    return render(request, "logs/email_reply.html", {
        'user_profile': user_profile,
        'unread_messages_count': unread_messages_count,
        'message': contact_message,  # Passing the Contact instance to the template
    })


@login_required
def email_replies(request):
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('/')  # Redirect to the home page
    user_profile = get_object_or_404(UserProfile, user=request.user)
    reply = Reply.objects.all().order_by('-replied_at')
    unread_messages_count = Contact.objects.filter(read=False).count()
    return render(request, "logs/email_replies.html", {
        'user_profile': user_profile,
        'reply': reply,
        'unread_messages_count': unread_messages_count,
    })

@login_required
def read_messages(request):
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('/')  # Redirect to the home page
    user_profile = get_object_or_404(UserProfile, user=request.user)
    messages = Contact.objects.filter(read=True).order_by('-create_at')
    unread_messages_count = Contact.objects.filter(read=False).count()
    return render(request, "logs/read_messages.html", {
        'user_profile': user_profile,
        'messages': messages,
        'unread_messages_count': unread_messages_count,
    })

@login_required
def email_read(request, id):
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('/')  # Redirect to the home page
    messages = Contact.objects.get(id=id)
    messages.read = True
    messages.save()
    user_profile = get_object_or_404(UserProfile, user=request.user)
    unread_messages_count = Contact.objects.filter(read=False).count()
    return render(request, "logs/email_read.html", {
        'user_profile': user_profile,
        'messages': messages,
        'unread_messages_count': unread_messages_count,
    })



@login_required
def g_post_assignment(request):
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        # Extract data from the form
        topic = request.POST['topic']
        link = request.POST['link']
        course_id = request.POST['course_id']

        course = Course.objects.get(id=course_id)
        
        assignment = GoogleFormAssignment(
            link=link,
            course=course,
            title=topic,
            user=user
        )
        assignment.save()
        
        messages.info(request, 'Assignmet created and posted successfully.')
        return redirect('/g_assignment/')  # Redirect to success page after the application is submitted
    
    # Retrieve all available courses to show in the form
    courses = Course.objects.all()
    return render(request, "logs/post_assignment.html", {
        'courses':courses,
        'user_profile':user_profile,
        })

@login_required
def delete_g_assignment(request, id):
    assignment = GoogleFormAssignment.objects.get(id=id)
    assignment.delete()
    return redirect('/view_posted_assignments/')

    
        
    
       

@login_required
def view_posted_assignments(request):
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=request.user)
    print("User is student:", user.is_student)  # Debug statement

    assign = []  # Default value for assignments in case the user is not a teacher
    assignments = []  # Default value in case the user is not a student
    assigns = []  # Default value for admins

    if user.is_teacher:
        # Teacher can see all assignments they posted
        assign = GoogleFormAssignment.objects.filter(user=user)
    elif user.is_admin:
        # Admin can see all assignments
        assigns = GoogleFormAssignment.objects.all()
    elif user.is_student:
        # Get the student instance corresponding to the current user
        student = StudentApp.objects.filter(registration_number=user.username).first()  # Get the first matching student
        print(f"student name is {student}")
        if student:
            # Get the student's course (this is a Course instance)
            student_course = student.course  # This will be a Course instance
            print("Student's course:", student_course.name)  # Debug print
            # Filter assignments based on the student's course
            assignments = GoogleFormAssignment.objects.filter(course=student_course)
            print("Assignments found:", assignments)  # Debug print

    else:
        messages.info(request, "You are not permitted to view this page")
        return redirect('/')

    return render(request, "logs/view_posted_assignments.html", {
        'assign': assign,
        'assignments': assignments,
        'assigns': assigns,
        'user_profile':user_profile,
    })


# View for creating a new note
@login_required
def create_note(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        # Handle the form submission
        title = request.POST.get('title')
        thumbnail = request.FILES.get('thumbnail')
        course_id = request.POST.get('course')
        file = request.FILES.get('file')
        user = request.user  # Assuming the user is logged in

        course = Course.objects.get(id=course_id)
        note = Notes(user=user, title=title, thumbnail=thumbnail, course=course, file=file)
        note.save()

        messages.success(request, f"{title} notes created successfully.")
        return redirect('/create-note/')  # Redirect to a success page

    # Get the list of courses to display in the dropdown
    courses = Course.objects.all()
    return render(request, 'logs/notes.html', {'courses': courses, 'user_profile': user_profile})

@login_required
def view_posted_notes(request):
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=request.user)
    print("User is student:", user.is_student)  # Debug statement

    assign = []  # Default value for assignments in case the user is not a teacher
    assignments = []  # Default value in case the user is not a student
    assigns = []  # Default value for admins

    if user.is_teacher:
        # Teacher can see all assignments they posted
        assign = Notes.objects.filter(user=user)
    elif user.is_admin:
        # Admin can see all assignments
        assigns = Notes.objects.all()
    elif user.is_student:
        # Get the student instance corresponding to the current user
        student = StudentApp.objects.filter(registration_number=user.username).first()  # Get the first matching student
        print(f"student name is {student}")
        if student:
            # Get the student's course (this is a Course instance)
            student_course = student.course  # This will be a Course instance
            print("Student's course:", student_course.name)  # Debug print
            # Filter assignments based on the student's course
            assignments = Notes.objects.filter(course=student_course)
            print("Assignments found:", assignments)  # Debug print

    else:
        messages.info(request, "You are not permitted to view this page")
        return redirect('/')

    return render(request, "logs/view_notes.html", {
        'assign': assign,
        'assignments': assignments,
        'assigns': assigns,
        'user_profile': user_profile,
    })


@login_required
def delete_notes(request, id):
    notes = Notes.objects.get(id=id)
    notes.delete()
    return redirect('/notes/')



# View for creating a new tutorial
@login_required
def create_tutorial(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        # Handle the form submission
        title = request.POST.get('title')
        thumbnail = request.FILES.get('thumbnail')
        course_id = request.POST.get('course')
        video_file = request.FILES.get('video_file')
        user = request.user  # Assuming the user is logged in

        course = Course.objects.get(id=course_id)
        tutorial = Tutorial(user=user, title=title, thumbnail=thumbnail, course=course, video_file=video_file)
        tutorial.save()

        messages.success(request, f"{title} tutorial is posted successfully.")
        messages.info(request, f"post another video if needed.")
        return redirect('/create-tutorial/')  # Redirect to a success page

    # Get the list of courses to display in the dropdown
    courses = Course.objects.all()
    return render(request, 'logs/tutorial.html', {'courses': courses, 'user_profile': user_profile})


@login_required
def view_posted_tutorials(request):
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=user)

    assign = []  # Default value for assignments in case the user is not a teacher
    assignments = []  # Default value in case the user is not a student
    assigns = []  # Default value for admins

    if user.is_teacher:
        # Teacher can see all assignments they posted
        assign = Tutorial.objects.filter(user=user)
    elif user.is_admin:
        # Admin can see all assignments
        assigns = Tutorial.objects.all()
    elif user.is_student:
        # Get the student instance corresponding to the current user
        student = StudentApp.objects.filter(registration_number=user.username).first()  # Get the first matching student
        print(f"student name is {student}")
        if student:
            # Get the student's course (this is a Course instance)
            student_course = student.course  # This will be a Course instance
            print("Student's course:", student_course.name)  # Debug print
            # Filter assignments based on the student's course
            assignments = Tutorial.objects.filter(course=student_course)
            print("Assignments found:", assignments)  # Debug print

    else:
        messages.info(request, "You are not permitted to view this page")
        return redirect('/')

    return render(request, "logs/view_tutorials.html", {
        'assign': assign,
        'assignments': assignments,
        'assigns': assigns,
        'user_profile':user_profile,
    })

@login_required
def delete_tutorial(request, id):
    tut = Tutorial.objects.get(id=id)
    tut.delete()
    return redirect('/tutorial/')

@login_required
def view_departments(request):
    departments = Department.objects.all()
    user_profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'logs/departments.html', {
        'departments':departments,
        'user_profile':user_profile,
        })

@login_required
def delete_course(request, id):
    cos = Course.objects.get(id=id)
    cos.delete()
    return redirect('/courses/')

@login_required
def delete_department(request, id):
    department = Department.objects.get(id=id)
    department.delete()
    return redirect('/departments/')

@login_required
def create_course(request):
    # Get all departments to populate the select box in the form
    departments = Department.objects.filter(is_tution=True)
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        # Get form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        department_id = request.POST.get('department')
        price = request.POST.get('price')
        period_of_study = request.POST.get('duration')  # in months

        # Check if the required fields are provided
        if not department_id:
            messages.error(request, "Please select a department.")
            return redirect('create_course')

        try:
            department = Department.objects.get(id=department_id)  # Get the department by ID
        except Department.DoesNotExist:
            messages.error(request, "Invalid department selected.")
            return redirect('create_course')

        # Create the new course
        course = Course(
            name=title,
            description=description,
            department=department,
            price=price,
            period_of_study=period_of_study
        )

        course.save()  # Save the course

        # Show success message
        messages.success(request, f"Course '{title}' created successfully.")

        return redirect('create_course')  # Redirect to the course creation page

    # Render the form with departments for GET request
    return render(request, "logs/course_update.html", {
        'departments': departments,
        'user_profile':user_profile,
    })


@login_required
def edit_course(request, id):
    # Get all departments to populate the select box in the form
    departments = Department.objects.filter(is_tution=True)
    coss = Course.objects.get(id=id)
    user_profile = get_object_or_404(UserProfile, user=request.user)


    if request.method == "POST":
        # Get form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        department_id = request.POST.get('department')
        price = request.POST.get('price')
        period_of_study = request.POST.get('duration')  # in months

        # Check if the required fields are provided
        if not department_id:
            messages.error(request, "Please select a department.")
            return redirect('create_course')

        try:
            department = Department.objects.get(id=department_id)  # Get the department by ID
        except Department.DoesNotExist:
            messages.error(request, "Invalid department selected.")
            return redirect('/edit_course/<int:id>/')

        coss.name=title
        coss.description=description
        coss.department=department
        coss.price=price
        coss.period_of_study=period_of_study
        coss.save()

        # Show success message
        messages.success(request, f"Course '{title}' edited successfully.")

        return redirect('/courses/')  # Redirect to the course creation page

    # Render the form with departments for GET request
    return render(request, "logs/edit_course.html", {
        'departments': departments,
        'user_profile': user_profile,
        'coss': coss,
    })

def create_department(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method=="POST":
        title = request.POST.get('title')
        is_tution = request.POST.get('is_tution', None)

        if is_tution== 'on':
            is_tution=True
        else:
            is_tution=False

        depart = Department(
            name=title,
            is_tution=is_tution,
        )
        depart.save()

        return redirect('/departments/')
    return render(request, 'logs/create_department.html', {
        'user_profile': user_profile,
    })


def edit_department(request, id):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    department = Department.objects.get(id=id)
    if request.method=="POST":
        title = request.POST.get('title')
        is_tution = request.POST.get('is_tution', None)

        if is_tution== 'on':
            is_tution=True
        else:
            is_tution=False

        department.name = title
        department.is_tution = is_tution
        department.save()

        return redirect('/departments/')
    return render(request, 'logs/edit_department.html', {
        'user_profile': user_profile,
        'department': department,
    })

@login_required
def view_course(request):
    courses = Course.objects.all()
    user_profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'logs/courses.html', {
        'courses':courses,
        'user_profile':user_profile,
        })

@redirect_if_authenticated
def view_cos(request):
    courses = Course.objects.all()
    return render(request, 'logs/cos.html', {
        'courses':courses,
        })

# View to handle course application
@redirect_if_authenticated
def cos_apply(request, id):
    course = Course.objects.get(id=id)
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
            return redirect(f'/techsols/courses/apply/{course_id}/')

        if CustomerUser.objects.filter(email=email).exists():
            messages.warning(request, "The email address provided is already registered")
            return redirect(f'/techsols/courses/apply/{course_id}/')
        
        if UserProfile.objects.filter(phone_number=phone_number).exists():
            messages.warning(request, "The phone_number provided is already registered")
            return redirect(f'/techsols/courses/apply/{course_id}/')

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
    return render(request, 'logs/apply_cos.html', {
        'course':course,
        })

@login_required
def course_details(request, course_id):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    course = Course.objects.get(id=course_id)
    return render(request, 'logs/course_details.html', {
        'course':course,
        'user_profile':user_profile,
        })

@login_required
def all_students(request):
    students = StudentApp.objects.all()
    user_profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'logs/all_students.html', {
        'students':students,
        'user_profile':user_profile,
        })
@login_required
def student_details(request, student_id):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    student = StudentApp.objects.get(id=student_id)
    return render(request, 'logs/student_details.html', {
        'student':student,
        'user_profile':user_profile,
        })
@login_required
def teacher_list(request):
    # Retrieve all teacher objects from the database
    teachers = Teacher.objects.all()
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    # Pass the teachers to the template
    return render(request, 'logs/teachers_list.html', {'teachers': teachers, 'user_profile': user_profile})

@login_required
def fee_payment_view(request):
    """
    View to handle fee payment through M-Pesa.
    """
    # Get the logged-in student's information
    stud = request.user  # Assuming the user is logged in and has a student profile
    student = StudentApp.objects.filter(registration_number=stud).first()
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        # Get the amount and other details from the form
        aamount = request.POST.get('amount')
        fees_payment_for = request.POST.get('fees_payment_for')
        registration_number = request.POST.get('reg_no')
        mode_of_payment = request.POST.get('mode_of_payment')
        phone_number = request.POST.get('phone')

        if amount:
            try:
                # Convert the amount to a Decimal
                amount = Decimal(amount)

                # Create a new FeePayment record
                payment = FeePayment(
                    student=student,
                    amount=aamount,
                    registration_number=registration_number,
                    mode_of_payment=mode_of_payment,
                    fees_payment_for=fees_payment_for,
                    payment_phone_number=phone_number
                )
                payment.save()  # Save the payment record in the database

                # Call M-Pesa API to initiate payment
                payment_response = initiate_stk_push(aamount, phone_number)

                # Check if the payment initiation was successful
                if payment_response.get('status') == 'success':
                    messages.success(request, f"Payment of KSh {amount} was successful! Your remaining balance is KSh {student.remaining_balance}.")
                    return redirect('/auth_access/student_dashboard/')  # Redirect to the student's dashboard or another page

                else:
                    # Handle payment failure
                    messages.warning(request, "M-Pesa payment failed. Please try again later.")
                    return redirect('/fee_payment/')

            except Exception as e:
                # Handle any exceptions during the process (e.g., invalid amount)
                messages.warning(request, f"Error processing payment: {str(e)}")
                return redirect('/fee_payment/')

        else:
            messages.error(request, "Invalid payment amount.")

    return render(request, 'logs/fee_payment.html', {'student': student, 'user_profile': user_profile})

@login_required
def GenerateFeeStatement(request):
    # Get the logged-in user, assuming the user is a student
    student = get_object_or_404(StudentApp, registration_number=request.user)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    # Fetch all payments related to the logged-in student
    payments = FeePayment.objects.filter(student=student)

    context = {
        'payments': payments,
        'user_profile': user_profile,
    }

    return render(request, 'logs/fee_statement.html', context)
    
@login_required
def update_student_bio(request):
    try:
        # Get the StudentApp instance associated with the logged-in user
        student_app = StudentApp.objects.get(stud=request.user)

        # Get the student's bio data
        bio_data = StudentBioData.objects.get(student=student_app)

        if request.method == 'POST':
            # Update the bio data with the form data
            bio_data.date_of_birth = request.POST.get('date_of_birth')
            bio_data.gender = request.POST.get('gender')
            bio_data.address = request.POST.get('address')
            bio_data.nationality = request.POST.get('nationality')
            bio_data.emergency_contact_name = request.POST.get('emergency_contact_name')
            bio_data.emergency_contact_phone = request.POST.get('emergency_contact_phone')
            bio_data.blood_group = request.POST.get('blood_group')
            bio_data.hobbies = request.POST.get('hobbies')

            # Save the updated data to the database
            bio_data.save()

            # Redirect to a success page or the updated bio page
            return redirect('student_dashboard')  # Example redirect to a page showing the student's bio

        # If the method is GET, render the update form
        return render(request, 'logs/update_student_bio.html', {'bio_data': bio_data})

    except StudentApp.DoesNotExist:
        messages.error(request, "StudentApp not found for this user.")
        return render(request, 'logs/update_student_bio.html')

    except StudentBioData.DoesNotExist:
        messages.error(request, "Bio data not found for this student.")
        return redirect('student_dashboard')


from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from io import BytesIO
from django.shortcuts import get_object_or_404



@login_required
def payment_receipt_pdf(request, payment_id):
    # Fetch the specific payment instance by payment_id
    payment = get_object_or_404(FeePayment, id=payment_id)
    student = payment.student
    
    # Ensure that the logged-in user is the student making the payment
    if request.user.username != student.registration_number:  # Assuming StudentApp is connected to the User model
        return HttpResponse('Unauthorized', status=401)
    
    # Create an in-memory buffer to hold the PDF content
    buffer = BytesIO()
    
    # Create a canvas to start writing the PDF content
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Set up the font and style for the PDF
    p.setFont("Helvetica", 12)
    
    # Add header information for the receipt
    p.drawString(220, 750, "Fee Payment Receipt")
    
    # Add payment details to the receipt
    p.drawString(50, 700, f"Student Name: {student.first_name} {student.last_name}")
    p.drawString(50, 680, f"Registration Number: {student.registration_number}")
    p.drawString(50, 660, f"Payment Date: {payment.payment_date.strftime('%d-%m-%Y')}")
    p.drawString(50, 640, f"Amount Paid: ${payment.amount}")
    p.drawString(50, 620, f"Receipt Number: {payment.receipt_number}")
    p.drawString(50, 600, f"Mode of Payment: {payment.mode_of_payment}")
    p.drawString(50, 580, f"Remaining Balance: ${payment.new_remaining_balance}")
    
    # Add a line separator
    p.setStrokeColor(colors.black)
    p.line(50, 570, 550, 570)
    
    # Add a thank you message
    p.drawString(50, 550, "Thank you for your payment!")
    
    # Finalize the PDF page
    p.showPage()
    p.save()
    
    # Move to the beginning of the buffer to prepare it for the response
    buffer.seek(0)
    
    # Create an HTTP response to send the PDF to the browser
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payment_receipt_{payment.receipt_number}.pdf"'
    
    return response



"""
@login_required
def payment_receipt(request, payment_id):
    # Fetch the specific payment instance by payment_id
    payment = get_object_or_404(FeePayment, id=payment_id)
    student = payment.student
    
    # Ensure that the logged-in user is the student making the payment
    if request.user.username != student.registration_number:  # Assuming StudentApp is connected to the User model
        return HttpResponse('Unauthorized', status=401)
    
    # Prepare context data for rendering the HTML page
    context = {
        'student': student,
        'payment': payment,
    }
    
    # Render the HTML template for the receipt
    return render(request, 'logs/payment_receipt.html', context)

from weasyprint import HTML
from django.template.loader import render_to_string
from django.http import HttpResponse

@login_required
def payment_receipt_pdf(request, payment_id):
    # Fetch the specific payment instance by payment_id
    payment = get_object_or_404(FeePayment, id=payment_id)
    student = payment.student
    
    # Ensure that the logged-in user is the student making the payment
    if request.user.username != student.registration_number:
        return HttpResponse('Unauthorized', status=401)
    
    # Prepare context data for rendering the HTML page
    context = {
        'student': student,
        'payment': payment,
    }
    
    # Render the receipt HTML content
    html_content = render_to_string('payment_receipt.html', context)
    
    # Generate PDF from HTML content using WeasyPrint
    pdf = HTML(string=html_content).write_pdf()
    
    # Create an HTTP response to send the PDF to the browser
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payment_receipt_{payment.receipt_number}.pdf"'
    
    return response
"""

@login_required
def create_quiz(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    # Check if user is admin or teacher
    if not (request.user.is_admin or request.user.is_teacher):
        messages.error(request, "You don't have permission to create a quiz.")
        return redirect('home')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        course_id = request.POST.get('course')
        is_exam = request.POST.get('is_exam') == 'on'
        
        # Validate title and course
        if not title or not course_id:
            messages.error(request, "Both title and course are required.")
            return redirect('create_quiz')

        course = get_object_or_404(Course, id=course_id)

        # Create the Quiz
        quiz = Quiz.objects.create(
            title=title,
            course=course,
            teacher=request.user.first_name,
            is_exam=is_exam
        )
        
        messages.success(request, "Quiz created! You can now add questions.")
        return redirect('add_questions', quiz_id=quiz.id)

    courses = Course.objects.all()
    return render(request, 'logs/create_quiz.html', {'courses': courses, 'user_profile': user_profile,})

@login_required
def add_questions(request, quiz_id):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if not (request.user.is_admin or request.user.is_teacher):
        messages.error(request, "You don't have permission to create a quiz.")
        return redirect('home')

    if request.method == 'POST':
        question_text = request.POST.get('question_text', '').strip()
        total_marks = request.POST.get('total_marks', '').strip()
        correct_answer_index = request.POST.get('correct_answer')  # Get selected correct answer index

        # Validate question text and total marks
        if not question_text or not total_marks:
            messages.error(request, "Question text and total marks are required.")
            return redirect('add_questions', quiz_id=quiz.id)

        try:
            total_marks = int(total_marks)
        except ValueError:
            messages.error(request, "Total marks must be a valid integer.")
            return redirect('add_questions', quiz_id=quiz.id)

        # Ensure a correct answer is selected
        if correct_answer_index is None:
            messages.error(request, "You must select the correct answer.")
            return redirect('add_questions', quiz_id=quiz.id)

        # Create the Question instance
        question = Question.objects.create(
            quiz=quiz,
            text=question_text,
            total_marks=total_marks
        )

        # Process and create Answers
        for ans_idx in range(4):  # Process up to 4 answers
            ans_text = request.POST.get(f'answers_{ans_idx}_text', '').strip()
            is_correct = str(ans_idx) == correct_answer_index  # Check if this is the correct answer

            if ans_text:  # Only create Answer if text is provided
                Answer.objects.create(
                    question=question,
                    text=ans_text,
                    is_correct=is_correct
                )

        messages.success(request, "Question and answers added successfully!")
        messages.info(request, "You can add another question if needed.")
        return redirect('add_questions', quiz_id=quiz.id)

    return render(request, 'logs/add_questions.html', {'quiz': quiz, 'user_profile': user_profile,})

@login_required
def quiz_list(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    quizzes = []

    if not (request.user.is_admin or request.user.is_teacher or request.user.is_student):
        messages.error(request, "You don't have permission to view this page.")
        return redirect('home')
    if request.user.is_student:
        student = StudentApp.objects.filter(registration_number=request.user).first()  # Get the first matching student
        print(f"student name is {student}")
        if student:
            # Get the student's course (this is a Course instance)
            student_course = student.course  # This will be a Course instance
            print("Student's course:", student_course.name)  # Debug print
            # Filter quizzes based on the student's course
            quizzes = Quiz.objects.filter(course=student_course)
            print("quizzes found:", quizzes)  # Debug print
    elif request.user.is_admin:
        # Admin can see all assignments
        quizzes = Quiz.objects.all()

    elif request.user.is_teacher:
        # Teacher can see all assignments they posted
        quizzes = Quiz.objects.filter(teacher=request.user)

    else:
        messages.info(request, "You are not permitted to view this page")
        return redirect('/')
    return render(request, 'logs/quiz_list.html', {'quizzes': quizzes, 'user_profile': user_profile,})

@login_required
def delete_quiz(request, id):
    q = Quiz.objects.get(id=id)
    q.delete()
    return redirect('/quiz_list/')

@login_required
def take_quiz(request, quiz_id):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    quiz = get_object_or_404(Quiz, id=quiz_id)
    student = request.user

    attempt_count = QuizAttempt.objects.filter(student=student.id, quiz=quiz).count()

    if not request.user.is_student:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('home')
    
    if attempt_count >= 1:
        messages.error(request, "One Attemp Only Per Quiz.")
        return redirect('/quiz_list/')

    if request.method == 'POST':
        correct_answers = 0
        for question in quiz.questions.all():
            selected_answers = request.POST.getlist(f'question_{question.id}')
            correct_answers_for_question = Answer.objects.filter(
                question=question, is_correct=True
            ).values_list('text', flat=True)

            if set(selected_answers) == set(correct_answers_for_question):
                correct_answers += 1

        score = (correct_answers / quiz.questions.count()) * 100
        
        QuizAttempt.objects.create(
            student=student,
            registration_number=request.user.username,
            quiz=quiz,
            score=score,
            attempt_number=attempt_count + 1
        )

        return render(request, 'logs/quiz_result.html', {'score': score})
    
    return render(request, 'logs/take_quiz.html', {'quiz': quiz, 'user_profile': user_profile,})

@login_required
def quiz_result(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    attempts = QuizAttempt.objects.filter(registration_number=request.user).last()
    return render(request, 'logs/quiz_result.html', {'attempts': attempts, 'user_profile': user_profile,})

@login_required
def results(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    student = StudentApp.objects.filter(registration_number=request.user.username).first()
    print(f'student {student}')

    if student:
        attempts = QuizAttempt.objects.filter(registration_number=student.registration_number)
        print(f'results {attempts}')
    return render(request, 'logs/results.html', {'attempts': attempts, 'user_profile': user_profile,})



@login_required
def edit_quiz(request, quiz_id):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Ensure that the user has permission to edit the quiz (either admin or the teacher who created it)
    if not (request.user.is_admin or request.user.is_teacher):
        messages.error(request, "You don't have permission to edit this quiz.")
        return redirect('home')

    if request.method == 'POST':
        title = request.POST.get('title')
        course_id = request.POST.get('course')
        is_exam = request.POST.get('is_exam') == 'on'

        # Fetch the associated course object
        course = get_object_or_404(Course, id=course_id)

        # Update the quiz details
        quiz.title = title
        quiz.course = course
        quiz.teacher = request.user.first_name
        quiz.is_exam = is_exam
        quiz.save()

        messages.success(request, "Quiz updated successfully!")

        # Check if there are any questions for this quiz, and redirect to the first question
        first_question = quiz.questions.first()

        if first_question:
            # If there is at least one question, redirect to edit that question
            return redirect('edit_question', question_id=first_question.id)
        else:
            # If there are no questions, redirect to the page where they can add questions
            return redirect('add_questions', quiz_id=quiz.id)

    # Fetch all available courses to display in the form
    courses = Course.objects.all()
    return render(request, 'logs/edit_quiz.html', {'quiz': quiz, 'courses': courses, 'user_profile': user_profile,})

@login_required
def edit_question(request, question_id):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    question = get_object_or_404(Question, id=question_id)

    # Ensure user has permission to edit (admin or quiz creator)
    if not (request.user.is_admin or request.user.is_teacher):
        messages.error(request, "You don't have permission to edit this quiz.")
        return redirect('home')

    answers = list(question.answers.all())  # Fetch all related answers

    if request.method == 'POST':
        question_text = request.POST.get('question_text', '').strip()
        total_marks = request.POST.get('total_marks', '').strip()
        correct_answer_id = request.POST.get('correct_answer')  # Correct answer ID

        if not question_text or not total_marks:
            messages.error(request, "Question text and total marks are required.")
            return redirect('edit_question', question_id=question.id)

        # Update question details
        question.text = question_text
        question.total_marks = int(total_marks)
        question.save()

        # Update answers
        for idx, answer in enumerate(answers):
            ans_text = request.POST.get(f'answers_{idx}_text', '').strip()
            
            if not ans_text:
                messages.error(request, f"Answer {idx + 1} text cannot be empty.")
                return redirect('edit_question', question_id=question.id)

            answer.text = ans_text
            answer.is_correct = (str(answer.id) == correct_answer_id)  # Set correct answer
            answer.save()

        messages.success(request, "Question and answers updated successfully!")

        # Redirect to next question or quiz summary
        next_question = question.quiz.questions.filter(id__gt=question.id).first()
        if next_question:
            return redirect('edit_question', question_id=next_question.id)
        else:
            return redirect('/quiz_list/')  # Adjust the redirect as needed

    return render(request, 'logs/edit_question.html', {'question': question, 'answers': answers, 'user_profile': user_profile})
