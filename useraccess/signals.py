from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import UserProfile, CustomerUser, StudentApp, CAT, CATScore, Teacher
from django.db import transaction


@receiver(post_save, sender=CustomerUser)
def create_student_app(sender, instance, created, **kwargs):
    if created and instance.is_student is True:
        # Prevent duplicate creation if StudentApp already exists
        if not hasattr(instance, 'studentapp'):
            student_app = StudentApp.objects.create(stud=instance)

            # Save to generate registration_number
            student_app.save()

            # Set user's username to match the registration number
            instance.username = student_app.registration_number
            instance.save(update_fields=['username'])

            # Send confirmation email
            student_app.send_confirmation_email(instance)

@receiver(post_save, sender=CustomerUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Only create UserProfile for new users
        UserProfile.objects.create(user=instance)
    else:
        # If the user is being updated, handle accordingly
        instance.userprofile.save()

@receiver(pre_delete, sender=CustomerUser)
def delete_student_application(sender, instance, **kwargs):
    try:
        # Use the username of the instance to search for the related StudentApplication
        student_application = StudentApp.objects.get(registration_number=instance.username)
        student_application.delete()  # Delete the associated StudentApplication
        print(f"Deleted StudentApplication for {instance.username}")

    except StudentApp.DoesNotExist:
        print(f"No StudentApplication found for {instance.username}")
        # If no associated StudentApplication exists, do nothing

@receiver(pre_delete, sender=CustomerUser)
def delete_teacher_application(sender, instance, **kwargs):
    try:
        # Use the username of the instance to search for the related StudentApplication
        teacher_application = Teacher.objects.get(staff_number=instance.username)
        teacher_application.delete()  # Delete the associated StudentApplication
        print(f"Deleted TeacherApplication for {instance.username}")

    except Teacher.DoesNotExist:
        print(f"No TeacherApplication found for {instance.username}")
        # If no associated TeacherApplication exists, do nothing

@receiver(post_save, sender=StudentApp)
def create_cat_scores_for_new_student(sender, instance, created, **kwargs):
    if created:
        # Find all CATs in units under this student's course
        cats = CAT.objects.filter(unit__course=instance.course)
        for cat in cats:
            CATScore.objects.get_or_create(cat=cat, student=instance)

            

@receiver(post_save, sender=CAT)
def create_cat_scores_for_students(sender, instance, created, **kwargs):
    if created:
        students = StudentApp.objects.filter(course=instance.unit.course)
        for student in students:
            CATScore.objects.get_or_create(
                cat=instance,
                student=student
            )