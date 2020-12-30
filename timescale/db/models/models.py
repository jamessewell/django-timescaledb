from django.db import models
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager


class TimescaleModel(models.Model):
    """
    A helper class for using Timescale within Django, has the TimescaleManager and 
    TimescaleDateTimeField already present. This is an abstract class it should 
    be inheritted by another class for use.
    """
    time = TimescaleDateTimeField(interval="1 day")

    objects = models.Manager()
    timescale = TimescaleManager()
    

    class Meta:
        abstract = True