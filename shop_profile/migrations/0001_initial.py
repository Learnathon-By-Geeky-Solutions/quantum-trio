# Generated by Django 5.1.5 on 2025-03-03 10:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('my_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('user_type', models.CharField(choices=[('user', 'User'), ('shop', 'Shop Owner'), ('admin', 'Admin')], default='user', max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ShopProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shop_name', models.CharField(max_length=255)),
                ('shop_title', models.CharField(blank=True, max_length=255, null=True)),
                ('shop_info', models.TextField(blank=True, null=True)),
                ('shop_rating', models.DecimalField(decimal_places=2, default=0.0, max_digits=3)),
                ('shop_owner', models.CharField(blank=True, max_length=255, null=True)),
                ('shop_customer_count', models.IntegerField(default=0)),
                ('gender', models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10, null=True)),
                ('status', models.BooleanField(default=True)),
                ('mobile_number', models.CharField(blank=True, max_length=15, null=True)),
                ('shop_website', models.URLField(blank=True, null=True)),
                ('shop_state', models.CharField(blank=True, max_length=100, null=True)),
                ('shop_city', models.CharField(blank=True, max_length=100, null=True)),
                ('shop_area', models.CharField(blank=True, max_length=100, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('shop_landmark_1', models.CharField(blank=True, max_length=255, null=True)),
                ('shop_landmark_2', models.CharField(blank=True, max_length=255, null=True)),
                ('shop_landmark_3', models.CharField(blank=True, max_length=255, null=True)),
                ('shop_landmark_4', models.CharField(blank=True, max_length=255, null=True)),
                ('shop_landmark_5', models.CharField(blank=True, max_length=255, null=True)),
                ('member_since', models.DateField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='shop_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ShopGallery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='ShopGallery/')),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopgallery', to='shop_profile.shopprofile')),
            ],
        ),
        migrations.CreateModel(
            name='ShopReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(default=1)),
                ('review', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopreview', to='shop_profile.shopprofile')),
            ],
        ),
        migrations.CreateModel(
            name='ShopSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.CharField(choices=[('Sunday', 'Sunday'), ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday')], max_length=10)),
                ('start', models.TimeField()),
                ('end', models.TimeField()),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopschedule', to='shop_profile.shopprofile')),
            ],
        ),
        migrations.CreateModel(
            name='ShopService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopservices', to='my_app.item')),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopservice', to='shop_profile.shopprofile')),
            ],
        ),
        migrations.CreateModel(
            name='ShopWorker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=15)),
                ('profile_pic', models.ImageField(blank=True, null=True, upload_to='ShopWorker/')),
                ('experience', models.PositiveIntegerField(help_text='Experience in years')),
                ('rating', models.DecimalField(decimal_places=2, default=0.0, max_digits=3)),
                ('expertise', models.ManyToManyField(blank=True, related_name='experts', to='my_app.item')),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopworker', to='shop_profile.shopprofile')),
            ],
        ),
    ]
