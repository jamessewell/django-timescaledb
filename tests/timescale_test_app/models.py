from django.db import models
from timescale.db import models as tsdb

# Create your models here.


class Sensor(models.Model):
    time = tsdb.TimescaleDateTimeField(interval="1 day")
    temperature = models.FloatField(default=0.0)