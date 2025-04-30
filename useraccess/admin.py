from django.contrib import admin
from .models import UserProfile, CustomerUser, Student, Department, Course, StudentApp, Unit, CAT, Practical

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(CustomerUser)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Department)
admin.site.register(StudentApp)
admin.site.register(Unit)
admin.site.register(CAT)
admin.site.register(Practical)
