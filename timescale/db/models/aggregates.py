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


class LTTB(models.Func):
    function = 'lttb'
    name = 'lttb'
    output_field = models.DateTimeField()

    def __init__(self, time, value, count, field):
        self.fieldname = field
        super().__init__(time, value, count)

    def as_sql(self, compiler, connection, **extra_context):
        sql, params = super().as_sql(compiler, connection, **extra_context)
        return f'(unnest({sql})).{self.fieldname}', params


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