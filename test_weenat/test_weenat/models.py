from django.db import models
import uuid

class Datalogger(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Location(models.Model):
    lat = models.FloatField()
    lng = models.FloatField()


class Measurement(models.Model):
    LABEL_CHOICES = [
        ('temp', 'Temperature'),
        ('rain', 'Rain'),
        ('hum', 'Humidity'),
    ]
    label = models.CharField(max_length=4, choices=LABEL_CHOICES)
    value = models.FloatField()


class DataRecord(models.Model):
    at = models.DateTimeField()
    datalogger = models.ForeignKey(Datalogger, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    measurements = models.ManyToManyField(Measurement)
