# Generated by Django 5.1.6 on 2025-02-22 18:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_profile", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user_profile",
            options={},
        ),
        migrations.AlterModelManagers(
            name="user_profile",
            managers=[],
        ),
        migrations.RemoveField(
            model_name="user_profile",
            name="date_joined",
        ),
        migrations.RemoveField(
            model_name="user_profile",
            name="first_name",
        ),
        migrations.RemoveField(
            model_name="user_profile",
            name="groups",
        ),
        migrations.RemoveField(
            model_name="user_profile",
            name="last_login",
        ),
        migrations.RemoveField(
            model_name="user_profile",
            name="last_name",
        ),
        migrations.RemoveField(
            model_name="user_profile",
            name="user_permissions",
        ),
        migrations.AddField(
            model_name="user_profile",
            name="date_of_birth",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="user_profile",
            name="profile_picture",
            field=models.ImageField(
                blank=True, null=True, upload_to="profile_pictures/"
            ),
        ),
        migrations.AddField(
            model_name="user_profile",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="user_profile",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name="user_profile",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="user_profile",
            name="is_staff",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="user_profile",
            name="is_superuser",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="user_profile",
            name="password",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="user_profile",
            name="username",
            field=models.CharField(max_length=150, unique=True),
        ),
    ]
