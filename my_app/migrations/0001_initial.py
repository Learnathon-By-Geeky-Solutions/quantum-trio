<<<<<<< HEAD:my_app/migrations/0001_initial.py
# Generated by Django 5.1.6 on 2025-03-03 09:29
=======
# Generated by Django 5.1.5 on 2025-03-03 08:39
>>>>>>> 47361a3b9f061c1c0fd6ebe06d18c1df9252f2bc:myApp/migrations/0001_initial.py

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Division',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='District',
            fields=[
<<<<<<< HEAD:my_app/migrations/0001_initial.py
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "division",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="districts",
                        to="my_app.division",
                    ),
                ),
=======
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('division', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='districts', to='myApp.division')),
>>>>>>> 47361a3b9f061c1c0fd6ebe06d18c1df9252f2bc:myApp/migrations/0001_initial.py
            ],
        ),
        migrations.CreateModel(
            name='Landmark',
            fields=[
<<<<<<< HEAD:my_app/migrations/0001_initial.py
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
                (
                    "area",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="landmarks",
                        to="my_app.area",
                    ),
                ),
=======
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='landmarks', to='myApp.area')),
>>>>>>> 47361a3b9f061c1c0fd6ebe06d18c1df9252f2bc:myApp/migrations/0001_initial.py
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
<<<<<<< HEAD:my_app/migrations/0001_initial.py
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "item_description",
                    models.CharField(blank=True, max_length=800, null=True),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="my_app.service",
                    ),
                ),
=======
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('item_description', models.CharField(blank=True, max_length=800, null=True)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='myApp.service')),
>>>>>>> 47361a3b9f061c1c0fd6ebe06d18c1df9252f2bc:myApp/migrations/0001_initial.py
            ],
        ),
        migrations.CreateModel(
            name='Upazilla',
            fields=[
<<<<<<< HEAD:my_app/migrations/0001_initial.py
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "district",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="upazillas",
                        to="my_app.district",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="area",
            name="upazilla",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="areas",
                to="my_app.upazilla",
            ),
=======
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='upazillas', to='myApp.district')),
            ],
        ),
        migrations.AddField(
            model_name='area',
            name='upazilla',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='areas', to='myApp.upazilla'),
>>>>>>> 47361a3b9f061c1c0fd6ebe06d18c1df9252f2bc:myApp/migrations/0001_initial.py
        ),
    ]
