# Generated by Django 5.1.6 on 2025-04-14 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop_profile", "0004_shopnotification"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shopworker",
            name="experience",
            field=models.FloatField(help_text="Experience in years"),
        ),
    ]
