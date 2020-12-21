# Django timescaledb

A database backend for Timescaledb.

Based on [gist](https://gist.github.com/dedsm/fc74f04eb70d78459ff0847ef16f2e7a) from WeRiot.


## Quick start

1. Install via pip

```bash
pip install django-timescaledb
```

2. Use as DATABASE engine in settings.py:

```python
DATABASES = {
    'default': {
        'ENGINE': 'timescale',
        ...
    },
}
```

3. Use TimescaleDateTimeField in your models. A [hypertable](https://docs.timescale.com/latest/using-timescaledb/hypertables#react-docs) will automatically be created.

```python
from timescale.fields import TimescaleDateTimeField

class SensorLog(models.Model):
   date = TimescaleDateTimeField(interval="1 day")
   value = models.IntegerField()

```
### Reading Data

"TimescaleDB hypertables are designed to behave in the same manner as PostgreSQL database tables for reading data, using standard SQL commands."

We can use any Django ORM methods, expressions or functions to build

#### Time Bucket

TimescaleDB's time_bucket acts as a more powerful version of the PostgreSQL function date_trunc. It accepts arbitrary time intervals as well as optional offsets and returns the bucket start time.

In SQL this can be written as such:

```sql

SELECT time_bucket('1 hour', time) AS bucket, avg(cpu)
  FROM metrics_metric
  GROUP BY bucket
  ORDER BY bucket DESC LIMIT 12;

```

We have abstracted this into a Django expression, to make the same query using the Django ORM would look like this:

```python

Metric.objects.all().values(five_min=TimeBucket("time", "1 hour")).annotate(avg_cpu=Avg("cpu"))

```


### Custom DB backend

Use a custom PostgreSQL db backend like PostGIS.

```python
# Configure via settings.py

TIMESCALE_DB_BACKEND_BASE = "django.contrib.gis.db.backends.postgis"
```
