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


def _translate_sql_for_sqlite(sql: str) -> str:
    """
    Translate common MySQL/PostgreSQL SQL commands to SQLite equivalents.

    Args:
        sql: The original SQL query

    Returns:
        Translated SQL query for SQLite
    """
    sql_upper = sql.upper().strip()

    # Handle SHOW TABLES
    if sql_upper == "SHOW TABLES;" or sql_upper == "SHOW TABLES":
        return "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"

    # Handle SHOW DATABASES (not really applicable to SQLite, but provide something useful)
    if sql_upper == "SHOW DATABASES;" or sql_upper == "SHOW DATABASES":
        return "SELECT 'main' as database_name;"

    # Handle DESC or DESCRIBE table
    if sql_upper.startswith("DESC ") or sql_upper.startswith("DESCRIBE "):
        # Extract table name
        parts = sql.split()
        if len(parts) >= 2:
            table_name = parts[1].strip(";")
            return f"PRAGMA table_info({table_name});"

    # Handle SHOW COLUMNS FROM table
    if sql_upper.startswith("SHOW COLUMNS FROM "):
        parts = sql.split()
        if len(parts) >= 4:
            table_name = parts[3].strip(";")
            return f"PRAGMA table_info({table_name});"

    # Return original SQL if no translation needed
    return sql


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

    # Translate SQL for SQLite if needed
    if connection.db_type.value == "sqlite":
        sql = _translate_sql_for_sqlite(sql)

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
        # Test the connection directly without relying on Redis
        if connection.db_type.value == "postgresql":
            result = await _execute_postgresql_query(connection, "SELECT 1 as test_connection")
        else:
            result = await _execute_generic_query(connection, "SELECT 1 as test_connection")

        return result.row_count == 1
    except (SQLExecutionError, Exception):
        return False


async def get_database_schema(connection: DatabaseConnection) -> dict:
    """
    Get the database schema information.

    Args:
        connection: The database connection to get schema from

    Returns:
        Dictionary containing schema information with tables and columns

    Raises:
        SQLExecutionError: If there's an error getting schema information
    """
    try:
        schema = {"tables": {}}

        if connection.db_type.value == "postgresql":
            # Get tables and their columns for PostgreSQL
            tables_query = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """
            tables_result = await _execute_postgresql_query(connection, tables_query)

            for table_row in tables_result.rows:
                table_name = table_row[0]

                # Get columns for this table
                columns_query = f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = '{table_name}'
                    ORDER BY ordinal_position;
                """
                columns_result = await _execute_postgresql_query(connection, columns_query)

                schema["tables"][table_name] = {"columns": []}

                for col_row in columns_result.rows:
                    schema["tables"][table_name]["columns"].append(
                        {"name": col_row[0], "type": col_row[1], "nullable": col_row[2] == "YES", "default": col_row[3]}
                    )

        elif connection.db_type.value == "sqlite":
            # Get tables for SQLite
            tables_query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
            tables_result = await _execute_generic_query(connection, tables_query)

            for table_row in tables_result.rows:
                table_name = table_row[0]

                # Get columns for this table using PRAGMA
                columns_query = f"PRAGMA table_info({table_name});"
                columns_result = await _execute_generic_query(connection, columns_query)

                schema["tables"][table_name] = {"columns": []}

                for col_row in columns_result.rows:
                    # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
                    schema["tables"][table_name]["columns"].append(
                        {
                            "name": col_row[1],
                            "type": col_row[2],
                            "nullable": not bool(col_row[3]),
                            "default": col_row[4],
                        }
                    )

        elif connection.db_type.value == "mysql":
            # Get tables for MySQL
            tables_query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{connection.database}' ORDER BY table_name;"
            tables_result = await _execute_generic_query(connection, tables_query)

            for table_row in tables_result.rows:
                table_name = table_row[0]

                # Get columns for this table
                columns_query = f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = '{connection.database}' AND table_name = '{table_name}'
                    ORDER BY ordinal_position;
                """
                columns_result = await _execute_generic_query(connection, columns_query)

                schema["tables"][table_name] = {"columns": []}

                for col_row in columns_result.rows:
                    schema["tables"][table_name]["columns"].append(
                        {"name": col_row[0], "type": col_row[1], "nullable": col_row[2] == "YES", "default": col_row[3]}
                    )

        else:
            # Generic approach for other databases
            tables_query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{connection.database}' ORDER BY table_name;"
            tables_result = await _execute_generic_query(connection, tables_query)

            for table_row in tables_result.rows:
                table_name = table_row[0]

                columns_query = f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = '{connection.database}' AND table_name = '{table_name}'
                    ORDER BY ordinal_position;
                """
                columns_result = await _execute_generic_query(connection, columns_query)

                schema["tables"][table_name] = {"columns": []}

                for col_row in columns_result.rows:
                    schema["tables"][table_name]["columns"].append(
                        {"name": col_row[0], "type": col_row[1], "nullable": col_row[2] == "YES", "default": col_row[3]}
                    )

        return schema

    except Exception as e:
        raise SQLExecutionError(f"Failed to get database schema: {str(e)}")
