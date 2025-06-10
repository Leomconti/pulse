#!/usr/bin/env python3
"""
Simple test script to verify the database chat API functionality.
This demonstrates how to use the API endpoints.
"""

import asyncio
from typing import Any

import httpx


class DatabaseChatAPIClient:
    """Simple client for testing the Database Chat API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def create_connection(self, connection_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new database connection."""
        response = await self.client.post(f"{self.base_url}/api/v1/instances", json=connection_data)
        return response.json()

    async def list_connections(self) -> dict[str, Any]:
        """List all database connections."""
        response = await self.client.get(f"{self.base_url}/api/v1/instances")
        return response.json()

    async def get_connection(self, connection_id: str) -> dict[str, Any]:
        """Get a specific database connection."""
        response = await self.client.get(f"{self.base_url}/api/v1/instances/{connection_id}")
        return response.json()

    async def test_connection(self, connection_id: str) -> dict[str, Any]:
        """Test a database connection."""
        response = await self.client.post(f"{self.base_url}/api/v1/instances/{connection_id}/test")
        return response.json()

    async def execute_query(self, connection_id: str, sql: str) -> dict[str, Any]:
        """Execute a SQL query."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/query", json={"connection_id": connection_id, "sql": sql}
        )
        return response.json()

    async def delete_connection(self, connection_id: str) -> dict[str, Any]:
        """Delete a database connection."""
        response = await self.client.delete(f"{self.base_url}/api/v1/instances/{connection_id}")
        return response.json()


async def test_api():
    """Test the Database Chat API endpoints."""
    client = DatabaseChatAPIClient()

    try:
        print("🧪 Testing Database Chat API")
        print("=" * 40)

        # Test 1: Create a SQLite connection (in-memory)
        print("\n1. Creating SQLite connection...")
        connection_data = {
            "name": "Test SQLite DB",
            "db_type": "sqlite",
            "host": "localhost",
            "port": 5432,  # Not used for SQLite
            "database": ":memory:",
            "username": "test",
            "password": "test",
        }

        create_result = await client.create_connection(connection_data)
        print(f"✅ Connection created: {create_result}")

        if "id" not in create_result:
            print("❌ Failed to create connection - no ID returned")
            return

        connection_id = create_result["id"]

        # Test 2: List connections
        print("\n2. Listing connections...")
        connections = await client.list_connections()
        print(f"✅ Found {len(connections)} connections")

        # Test 3: Get specific connection
        print(f"\n3. Getting connection {connection_id}...")
        connection = await client.get_connection(connection_id)
        print(f"✅ Connection details: {connection['name']}")

        # Test 4: Test connection
        print(f"\n4. Testing connection {connection_id}...")
        test_result = await client.test_connection(connection_id)
        print(f"✅ Connection test: {test_result}")

        # Test 5: Execute query
        print(f"\n5. Executing query on connection {connection_id}...")
        query_result = await client.execute_query(connection_id, "SELECT 1 as test_col, 'Hello World' as message")
        print(f"✅ Query result: {query_result}")

        # Test 6: Execute a more complex query
        print(f"\n6. Executing complex query...")
        complex_query = """
        SELECT
            'Database Chat' as feature,
            42 as answer,
            datetime('now') as timestamp
        """
        complex_result = await client.execute_query(connection_id, complex_query)
        print(f"✅ Complex query result: {complex_result}")

        # Test 7: Delete connection
        print(f"\n7. Deleting connection {connection_id}...")
        delete_result = await client.delete_connection(connection_id)
        print(f"✅ Delete result: {delete_result}")

        print("\n🎉 All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()

    finally:
        await client.close()


if __name__ == "__main__":
    print("Database Chat API Test Script")
    print("Make sure the API server is running on http://localhost:8000")
    print("You can start it with: uvicorn app.main:server --host 0.0.0.0 --port 8000")

    asyncio.run(test_api())
