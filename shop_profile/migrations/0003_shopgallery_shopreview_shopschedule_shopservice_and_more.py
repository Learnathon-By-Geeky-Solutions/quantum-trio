# Generated by Django 5.1.6 on 2025-02-26 17:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myApp", "0001_initial"),
        ("shop_profile", "0002_remove_myuser_date_of_birth_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShopGallery",
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
                (
                    "image",
                    models.ImageField(blank=True, null=True, upload_to="ShopGallery/"),
                ),
                (
                    "description",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "shop",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shopgallery",
                        to="shop_profile.shopprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ShopReview",
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
                ("rating", models.PositiveIntegerField(default=1)),
                ("review", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "shop",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shopreview",
                        to="shop_profile.shopprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ShopSchedule",
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
                (
                    "day_of_week",
                    models.CharField(
                        choices=[
                            ("Sunday", "Sunday"),
                            ("Monday", "Monday"),
                            ("Tuesday", "Tuesday"),
                            ("Wednesday", "Wednesday"),
                            ("Thursday", "Thursday"),
                            ("Friday", "Friday"),
                            ("Saturday", "Saturday"),
                        ],
                        max_length=10,
                    ),
                ),
                ("start", models.TimeField()),
                ("end", models.TimeField()),
                (
                    "shop",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shopschedule",
                        to="shop_profile.shopprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ShopService",
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
                (
                    "price",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shopservices",
                        to="myApp.item",
                    ),
                ),
                (
                    "shop",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shopservice",
                        to="shop_profile.shopprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ShopWorker",
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
                ("name", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=15)),
                (
                    "profile_pic",
                    models.ImageField(blank=True, null=True, upload_to="ShopWorker/"),
                ),
                (
                    "experience",
                    models.PositiveIntegerField(help_text="Experience in years"),
                ),
                (
                    "expertise",
                    models.ManyToManyField(
                        blank=True, related_name="experts", to="myApp.item"
                    ),
                ),
                (
                    "shop",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shopworker",
                        to="shop_profile.shopprofile",
                    ),
                ),
            ],
        ),
    ]
