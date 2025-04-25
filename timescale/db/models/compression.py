"""
Compression policy implementation for TimescaleDB.
"""
from django.db import connection
from typing import Optional, Union, List, Dict, Any
from datetime import datetime, timedelta


class CompressionPolicy:
    """
    A class to manage compression policies for TimescaleDB hypertables.

    This allows setting up automatic compression of chunks to reduce storage requirements.
    """

    @staticmethod
    def add_compression_policy(
        model,
        compress_after: Union[str, int, timedelta],
        schedule_interval: Optional[Union[str, timedelta]] = None,
        if_not_exists: bool = False,
        compress_created_before: Optional[Union[str, timedelta]] = None,
        initial_start: Optional[datetime] = None,
        timezone: Optional[str] = None
    ) -> int:
        """
        Add a compression policy to a TimescaleDB hypertable.

        Args:
            model: The Django model with a TimescaleDateTimeField
            compress_after: Chunks older than this interval will be compressed
            schedule_interval: The interval between policy executions
            if_not_exists: If True, don't error if policy already exists
            compress_created_before: Alternative to compress_after, compresses chunks created before this interval
            initial_start: Time the policy is first run
            timezone: Timezone for the policy

        Returns:
            The job ID of the created policy

        Raises:
            ValueError: If both compress_after and compress_created_before are provided
        """
        if compress_after is not None and compress_created_before is not None:
            raise ValueError("Cannot specify both compress_after and compress_created_before")

        table_name = model._meta.db_table

        # Convert timedelta to string interval if needed
        if isinstance(compress_after, timedelta):
            compress_after = f"{compress_after.total_seconds()} seconds"
        if isinstance(compress_created_before, timedelta):
            compress_created_before = f"{compress_created_before.total_seconds()} seconds"
        if isinstance(schedule_interval, timedelta):
            schedule_interval = f"{schedule_interval.total_seconds()} seconds"

        # Build the SQL query
        params = []
        sql = "SELECT add_compression_policy("

        # Add the table name
        sql += "%s"
        params.append(table_name)

        # Add compress_after or compress_created_before
        if compress_after is not None:
            sql += ", compress_after => INTERVAL %s"
            params.append(compress_after)
        if compress_created_before is not None:
            sql += ", compress_created_before => INTERVAL %s"
            params.append(compress_created_before)

        # Add optional parameters
        if schedule_interval is not None:
            sql += ", schedule_interval => INTERVAL %s"
            params.append(schedule_interval)

        if initial_start is not None:
            sql += ", initial_start => %s"
            params.append(initial_start)

        if timezone is not None:
            sql += ", timezone => %s"
            params.append(timezone)

        if if_not_exists:
            sql += ", if_not_exists => TRUE"

        sql += ")"

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            job_id = cursor.fetchone()[0]

        return job_id

    @staticmethod
    def remove_compression_policy(model, if_exists: bool = False) -> bool:
        """
        Remove a compression policy from a TimescaleDB hypertable.

        Args:
            model: The Django model with the compression policy
            if_exists: If True, don't error if policy doesn't exist

        Returns:
            True if the policy was removed, False otherwise
        """
        table_name = model._meta.db_table

        # Build the SQL query
        params = [table_name]
        sql = "SELECT remove_compression_policy(%s"

        if if_exists:
            sql += ", if_exists => TRUE"

        sql += ")"

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchone()[0]

        # If the result is None, the policy was removed successfully
        return True if result is None else result

    @staticmethod
    def enable_compression(model, compress_segmentby: Optional[List[str]] = None,
                          compress_orderby: Optional[List[str]] = None,
                          compress_chunk_time_interval: Optional[Union[str, timedelta]] = None,
                          if_not_exists: bool = False) -> bool:
        """
        Enable compression on a TimescaleDB hypertable.

        Args:
            model: The Django model to enable compression on
            compress_segmentby: List of columns to segment by
            compress_orderby: List of columns to order by
            compress_chunk_time_interval: Time interval for compression chunks
            if_not_exists: If True, don't error if compression is already enabled

        Returns:
            True if compression was enabled, False otherwise
        """
        table_name = model._meta.db_table

        # Convert timedelta to string interval if needed
        if isinstance(compress_chunk_time_interval, timedelta):
            compress_chunk_time_interval = f"{compress_chunk_time_interval.total_seconds()} seconds"

        # Build the SQL query
        sql = f"ALTER TABLE {table_name} SET (timescaledb.compress = TRUE"

        if compress_segmentby:
            sql += f", timescaledb.compress_segmentby = '{','.join(compress_segmentby)}'"

        if compress_orderby:
            sql += f", timescaledb.compress_orderby = '{','.join(compress_orderby)}'"

        if compress_chunk_time_interval:
            sql += f", timescaledb.compress_chunk_time_interval = '{compress_chunk_time_interval}'"

        sql += ")"

        # Execute the query
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
            return True
        except Exception as e:
            if if_not_exists and "already compressed" in str(e):
                return False
            raise

    @staticmethod
    def compress_chunk(chunk_name: str) -> bool:
        """
        Manually compress a specific chunk.

        Args:
            chunk_name: The name of the chunk to compress

        Returns:
            True if the chunk was compressed, False otherwise
        """
        # Build the SQL query
        sql = f"SELECT compress_chunk('{chunk_name}')"

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()[0]

        return result

    @staticmethod
    def decompress_chunk(chunk_name: str) -> bool:
        """
        Manually decompress a specific chunk.

        Args:
            chunk_name: The name of the chunk to decompress

        Returns:
            True if the chunk was decompressed, False otherwise
        """
        # Build the SQL query
        sql = f"SELECT decompress_chunk('{chunk_name}')"

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()[0]

        return result

    @staticmethod
    def get_compression_stats(model) -> List[Dict[str, Any]]:
        """
        Get compression statistics for a hypertable.

        Args:
            model: The Django model to get compression stats for

        Returns:
            A list of dictionaries containing compression statistics
        """
        table_name = model._meta.db_table

        # Build the SQL query
        sql = f"SELECT * FROM hypertable_compression_stats('{table_name}')"

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return results
