# Pulse - Database Chat API

A rock-solid "chat with database" API built with FastAPI, Redis, and modern Python patterns. This API allows you to manage database connections and execute SQL queries through clean REST endpoints.

## 🚀 Features

- **Multi-database support**: PostgreSQL, MySQL, and SQLite
- **Connection management**: Store, validate, and manage database connections securely
- **SQL execution**: Execute queries with proper error handling and performance monitoring
- **Redis storage**: All connections stored in Redis with proper serialization
- **Type safety**: Full Pydantic model validation throughout
- **Production-ready**: Comprehensive error handling, logging, and security practices

## 🏗️ Architecture

### Core Components

1. **Models** (`app/models.py`): Pydantic models for type safety and validation
2. **Redis Operations** (`app/services/redis_ops.py`): Generic Redis operations for BaseModel types
3. **SQL Runner** (`app/services/sql_runner.py`): Database query execution with connection pooling
4. **API Routes**:
   - `app/routes/instances.py`: Database connection management
   - `app/routes/query.py`: SQL query execution

### Data Flow

```
API Request → Pydantic Validation → Redis Storage/Retrieval → SQL Execution → Structured Response
```

## 🛠️ Setup

### Prerequisites

- Python 3.12+
- Redis server
- Target databases (PostgreSQL, MySQL, SQLite)

### Installation

1. **Clone and setup environment**:

```bash
git clone <repository-url>
cd pulse
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies**:

```bash
uv sync --dev
```

3. **Environment configuration**:
   Create a `.env` file:

```env
# Database (for app metadata, not chat targets)
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pulse

# Redis (for connection storage)
REDIS_URL=redis://localhost:6379/0
```

4. **Start services**:

```bash
# Start Redis (if using Docker)
docker run -d -p 6379:6379 redis:7-alpine

# Start the API server
uvicorn app.main:server --host 0.0.0.0 --port 8000 --reload
```

## 📚 API Reference

### Base URL

All endpoints are prefixed with `/api/v1`

### Database Connections

#### Create Connection

```http
POST /api/v1/instances
Content-Type: application/json

{
  "name": "My PostgreSQL DB",
  "db_type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "username": "user",
  "password": "password"
}
```

**Response**:

```json
{
  "id": "uuid-here",
  "name": "My PostgreSQL DB",
  "db_type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "username": "user",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

#### List Connections

```http
GET /api/v1/instances
```

#### Get Connection

```http
GET /api/v1/instances/{connection_id}
```

#### Update Connection

```http
PUT /api/v1/instances/{connection_id}
Content-Type: application/json

{
  "name": "Updated DB Name",
  "port": 5433
}
```

#### Delete Connection

```http
DELETE /api/v1/instances/{connection_id}
```

#### Test Connection

```http
POST /api/v1/instances/{connection_id}/test
```

### SQL Query Execution

#### Execute Query

```http
POST /api/v1/query
Content-Type: application/json

{
  "connection_id": "uuid-here",
  "sql": "SELECT * FROM users LIMIT 10"
}
```

**Response**:

```json
{
  "status": "ok",
  "data": {
    "columns": ["id", "name", "email"],
    "rows": [
      [1, "John Doe", "john@example.com"],
      [2, "Jane Smith", "jane@example.com"]
    ],
    "row_count": 2,
    "execution_time_ms": 45.23
  },
  "error": null
}
```

**Error Response**:

```json
{
  "status": "error",
  "data": null,
  "error": "SQL execution failed: table 'users' does not exist"
}
```

#### Alternative Query Endpoint

```http
POST /api/v1/instances/{connection_id}/query
Content-Type: application/json

{
  "sql": "SELECT COUNT(*) FROM products"
}
```

## 🧪 Testing

### Automated Tests

Run the test script to verify all functionality:

```bash
# Start the server first
uvicorn app.main:server --host 0.0.0.0 --port 8000

# Run tests in another terminal
python test_api.py
```

### Manual Testing

Use the FastAPI interactive docs at `http://localhost:8000/docs` to test endpoints manually.

## 🔒 Security Features

- **Input Validation**: All inputs validated with Pydantic models
- **SQL Injection Protection**: Parameterized queries and input sanitization
- **Connection Isolation**: Each query uses its own connection context
- **Error Handling**: Detailed error messages without exposing sensitive information
- **Password Security**: Passwords not returned in API responses

## 🏆 Production Considerations

### Performance

- Connection pooling for database operations
- Redis for fast connection metadata retrieval
- Async/await throughout for non-blocking operations
- Query execution time monitoring

### Reliability

- Comprehensive error handling at all layers
- Connection validation before saving
- Graceful degradation on connection failures
- Transaction safety where applicable

### Scalability

- Stateless API design
- Redis as external state store
- Horizontal scaling ready
- Connection pooling with limits

### Monitoring

- Execution time tracking
- Error categorization
- Health check endpoints

## 🚦 Health Checks

```http
GET /health
```

Returns API and dependency status.

## 📝 Development

### Code Structure

```
app/
├── models.py              # Pydantic models
├── config.py             # Configuration management
├── services/
│   ├── redis_ops.py      # Generic Redis operations
│   ├── sql_runner.py     # SQL execution logic
│   └── redis.py          # Redis client setup
└── routes/
    ├── instances.py      # Connection management
    ├── query.py          # Query execution
    └── health.py         # Health checks
```

### Adding New Database Types

1. Update `DatabaseType` enum in `models.py`
2. Add connection URL generation in `DatabaseConnection.get_connection_url()`
3. Add specific driver to dependencies in `pyproject.toml`
4. Update SQL runner if database-specific optimizations needed

### Redis Key Structure

```
DatabaseConnection:{uuid} → JSON serialized connection data
```

## 🤝 Contributing

1. Follow the existing code patterns
2. Add comprehensive error handling
3. Update tests for new features
4. Maintain type safety with Pydantic models
5. Follow the project's async/await patterns

## 📄 License

This project is licensed under the MIT License.
