from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import UserProfile, CustomerUser, StudentApp


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