# Generated by Django 5.1.4 on 2024-12-24 13:36

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Datalogger",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Location",
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
                ("lat", models.FloatField()),
                ("lng", models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name="Measurement",
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
                    "label",
                    models.CharField(
                        choices=[
                            ("temp", "Temperature"),
                            ("rain", "Rain"),
                            ("hum", "Humidity"),
                        ],
                        max_length=4,
                    ),
                ),
                ("value", models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name="DataRecord",
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
                ("at", models.DateTimeField()),
                (
                    "datalogger",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="test_weenat.datalogger",
                    ),
                ),
                (
                    "location",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="test_weenat.location",
                    ),
                ),
                ("measurements", models.ManyToManyField(to="test_weenat.measurement")),
            ],
        ),
    ]
