"""
Tests for TimescaleDB retention and compression policies.
"""
from django.test import TransactionTestCase
from django.db import connection, models
from django.utils import timezone
from datetime import timedelta

# Import directly to avoid circular imports
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager


# Define test models (these won't be migrated, just created/dropped in tests)
class TestMetric(models.Model):
    """Test model with TimescaleDateTimeField."""
    time = TimescaleDateTimeField(interval="1 day")
    temperature = models.FloatField(default=0.0)
    device = models.IntegerField(default=0)

    objects = models.Manager()
    timescale = TimescaleManager()

    class Meta:
        app_label = 'timescale'
        db_table = 'timescale_testmetric'


class TestTimescaleModel(models.Model):
    """Test model similar to TimescaleModel."""
    time = TimescaleDateTimeField(interval="1 day")
    value = models.FloatField(default=0.0)

    objects = models.Manager()
    timescale = TimescaleManager()

    class Meta:
        app_label = 'timescale'
        db_table = 'timescale_testtimescalemodel'


class RetentionPolicyTests(TransactionTestCase):
    """Tests for TimescaleDB retention policies."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        
        # Create the test tables
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TestMetric)
            schema_editor.create_model(TestTimescaleModel)
            
        # Create hypertables
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT create_hypertable('timescale_testmetric', 'time', if_not_exists => TRUE)"
            )
            cursor.execute(
                "SELECT create_hypertable('timescale_testtimescalemodel', 'time', if_not_exists => TRUE)"
            )
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test data."""
        # Drop the test tables
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS timescale_testmetric CASCADE")
            cursor.execute("DROP TABLE IF EXISTS timescale_testtimescalemodel CASCADE")
            
        super().tearDownClass()
    
    def setUp(self):
        """Set up test data."""
        # Create some test data
        self.timestamp = timezone.now()
        TestMetric.objects.create(
            time=self.timestamp - timedelta(days=30),
            temperature=10.0,
            device=1
        )
        TestMetric.objects.create(
            time=self.timestamp - timedelta(days=60),
            temperature=15.0,
            device=1
        )
        TestMetric.objects.create(
            time=self.timestamp - timedelta(days=90),
            temperature=20.0,
            device=1
        )

    def test_add_retention_policy(self):
        """Test adding a retention policy."""
        # Add a retention policy to drop data older than 60 days
        job_id = TestMetric.timescale.add_retention_policy(
            drop_after='60 days',
            if_not_exists=True
        )
        
        # Check that the job was created
        self.assertIsNotNone(job_id)
        
        # Check that the policy exists in the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM timescaledb_information.jobs
                WHERE job_id = %s
            """, [job_id])
            result = cursor.fetchone()
            self.assertIsNotNone(result)
    
    def test_remove_retention_policy(self):
        """Test removing a retention policy."""
        # Add a retention policy
        job_id = TestMetric.timescale.add_retention_policy(
            drop_after='60 days',
            if_not_exists=True
        )
        
        # Remove the policy
        result = TestMetric.timescale.remove_retention_policy(if_exists=True)
        
        # Check that the policy was removed
        self.assertTrue(result)
        
        # Check that the policy no longer exists in the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM timescaledb_information.jobs
                WHERE job_id = %s
            """, [job_id])
            result = cursor.fetchone()
            self.assertIsNone(result)
    
class CompressionPolicyTests(TransactionTestCase):
    """Tests for TimescaleDB compression policies."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        
        # Create the test tables
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TestMetric)
            schema_editor.create_model(TestTimescaleModel)
            
        # Create hypertables
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT create_hypertable('timescale_testmetric', 'time', if_not_exists => TRUE)"
            )
            cursor.execute(
                "SELECT create_hypertable('timescale_testtimescalemodel', 'time', if_not_exists => TRUE)"
            )
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test data."""
        # Drop the test tables
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS timescale_testmetric CASCADE")
            cursor.execute("DROP TABLE IF EXISTS timescale_testtimescalemodel CASCADE")
            
        super().tearDownClass()
    
    def setUp(self):
        """Set up test data."""
        # Create some test data
        self.timestamp = timezone.now()
        TestMetric.objects.create(
            time=self.timestamp - timedelta(days=30),
            temperature=10.0,
            device=1
        )
        TestMetric.objects.create(
            time=self.timestamp - timedelta(days=60),
            temperature=15.0,
            device=1
        )
        TestMetric.objects.create(
            time=self.timestamp - timedelta(days=90),
            temperature=20.0,
            device=1
        )
    
    def test_enable_compression(self):
        """Test enabling compression on a hypertable."""
        # Enable compression
        result = TestMetric.timescale.enable_compression(
            compress_orderby=['time'],
            if_not_exists=True
        )
        
        # Check that compression was enabled
        self.assertTrue(result)
        
        # Check that compression is enabled in the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT compression_enabled FROM timescaledb_information.hypertables
                WHERE hypertable_name = 'timescale_testmetric'
            """)
            result = cursor.fetchone()
            # If result is None, compression might not be properly enabled
            self.assertIsNotNone(result, "Compression status not found in hypertables")
            self.assertTrue(result[0], "Compression is not enabled")
    
    def test_add_compression_policy(self):
        """Test adding a compression policy."""
        # Enable compression first
        TestMetric.timescale.enable_compression(
            compress_orderby=['time'],
            if_not_exists=True
        )
        
        # Add a compression policy to compress data older than 30 days
        job_id = TestMetric.timescale.add_compression_policy(
            compress_after='30 days',
            if_not_exists=True
        )
        
        # Check that the job was created
        self.assertIsNotNone(job_id)
        
        # Check that the policy exists in the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM timescaledb_information.jobs
                WHERE job_id = %s
            """, [job_id])
            result = cursor.fetchone()
            self.assertIsNotNone(result)
    
    def test_remove_compression_policy(self):
        """Test removing a compression policy."""
        # Enable compression first
        TestMetric.timescale.enable_compression(
            compress_orderby=['time'],
            if_not_exists=True
        )
        
        # Add a compression policy
        job_id = TestMetric.timescale.add_compression_policy(
            compress_after='30 days',
            if_not_exists=True
        )
        
        # Remove the policy
        result = TestMetric.timescale.remove_compression_policy(if_exists=True)
        
        # Check that the policy was removed
        self.assertTrue(result)
        
        # Check that the policy no longer exists in the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM timescaledb_information.jobs
                WHERE job_id = %s
            """, [job_id])
            result = cursor.fetchone()
            self.assertIsNone(result)
    
    def test_get_compression_stats(self):
        """Test getting compression statistics."""
        # Enable compression
        TestMetric.timescale.enable_compression(
            compress_orderby=['time'],
            if_not_exists=True
        )
        
        # Get compression stats
        stats = TestMetric.timescale.get_compression_stats()
        
        # Check that stats were returned
        self.assertIsInstance(stats, list)
        
        # There should be at least one row for our hypertable
        self.assertTrue(len(stats) > 0)
