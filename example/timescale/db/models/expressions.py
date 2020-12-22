from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.functions.mixins import (
    FixDurationInputMixin, NumericOutputFieldMixin,
)


class TimeBucket(models.Func):
    function = 'time_bucket'
    name = "time_bucket"

    def __init__(self, expression, interval):
        if not isinstance(interval, models.Value):
            interval = models.Value(interval)
        super().__init__(interval, expression)


class Histogram(models.Aggregate):
    function = 'histogram'
    name = 'histogram'
    output_field = ArrayField(models.FloatField())

    def __init__(self, expression, min_value, max_value, bucket):
        super().__init__(expression, min_value, max_value, bucket)

