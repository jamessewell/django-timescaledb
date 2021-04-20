from django.db import models
from timescale.db.models.fields import TimescaleDateTimeField
from typing import Dict

from timescale.db.models.models import TimescaleModel
from timescale.db.models.managers import TimescaleManager




# Create your models here.
class Metric(models.Model):
    time = TimescaleDateTimeField(interval="1 day")
    temperature = models.FloatField(default=0.0)
    device = models.IntegerField(default=0)

    objects = models.Manager()
    timescale = TimescaleManager()


class AnotherMetricFromTimeScaleModel(TimescaleModel):
    value = models.FloatField(default=0.0)
