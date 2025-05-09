# Generated by Django 5.2 on 2025-05-05 18:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('loging', '0001_initial'),
        ('useraccess', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='composeemail',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='feepayment',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='useraccess.studentapp'),
        ),
        migrations.AddField(
            model_name='forward',
            name='contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='forwards', to='loging.contact'),
        ),
        migrations.AddField(
            model_name='googleformassignment',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='useraccess.course'),
        ),
        migrations.AddField(
            model_name='googleformassignment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='googleform', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notes',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='useraccess.course'),
        ),
        migrations.AddField(
            model_name='notes',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='loging.question'),
        ),
        migrations.AddField(
            model_name='quiz',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quizzes', to='useraccess.course'),
        ),
        migrations.AddField(
            model_name='question',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='loging.quiz'),
        ),
        migrations.AddField(
            model_name='quizattempt',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loging.quiz'),
        ),
        migrations.AddField(
            model_name='quizattempt',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='reply',
            name='contact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='loging.contact'),
        ),
        migrations.AddField(
            model_name='tutorial',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='useraccess.course'),
        ),
        migrations.AddField(
            model_name='tutorial',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutorials', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='quizattempt',
            unique_together={('student', 'quiz', 'attempt_number')},
        ),
    ]
