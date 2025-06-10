import time

import asyncpg
import sqlalchemy as sa
from app.models import DatabaseConnection, QueryResult
from app.services.redis_ops import get_data
from sqlalchemy.ext.asyncio import create_async_engine


class SQLExecutionError(Exception):
    """Custom exception for SQL execution errors."""

    pass


class ConnectionNotFoundError(Exception):
    """Exception raised when database connection is not found."""

    pass


async def _execute_postgresql_query(connection: DatabaseConnection, sql: str) -> QueryResult:
    """Execute query on PostgreSQL database."""
    start_time = time.time()

    try:
        # Create direct asyncpg connection for better control
        conn = await asyncpg.connect(
            user=connection.username,
            password=connection.password,
            database=connection.database,
            host=connection.host,
            port=connection.port,
            server_settings={"application_name": "pulse_sql_runner"},
        )

        try:
            # Execute query
            result = await conn.fetch(sql)

            # Process results
            columns = []
            rows = []

            if result:
                # Get column names from the first row
                columns = list(result[0].keys())

                # Convert rows to list format
                rows = [list(row.values()) for row in result]

            execution_time = (time.time() - start_time) * 1000

            return QueryResult(
                columns=columns, rows=rows, row_count=len(rows), execution_time_ms=round(execution_time, 2)
            )

        finally:
            await conn.close()

    except asyncpg.PostgresError as e:
        raise SQLExecutionError(f"PostgreSQL error: {str(e)}")
    except Exception as e:
        raise SQLExecutionError(f"Unexpected error: {str(e)}")


async def _execute_generic_query(connection: DatabaseConnection, sql: str) -> QueryResult:
    """Execute query using SQLAlchemy for generic database support."""
    start_time = time.time()

    try:
        # Create engine for the specific database type
        engine = create_async_engine(connection.get_connection_url(), echo=False, pool_pre_ping=True, pool_recycle=300)

        try:
            async with engine.begin() as conn:
                # Execute the query
                result = await conn.execute(sa.text(sql))

                # Process results
                columns = []
                rows = []

                if result.returns_rows:
                    # Get column names
                    columns = list(result.keys())

                    # Fetch all rows
                    fetched_rows = result.fetchall()
                    rows = [list(row) for row in fetched_rows]
                else:
                    # For non-SELECT queries, return row count if available
                    if hasattr(result, "rowcount") and result.rowcount is not None:
                        return QueryResult(
                            columns=["affected_rows"],
                            rows=[[result.rowcount]],
                            row_count=1,
                            execution_time_ms=round((time.time() - start_time) * 1000, 2),
                        )

                execution_time = (time.time() - start_time) * 1000

                return QueryResult(
                    columns=columns, rows=rows, row_count=len(rows), execution_time_ms=round(execution_time, 2)
                )

        finally:
            await engine.dispose()

    except Exception as e:
        # Handle SQLAlchemy and database-specific errors
        if "sqlalchemy" in str(type(e).__module__).lower():
            raise SQLExecutionError(f"Database error: {str(e)}")
        raise SQLExecutionError(f"Unexpected error: {str(e)}")


async def run_sql_query(connection_id: str, sql: str) -> QueryResult:
    """
    Execute a SQL query on the specified database connection.

    Args:
        connection_id: The ID of the database connection to use
        sql: The SQL query to execute

    Returns:
        QueryResult with the query results

    Raises:
        ConnectionNotFoundError: If the connection ID is not found
        SQLExecutionError: If there's an error executing the SQL
    """
    try:
        # Retrieve the database connection from Redis
        connection = await get_data(connection_id, DatabaseConnection)
    except KeyError:
        raise ConnectionNotFoundError(f"Database connection with ID {connection_id} not found")

    # Validate SQL input
    sql = sql.strip()
    if not sql:
        raise SQLExecutionError("SQL query cannot be empty")

    # Use PostgreSQL-specific implementation for better performance
    if connection.db_type.value == "postgresql":
        return await _execute_postgresql_query(connection, sql)
    else:
        # Use generic SQLAlchemy implementation for other databases
        return await _execute_generic_query(connection, sql)


async def test_database_connection(connection: DatabaseConnection) -> bool:
    """
    Test if a database connection is valid.

    Args:
        connection: The database connection to test

    Returns:
        True if connection is successful, False otherwise
    """
    try:
        # Use a simple query to test the connection
        result = await run_sql_query(connection.id, "SELECT 1 as test_connection")
        return result.row_count == 1
    except (ConnectionNotFoundError, SQLExecutionError):
        return False
