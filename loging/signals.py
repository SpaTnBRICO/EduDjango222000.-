from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from useraccess.models import StudentApp
#from .models import StudentBioData

"""
@receiver(post_save, sender=StudentApp)
def create_student_bio_data(sender, instance, created, **kwargs):
    if created:
        # Only create StudentBioData for new students
        StudentBioData.objects.create(student=instance)
    else:
        # If the user is being updated, handle accordingly
        instance.bio_data.save()

"""


