from fastapi import APIRouter

from app.models import QueryRequest, QueryResponse
from app.services.sql_runner import ConnectionNotFoundError, SQLExecutionError, run_sql_query

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def execute_sql_query(query_request: QueryRequest):
    """
    Execute a SQL query on the specified database connection.

    Returns a structured response with status, data, and error information.
    """
    try:
        # Execute the query
        result = await run_sql_query(query_request.connection_id, query_request.sql)

        # Return successful response
        return QueryResponse(status="ok", data=result, error=None)

    except ConnectionNotFoundError as e:
        # Connection not found - return error response instead of HTTP exception
        return QueryResponse(status="error", data=None, error=f"Connection not found: {str(e)}")

    except SQLExecutionError as e:
        # SQL execution error - return error response instead of HTTP exception
        return QueryResponse(status="error", data=None, error=f"SQL execution failed: {str(e)}")

    except Exception as e:
        # Unexpected error - return error response
        return QueryResponse(status="error", data=None, error=f"Unexpected error: {str(e)}")


@router.post("/instances/{connection_id}/query", response_model=QueryResponse)
async def execute_sql_query_by_connection(connection_id: str, sql_query: dict):
    """
    Execute a SQL query on a specific database connection (alternative endpoint).

    This endpoint allows specifying the connection ID in the URL path.
    The request body should contain: {"sql": "SELECT * FROM table"}
    """
    try:
        # Validate that sql is provided
        if "sql" not in sql_query or not sql_query["sql"]:
            return QueryResponse(status="error", data=None, error="SQL query is required in request body")

        # Execute the query
        result = await run_sql_query(connection_id, sql_query["sql"])

        # Return successful response
        return QueryResponse(status="ok", data=result, error=None)

    except ConnectionNotFoundError as e:
        # Connection not found - return error response
        return QueryResponse(status="error", data=None, error=f"Connection not found: {str(e)}")

    except SQLExecutionError as e:
        # SQL execution error - return error response
        return QueryResponse(status="error", data=None, error=f"SQL execution failed: {str(e)}")

    except Exception as e:
        # Unexpected error - return error response
        return QueryResponse(status="error", data=None, error=f"Unexpected error: {str(e)}")
