# Generated by Django 5.1.6 on 2025-04-14 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "user_profile",
            "0002_alter_userprofile_gender_alter_userprofile_latitude_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="latitude",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="longitude",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
