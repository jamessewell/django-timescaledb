Django timescaledb
==================

A database backend for Timescaledb.

Based on
`gist <https://gist.github.com/dedsm/fc74f04eb70d78459ff0847ef16f2e7a>`__
from WeRiot.


Quick start
-----------

1. Install via pip

::

    pip install django-timescaledb

2. Use as DATABASE engine in settings.py:

.. code:: python

        DATABASES = {
        'default': {
            'ENGINE': 'timescale',
            ...
        },
    }

3. Use TimescaleDateTimeField in your models. A
   `hypertable <https://docs.timescale.com/latest/using-timescaledb/hypertables#react-docs>`__
   will automatically be created.

.. code:: python

    from timescale.fields import TimescaleDateTimeField

    class SensorLog(models.Model):
       date = TimescaleDateTimeField(interval="1 day")
       value = models.IntegerField()

Custom DB backend
~~~~~~~~~~~~~~~~~

Use a custom PostgreSQL db backend like PostGIS.

.. code:: python

    # Configure via settings.py

    TIMESCALE_DB_BACKEND_BASE = "django.contrib.gis.db.backends.postgis"

