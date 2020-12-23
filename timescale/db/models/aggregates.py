from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.fields import FloatField


class Histogram(models.Aggregate):
    """
    Implementation of the histogram function from Timescale. 

    Read more about it here - https://docs.timescale.com/latest/using-timescaledb/reading-data#histogram

    Response:

    <TimescaleQuerySet [{'histogram': [0, 0, 0, 87, 93, 125, 99, 59, 0, 0, 0, 0], 'device__count': 463}]>

    """
    function = 'histogram'
    name = 'histogram'
    output_field = ArrayField(models.FloatField())

    def __init__(self, expression, min_value, max_value, bucket):
        super().__init__(expression, min_value, max_value, bucket)


class Last(models.Aggregate):
    function = 'last'
    name = 'last'
    output_field = FloatField()

    def __init__(self, expression, bucket):
        super().__init__(expression, bucket)


class First(models.Aggregate):
    function = 'first'
    name = 'first'
    output_field = FloatField()

    def __init__(self, expression, bucket):
        super().__init__(expression, bucket)