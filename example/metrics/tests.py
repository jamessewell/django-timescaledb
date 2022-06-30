from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.expressions import TimeBucketNG
from metrics.models import Metric
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.db.models import Avg
from timescale.db.models.aggregates import First


class TimescaleDBTests(TestCase):
    def setUp(self):
        super().setUp()

    def test_time_bucket_ng(self):
        timestamp = timezone.now().replace(day=1)

        # datapoints for current month
        Metric.objects.create(time=timestamp - relativedelta(days=15), temperature=8)
        Metric.objects.create(time=timestamp - relativedelta(days=10), temperature=10)

        # datapoints for last month
        Metric.objects.create(time=timestamp - relativedelta(months=1, days=15), temperature=14)
        Metric.objects.create(time=timestamp - relativedelta(months=1, days=10), temperature=12)

        # get all metrics, monthly aggregated
        metrics = Metric.timescale.time_bucket_ng('time', '1 month').annotate(Avg('temperature'))

        # verify
        self.assertEqual(metrics[0]["temperature__avg"], 9.0)
        self.assertEqual(metrics[1]["temperature__avg"], 13.0)

        # get first entry of the monthly aggregated datapoints
        metrics = (Metric.timescale
                   .values(interval_end=TimeBucketNG('time', f'1 month', output_field=TimescaleDateTimeField(interval='1 month')))
                   .annotate(temperature__first=First('temperature', 'time')))

        # verify
        # XXX: Remove
        self.assertEqual(metrics[0]["temperature__first"], 14.0)
        self.assertEqual(metrics[1]["temperature__first"], 8.0)
        
