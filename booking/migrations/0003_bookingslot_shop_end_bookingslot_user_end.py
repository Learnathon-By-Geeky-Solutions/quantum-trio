# Generated by Django 5.1.6 on 2025-04-03 06:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("booking", "0002_alter_bookingslot_notes"),
    ]

    operations = [
        migrations.AddField(
            model_name="bookingslot",
            name="shop_end",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="bookingslot",
            name="user_end",
            field=models.BooleanField(default=False),
        ),
    ]
