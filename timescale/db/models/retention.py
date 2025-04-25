"""
Retention policy implementation for TimescaleDB.
"""
from django.db import connection
from typing import Optional, Union
from datetime import datetime, timedelta


class RetentionPolicy:
    """
    A class to manage retention policies for TimescaleDB hypertables.

    This allows setting up automatic removal of old data based on time,
    helping manage database size.
    """

    @staticmethod
    def add_retention_policy(
        model,
        drop_after: Union[str, int, timedelta],
        schedule_interval: Optional[Union[str, timedelta]] = None,
        if_not_exists: bool = False,
        drop_created_before: Optional[Union[str, timedelta]] = None,
        initial_start: Optional[datetime] = None,
        timezone: Optional[str] = None
    ) -> int:
        """
        Add a retention policy to a TimescaleDB hypertable.

        Args:
            model: The Django model with a TimescaleDateTimeField
            drop_after: Chunks older than this interval will be dropped
            schedule_interval: The interval between policy executions
            if_not_exists: If True, don't error if policy already exists
            drop_created_before: Alternative to drop_after, drops chunks created before this interval
            initial_start: Time the policy is first run
            timezone: Timezone for the policy

        Returns:
            The job ID of the created policy

        Raises:
            ValueError: If both drop_after and drop_created_before are provided
        """
        if drop_after is not None and drop_created_before is not None:
            raise ValueError("Cannot specify both drop_after and drop_created_before")

        table_name = model._meta.db_table

        # Convert timedelta to string interval if needed
        if isinstance(drop_after, timedelta):
            drop_after = f"{drop_after.total_seconds()} seconds"
        if isinstance(drop_created_before, timedelta):
            drop_created_before = f"{drop_created_before.total_seconds()} seconds"
        if isinstance(schedule_interval, timedelta):
            schedule_interval = f"{schedule_interval.total_seconds()} seconds"

        # Build the SQL query
        params = []
        sql = "SELECT add_retention_policy("

        # Add the table name
        sql += "%s"
        params.append(table_name)

        # Add drop_after or drop_created_before
        if drop_after is not None:
            sql += ", drop_after => INTERVAL %s"
            params.append(drop_after)
        if drop_created_before is not None:
            sql += ", drop_created_before => INTERVAL %s"
            params.append(drop_created_before)

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
    def remove_retention_policy(model, if_exists: bool = False) -> bool:
        """
        Remove a retention policy from a TimescaleDB hypertable.

        Args:
            model: The Django model with the retention policy
            if_exists: If True, don't error if policy doesn't exist

        Returns:
            True if the policy was removed, False otherwise
        """
        table_name = model._meta.db_table

        # Build the SQL query
        params = [table_name]
        sql = "SELECT remove_retention_policy(%s"

        if if_exists:
            sql += ", if_exists => TRUE"

        sql += ")"

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchone()[0]

        # If the result is None, the policy was removed successfully
        return True if result is None else result
