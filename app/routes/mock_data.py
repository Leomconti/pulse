import sqlite3
from pathlib import Path

from app.models import DatabaseConnection, DatabaseConnectionResponse, DatabaseType
from app.services.redis_ops import delete_data, list_data, save_data
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

# Mock database configurations
MOCK_DATABASES = [
    {
        "name": "E-commerce Store",
        "filename": "ecommerce.sqlite",
        "tables": {
            "customers": [
                ("id", "INTEGER PRIMARY KEY"),
                ("name", "TEXT NOT NULL"),
                ("email", "TEXT UNIQUE"),
                ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
            ],
            "products": [
                ("id", "INTEGER PRIMARY KEY"),
                ("name", "TEXT NOT NULL"),
                ("price", "DECIMAL(10,2)"),
                ("category", "TEXT"),
                ("stock", "INTEGER DEFAULT 0"),
            ],
            "orders": [
                ("id", "INTEGER PRIMARY KEY"),
                ("customer_id", "INTEGER REFERENCES customers(id)"),
                ("total", "DECIMAL(10,2)"),
                ("status", "TEXT DEFAULT 'pending'"),
                ("order_date", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
            ],
        },
        "data": {
            "customers": [
                (1, "Alice Johnson", "alice@example.com", "2024-01-15 10:30:00"),
                (2, "Bob Smith", "bob@example.com", "2024-01-20 14:45:00"),
                (3, "Carol Williams", "carol@example.com", "2024-02-01 09:15:00"),
                (4, "David Brown", "david@example.com", "2024-02-05 16:20:00"),
                (5, "Eva Davis", "eva@example.com", "2024-02-10 11:00:00"),
            ],
            "products": [
                (1, "Laptop", 999.99, "Electronics", 50),
                (2, "Smartphone", 699.99, "Electronics", 100),
                (3, "Headphones", 199.99, "Electronics", 75),
                (4, "Coffee Mug", 12.99, "Kitchen", 200),
                (5, "Notebook", 8.99, "Office", 150),
                (6, "Desk Lamp", 45.99, "Office", 30),
            ],
            "orders": [
                (1, 1, 999.99, "completed", "2024-01-16 10:00:00"),
                (2, 2, 899.98, "completed", "2024-01-21 15:30:00"),
                (3, 3, 212.98, "pending", "2024-02-02 14:15:00"),
                (4, 4, 54.98, "shipped", "2024-02-06 10:45:00"),
                (5, 5, 199.99, "pending", "2024-02-11 09:30:00"),
            ],
        },
    },
    {
        "name": "Blog Platform",
        "filename": "blog.sqlite",
        "tables": {
            "authors": [
                ("id", "INTEGER PRIMARY KEY"),
                ("username", "TEXT UNIQUE NOT NULL"),
                ("full_name", "TEXT"),
                ("email", "TEXT"),
                ("bio", "TEXT"),
            ],
            "posts": [
                ("id", "INTEGER PRIMARY KEY"),
                ("title", "TEXT NOT NULL"),
                ("content", "TEXT"),
                ("author_id", "INTEGER REFERENCES authors(id)"),
                ("published_at", "DATETIME"),
                ("status", "TEXT DEFAULT 'draft'"),
            ],
            "comments": [
                ("id", "INTEGER PRIMARY KEY"),
                ("post_id", "INTEGER REFERENCES posts(id)"),
                ("author_name", "TEXT"),
                ("content", "TEXT"),
                ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
            ],
        },
        "data": {
            "authors": [
                (1, "techblogger", "Jane Doe", "jane@techblog.com", "Tech enthusiast and writer"),
                (2, "codeguru", "John Smith", "john@codeguru.com", "Senior developer sharing insights"),
                (3, "airesearcher", "Dr. Emily Chen", "emily@airesearch.com", "AI researcher and educator"),
            ],
            "posts": [
                (
                    1,
                    "Getting Started with FastAPI",
                    "FastAPI is a modern web framework...",
                    1,
                    "2024-01-10 08:00:00",
                    "published",
                ),
                (
                    2,
                    "Database Design Best Practices",
                    "When designing databases...",
                    2,
                    "2024-01-15 12:00:00",
                    "published",
                ),
                (
                    3,
                    "Machine Learning in Production",
                    "Deploying ML models requires...",
                    3,
                    "2024-01-20 14:30:00",
                    "published",
                ),
                (
                    4,
                    "Advanced Python Patterns",
                    "Python offers many advanced features...",
                    2,
                    "2024-01-25 10:15:00",
                    "draft",
                ),
            ],
            "comments": [
                (1, 1, "Alice Reader", "Great introduction! Very helpful.", "2024-01-11 09:30:00"),
                (2, 1, "Bob Developer", "Thanks for the clear examples.", "2024-01-12 14:15:00"),
                (3, 2, "Carol DBA", "Excellent points about normalization.", "2024-01-16 16:20:00"),
                (4, 3, "David ML", "Looking forward to more ML content!", "2024-01-21 11:45:00"),
            ],
        },
    },
]


def create_mock_database(db_config: dict) -> str:
    """Create a mock SQLite database with sample data."""
    db_path = Path("mock_data") / db_config["filename"]
    db_path.parent.mkdir(exist_ok=True)

    # Remove existing database
    if db_path.exists():
        db_path.unlink()

    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Create tables
        for table_name, columns in db_config["tables"].items():
            column_defs = ", ".join([f"{col[0]} {col[1]}" for col in columns])
            cursor.execute(f"CREATE TABLE {table_name} ({column_defs})")

        # Insert data
        for table_name, rows in db_config["data"].items():
            if rows:
                placeholders = ", ".join(["?"] * len(rows[0]))
                cursor.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", rows)

        conn.commit()
        return str(db_path.absolute())

    finally:
        conn.close()


@router.post("/mock-data/create")
async def create_mock_databases():
    """Create mock databases with sample data for testing."""
    try:
        created_connections = []

        for db_config in MOCK_DATABASES:
            # Create the SQLite database file
            db_path = create_mock_database(db_config)

            # Create connection object
            connection = DatabaseConnection(
                name=db_config["name"],
                db_type=DatabaseType.SQLITE,
                host="localhost",
                port=5432,  # Not used for SQLite
                database=db_path,
                username="mock",
                password="mock",
            )

            # Save to Redis
            await save_data(connection.id, connection)
            created_connections.append(DatabaseConnectionResponse.from_connection(connection))

        return JSONResponse(
            content={
                "message": f"Created {len(created_connections)} mock databases",
                "connections": [conn.model_dump() for conn in created_connections],
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create mock databases: {str(e)}")


@router.delete("/mock-data/cleanup")
async def cleanup_mock_databases():
    """Clean up all mock databases and connections."""
    try:
        # Get all connections
        connections = await list_data(DatabaseConnection)

        deleted_count = 0
        cleaned_files = []

        for connection in connections:
            # Check if it's a mock database (in mock_data directory)
            if "mock_data" in connection.database or connection.username == "mock":
                # Delete from Redis
                await delete_data(connection.id, DatabaseConnection)
                deleted_count += 1

                # Delete database file if it exists
                db_path = Path(connection.database)
                if db_path.exists():
                    try:
                        db_path.unlink()
                        cleaned_files.append(str(db_path))
                    except Exception as e:
                        print(f"Warning: Could not delete {db_path}: {e}")

        # Clean up empty mock_data directory
        mock_data_dir = Path("mock_data")
        if mock_data_dir.exists() and not any(mock_data_dir.iterdir()):
            mock_data_dir.rmdir()

        return JSONResponse(
            content={
                "message": f"Cleaned up {deleted_count} mock database connections",
                "deleted_connections": deleted_count,
                "cleaned_files": cleaned_files,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup mock databases: {str(e)}")


@router.get("/mock-data/info")
async def get_mock_database_info():
    """Get information about available mock databases."""
    info = []

    for db_config in MOCK_DATABASES:
        table_info = {}
        for table_name, columns in db_config["tables"].items():
            table_info[table_name] = {
                "columns": [col[0] for col in columns],
                "row_count": len(db_config["data"].get(table_name, [])),
            }

        info.append({"name": db_config["name"], "filename": db_config["filename"], "tables": table_info})

    return JSONResponse(content={"mock_databases": info})
