# Generated by Django 4.2.5 on 2024-01-04 13:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("task_manager", "0002_alter_task_project"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="status",
            field=models.CharField(
                choices=[
                    ("new", "New"),
                    ("progress", "In progress"),
                    ("blocked", "Blocked"),
                    ("review", "Under review"),
                    ("completed", "Completed"),
                    ("cancelled", "Cancelled"),
                ],
                default="new",
                max_length=255,
            ),
        ),
    ]
