from django.contrib import admin

from .models import FeePayment, SiteLogo, GoogleFormAssignment, Notes, Tutorial, Quiz, Question, Answer, QuizAttempt,Contact, Reply, Forward, ComposeEmail, Event, Blog, News, Slider


# Register your models here.
admin.site.register(FeePayment)
admin.site.register(GoogleFormAssignment)
admin.site.register(Notes)
admin.site.register(Tutorial)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QuizAttempt)
admin.site.register(Contact)
admin.site.register(Reply)
admin.site.register(Forward)
admin.site.register(ComposeEmail)
admin.site.register(Event)
admin.site.register(Blog)
admin.site.register(News)
admin.site.register(Slider)
admin.site.register(SiteLogo)