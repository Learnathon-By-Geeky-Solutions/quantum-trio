# Generated by Django 5.1.6 on 2025-04-02 18:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shop_profile", "0003_shopprofile_shop_picture"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShopNotification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("message", models.TextField()),
                (
                    "notification_type",
                    models.CharField(
                        choices=[
                            ("booking", "Booking"),
                            ("payment", "Payment"),
                            ("message", "Message"),
                            ("general", "General"),
                        ],
                        default="general",
                        max_length=10,
                    ),
                ),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "shop",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="shop_profile.shopprofile",
                    ),
                ),
            ],
        ),
    ]
