from django.db import models
from django.db.models.aggregates import Aggregate
from django.db.models.functions.mixins import (
    FixDurationInputMixin, NumericOutputFieldMixin,
)


class TimeBucket(models.Func):
    function = 'time_bucket'

    def __init__(self, expression, interval):
        if not isinstance(interval, models.Value):
            interval = models.Value(interval)
        super().__init__(interval, expression)


class Bucket(NumericOutputFieldMixin, Aggregate):
    function = 'time_bucket'
    allow_distinct = True

    def __init__(self, expression, interval):
        if not isinstance(interval, models.Value):
            interval = models.Value(interval)
        super().__init__(interval, expression)