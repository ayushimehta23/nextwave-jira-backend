# Generated by Django 5.1.6 on 2025-03-08 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jira_app', '0005_task_priority'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='text',
            new_name='content',
        ),
        migrations.AddField(
            model_name='task',
            name='deadline',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
