# Generated by Django 5.1.6 on 2025-03-02 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jira_app', '0004_remove_task_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='priority',
            field=models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium', max_length=10),
        ),
    ]
