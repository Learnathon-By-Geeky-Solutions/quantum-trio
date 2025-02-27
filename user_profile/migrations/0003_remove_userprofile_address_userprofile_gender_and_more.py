# Generated by Django 5.1.6 on 2025-02-27 15:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_profile", "0002_rename_username_userprofile_first_name_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="address",
        ),
        migrations.AddField(
            model_name="userprofile",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="latitude",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="longitude",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="user_area",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="user_city",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="user_state",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
