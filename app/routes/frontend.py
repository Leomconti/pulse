from datetime import datetime
from typing import Optional

from app.models import DatabaseConnection, DatabaseConnectionCreate, DatabaseType
from app.services.redis_ops import delete_data, get_data, list_data, save_data
from app.services.sql_runner import ConnectionNotFoundError, SQLExecutionError, run_sql_query
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# Add custom filter to convert Unix timestamp to readable date
def timestamp_to_date(timestamp: float) -> str:
    """Convert Unix timestamp to readable date format."""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError, OSError):
        return "Invalid date"


# Add pluralize filter for proper pluralization
def pluralize_filter(count: int, singular: str = "", plural: str = "s") -> str:
    """Add 's' for pluralization or custom singular/plural forms."""
    if count == 1:
        return singular
    return plural


templates.env.filters["timestamp_to_date"] = timestamp_to_date
templates.env.filters["pluralize"] = pluralize_filter


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page."""
    try:
        connections = await list_data(DatabaseConnection)
        return templates.TemplateResponse("dashboard.html", {"request": request, "connections": connections})
    except Exception as e:
        return templates.TemplateResponse("dashboard.html", {"request": request, "connections": [], "error": str(e)})


@router.get("/connections", response_class=HTMLResponse)
async def connections_page(request: Request):
    """Connections management page."""
    try:
        connections = await list_data(DatabaseConnection)
        return templates.TemplateResponse("connections.html", {"request": request, "connections": connections})
    except Exception as e:
        return templates.TemplateResponse("connections.html", {"request": request, "connections": [], "error": str(e)})


@router.post("/connections", response_class=HTMLResponse)
async def create_connection_form(
    request: Request,
    name: str = Form(...),
    db_type: str = Form(...),
    host: str = Form(...),
    port: int = Form(...),
    database: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
):
    """Create a new database connection via form."""
    try:
        # Create connection
        connection_data = DatabaseConnectionCreate(
            name=name,
            db_type=DatabaseType(db_type),
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
        )

        connection = DatabaseConnection(**connection_data.model_dump())

        # Test connection (using the test function)
        from app.services.sql_runner import test_database_connection

        is_valid = await test_database_connection(connection)

        if not is_valid:
            raise HTTPException(status_code=400, detail="Unable to connect to database")

        # Save connection
        await save_data(connection.id, connection)

        # Return updated connections list
        connections = await list_data(DatabaseConnection)
        return templates.TemplateResponse(
            "partials/connections_list.html",
            {"request": request, "connections": connections, "success": f"Connection '{name}' created successfully!"},
        )

    except Exception as e:
        connections = await list_data(DatabaseConnection)
        return templates.TemplateResponse(
            "partials/connections_list.html", {"request": request, "connections": connections, "error": str(e)}
        )


@router.delete("/connections/{connection_id}", response_class=HTMLResponse)
async def delete_connection_form(request: Request, connection_id: str):
    """Delete a database connection."""
    try:
        await delete_data(connection_id, DatabaseConnection)

        # Return updated connections list
        connections = await list_data(DatabaseConnection)
        return templates.TemplateResponse(
            "partials/connections_list.html",
            {"request": request, "connections": connections, "success": "Connection deleted successfully!"},
        )

    except Exception as e:
        connections = await list_data(DatabaseConnection)
        return templates.TemplateResponse(
            "partials/connections_list.html", {"request": request, "connections": connections, "error": str(e)}
        )


@router.get("/query", response_class=HTMLResponse)
async def query_page(request: Request, connection_id: Optional[str] = None):
    """SQL query execution page."""
    try:
        connections = await list_data(DatabaseConnection)
        selected_connection = None

        if connection_id:
            try:
                selected_connection = await get_data(connection_id, DatabaseConnection)
            except KeyError:
                pass

        return templates.TemplateResponse(
            "query.html", {"request": request, "connections": connections, "selected_connection": selected_connection}
        )
    except Exception as e:
        return templates.TemplateResponse("query.html", {"request": request, "connections": [], "error": str(e)})


@router.post("/query/execute", response_class=HTMLResponse)
async def execute_query_form(request: Request, connection_id: str = Form(...), sql: str = Form(...)):
    """Execute a SQL query via form."""
    try:
        # Execute the query
        result = await run_sql_query(connection_id, sql)

        # Get connection name for display
        try:
            connection = await get_data(connection_id, DatabaseConnection)
            connection_name = connection.name
        except:
            connection_name = "Unknown"

        return templates.TemplateResponse(
            "partials/query_result.html",
            {"request": request, "result": result, "sql": sql, "connection_name": connection_name, "success": True},
        )

    except (ConnectionNotFoundError, SQLExecutionError) as e:
        return templates.TemplateResponse(
            "partials/query_result.html", {"request": request, "error": str(e), "sql": sql, "success": False}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "partials/query_result.html",
            {"request": request, "error": f"Unexpected error: {str(e)}", "sql": sql, "success": False},
        )


@router.post("/mock-data/create-ui", response_class=HTMLResponse)
async def create_mock_data_ui(request: Request):
    """Create mock databases via UI."""
    try:
        # Import and call the mock data creation
        from app.routes.mock_data import create_mock_databases

        await create_mock_databases()

        # Get updated connections
        connections = await list_data(DatabaseConnection)

        return templates.TemplateResponse(
            "partials/connections_list.html",
            {"request": request, "connections": connections, "success": "Mock databases created successfully!"},
        )

    except Exception as e:
        connections = await list_data(DatabaseConnection)
        return templates.TemplateResponse(
            "partials/connections_list.html", {"request": request, "connections": connections, "error": str(e)}
        )


@router.post("/mock-data/cleanup-ui", response_class=HTMLResponse)
async def cleanup_mock_data_ui(request: Request):
    """Cleanup mock databases via UI."""
    try:
        # Import and call the mock data cleanup
        from app.routes.mock_data import cleanup_mock_databases

        await cleanup_mock_databases()

        # Get updated connections
        connections = await list_data(DatabaseConnection)

        return templates.TemplateResponse(
            "partials/connections_list.html",
            {"request": request, "connections": connections, "success": "Mock databases cleaned up successfully!"},
        )

    except Exception as e:
        connections = await list_data(DatabaseConnection)
        return templates.TemplateResponse(
            "partials/connections_list.html", {"request": request, "connections": connections, "error": str(e)}
        )


# Universal mock data endpoints that work with HTMX events
@router.post("/mock-data/create-universal")
async def create_mock_data_universal(request: Request):
    """Universal mock data creation endpoint that triggers custom events."""
    try:
        from app.routes.mock_data import create_mock_databases

        await create_mock_databases()

        # Return response with custom event trigger
        response = templates.TemplateResponse("partials/empty.html", {"request": request})
        response.headers["HX-Trigger"] = "mockDataCreated"
        return response

    except Exception as e:
        response = templates.TemplateResponse("partials/empty.html", {"request": request})
        response.headers["HX-Trigger"] = f"mockDataError:{str(e)}"
        return response


@router.delete("/mock-data/cleanup-universal")
async def cleanup_mock_data_universal(request: Request):
    """Universal mock data cleanup endpoint that triggers custom events."""
    try:
        # Import and call the mock data cleanup
        from app.routes.mock_data import cleanup_mock_databases

        await cleanup_mock_databases()

        # Return response with custom event trigger
        response = templates.TemplateResponse("partials/empty.html", {"request": request})
        response.headers["HX-Trigger"] = "mockDataCleaned"
        return response

    except Exception as e:
        response = templates.TemplateResponse("partials/empty.html", {"request": request})
        response.headers["HX-Trigger"] = f"mockDataError:{str(e)}"
        return response


@router.get("/connections-list-partial", response_class=HTMLResponse)
async def connections_list_partial(request: Request):
    """Get just the connections list partial for refreshing."""
    try:
        connections = await list_data(DatabaseConnection)
        return templates.TemplateResponse(
            "partials/connections_list.html", {"request": request, "connections": connections}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "partials/connections_list.html", {"request": request, "connections": [], "error": str(e)}
        )


@router.get("/dashboard-stats-partial", response_class=HTMLResponse)
async def dashboard_stats_partial(request: Request):
    """Get just the dashboard stats partial for refreshing."""
    try:
        connections = await list_data(DatabaseConnection)
        return templates.TemplateResponse(
            "partials/dashboard_stats.html", {"request": request, "connections": connections}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "partials/dashboard_stats.html", {"request": request, "connections": [], "error": str(e)}
        )


@router.get("/dashboard-connections-partial", response_class=HTMLResponse)
async def dashboard_connections_partial(request: Request):
    """Get just the dashboard connections partial for refreshing."""
    try:
        connections = await list_data(DatabaseConnection)
        return templates.TemplateResponse(
            "partials/dashboard_connections.html", {"request": request, "connections": connections}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "partials/dashboard_connections.html", {"request": request, "connections": [], "error": str(e)}
        )
