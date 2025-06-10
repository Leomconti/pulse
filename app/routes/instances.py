import time

from app.models import (
    DatabaseConnection,
    DatabaseConnectionCreate,
    DatabaseConnectionResponse,
    DatabaseConnectionUpdate,
)
from app.services.redis_ops import delete_data, exists_data, get_data, list_data, save_data
from app.services.sql_runner import test_database_connection
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/instances", response_model=DatabaseConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_database_connection(connection_data: DatabaseConnectionCreate):
    """
    Create a new database connection after validating it.
    """
    try:
        # Create the database connection model
        connection = DatabaseConnection(**connection_data.model_dump())

        # Test the connection before saving
        connection_test_success = await test_database_connection(connection)
        if not connection_test_success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to establish connection to the database. Please check your connection parameters.",
            )

        # Save to Redis
        await save_data(connection.id, connection)

        # Return response without password
        return DatabaseConnectionResponse.from_connection(connection)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create database connection: {str(e)}"
        )


@router.get("/instances", response_model=list[DatabaseConnectionResponse])
async def list_database_connections():
    """
    List all saved database connections.
    """
    try:
        connections = await list_data(DatabaseConnection)

        # Convert to response models (without passwords)
        return [DatabaseConnectionResponse.from_connection(conn) for conn in connections]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve database connections: {str(e)}",
        )


@router.get("/instances/{connection_id}", response_model=DatabaseConnectionResponse)
async def get_database_connection(connection_id: str):
    """
    Get a specific database connection by ID.
    """
    try:
        connection = await get_data(connection_id, DatabaseConnection)
        return DatabaseConnectionResponse.from_connection(connection)

    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Database connection with ID {connection_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve database connection: {str(e)}",
        )


@router.put("/instances/{connection_id}", response_model=DatabaseConnectionResponse)
async def update_database_connection(connection_id: str, connection_update: DatabaseConnectionUpdate):
    """
    Update an existing database connection.
    """
    try:
        # Get the existing connection
        existing_connection = await get_data(connection_id, DatabaseConnection)

        # Apply updates
        update_data = connection_update.model_dump(exclude_unset=True)
        if update_data:
            # Update the timestamp
            update_data["updated_at"] = time.time()

            # Create updated connection
            updated_connection = existing_connection.model_copy(update=update_data)

            # Test the updated connection if connection parameters changed
            connection_params_changed = any(
                field in update_data for field in ["db_type", "host", "port", "database", "username", "password"]
            )

            if connection_params_changed:
                connection_test_success = await test_database_connection(updated_connection)
                if not connection_test_success:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Unable to establish connection with updated parameters. Please check your connection settings.",
                    )

            # Save the updated connection
            await save_data(connection_id, updated_connection)

            return DatabaseConnectionResponse.from_connection(updated_connection)
        else:
            # No updates provided, return existing connection
            return DatabaseConnectionResponse.from_connection(existing_connection)

    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Database connection with ID {connection_id} not found"
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update database connection: {str(e)}"
        )


@router.delete("/instances/{connection_id}")
async def delete_database_connection(connection_id: str):
    """
    Delete a database connection.
    """
    try:
        # Check if connection exists first
        connection_exists = await exists_data(connection_id, DatabaseConnection)
        if not connection_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Database connection with ID {connection_id} not found"
            )

        # Delete the connection
        deleted = await delete_data(connection_id, DatabaseConnection)

        if deleted:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": f"Database connection {connection_id} deleted successfully"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete database connection"
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete database connection: {str(e)}"
        )


@router.post("/instances/{connection_id}/test")
async def test_connection(connection_id: str):
    """
    Test a database connection without executing a custom query.
    """
    try:
        connection = await get_data(connection_id, DatabaseConnection)

        is_valid = await test_database_connection(connection)

        if is_valid:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status": "ok", "message": "Database connection is working correctly"},
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "error", "message": "Unable to establish connection to the database"},
            )

    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Database connection with ID {connection_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to test database connection: {str(e)}"
        )


@router.get("/instances/{connection_id}/schema")
async def get_schema(connection_id: str):
    """
    Get the schema information from a database connection.
    """
    try:
        connection = await get_data(connection_id, DatabaseConnection)

        from app.services.sql_runner import get_database_schema

        schema = await get_database_schema(connection)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok", "schema": schema},
        )

    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Database connection with ID {connection_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get database schema: {str(e)}"
        )
