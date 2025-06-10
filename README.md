# Pulse - Intelligent Database Chat API

A sophisticated "chat with database" API built with FastAPI, Redis, and multi-agent AI workflows. This API provides both direct SQL execution capabilities and intelligent natural language to SQL conversion through an agentic pipeline.

## 🚀 Features

### Core Database Features

- **Multi-database support**: PostgreSQL, MySQL, and SQLite
- **Connection management**: Store, validate, and manage database connections securely
- **SQL execution**: Execute queries with proper error handling and performance monitoring
- **Redis storage**: All connections stored in Redis with proper serialization
- **Type safety**: Full Pydantic model validation throughout

### 🤖 Intelligent Agent Workflow

- **Natural Language Processing**: Convert plain English queries to SQL using AI agents
- **Multi-Agent Pipeline**: Four specialized agents working in coordination:
  - **Planner**: Parse natural language into structured intent
  - **Mapper**: Map entities to database schema
  - **Composer**: Generate SQL from structured representation
  - **Validator**: Validate and refine generated SQL
- **DAG-based Orchestration**: Workflow orchestrator manages agent dependencies and execution
- **Feedback Loops**: Automatic retry mechanism with validation feedback
- **Real-time Status**: Track workflow progress with WebSocket-like updates
- **State Persistence**: Complete workflow state stored in Redis with recovery capabilities


<img width="1438" alt="image" src="https://github.com/user-attachments/assets/ed941df8-37d1-4696-b189-53b8663e22c0" />
<img width="1438" alt="image" src="https://github.com/user-attachments/assets/69790253-5a25-4482-aa99-e2920a2ecb48" />
<img width="1438" alt="image" src="https://github.com/user-attachments/assets/835972d9-2e71-4d06-bb6c-fbf09040b302" />


## 🏗️ Architecture

### Core Components

1. **Models** (`app/models.py`): Pydantic models for type safety and validation
2. **Redis Operations** (`app/services/redis_ops.py`): Generic Redis operations for BaseModel types
3. **SQL Runner** (`app/services/sql_runner.py`): Database query execution with connection pooling
4. **Workflow Orchestrator** (`app/orchestrator.py`): DAG-based agent coordination system
5. **AI Agents** (`app/agents/`): Specialized processing agents
6. **LLM Clients** (`app/llm_clients/`): OpenAI integration for structured AI calls
7. **API Routes**:
   - `app/routes/instances.py`: Database connection management
   - `app/routes/query.py`: Direct SQL query execution
   - `app/routes/workflow.py`: Agent workflow management
   - `app/routes/frontend.py`: Web interface for testing

### Agent Workflow Data Flow

```
Natural Language Query → Planner Agent → Mapper Agent → Composer Agent → Validator Agent → SQL + Results
                            ↓              ↓             ↓              ↓
                       Intent Analysis  Schema Mapping  SQL Generation  Validation & Retry Loop
```

### Traditional Data Flow

```
API Request → Pydantic Validation → Redis Storage/Retrieval → SQL Execution → Structured Response
```

## 🛠️ Setup

### Prerequisites

- Python 3.12+
- Redis server
- Target databases (PostgreSQL, MySQL, SQLite)
- OpenAI API key (for agent workflows)

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

# Redis (for connection storage and workflow state)
REDIS_URL=redis://localhost:6379/0

# OpenAI (for agent workflows)
OPENAI_API_KEY=your_openai_api_key

# Logfire (optional, for monitoring)
LOGFIRE_TOKEN=your_logfire_token
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

### 🤖 Agent Workflow Endpoints

#### Start Natural Language Workflow

```http
POST /api/v1/workflows
Content-Type: application/json

{
  "query": "Show me all users who registered last month",
  "schema": {
    "users": {
      "id": "integer",
      "name": "varchar",
      "email": "varchar",
      "created_at": "timestamp"
    }
  },
  "user_id": "optional-user-id"
}
```

**Response**:

```json
{
  "request_id": "uuid-workflow-id"
}
```

#### Start Workflow with Database Connection

```http
POST /api/v1/workflows/start-with-connection
Content-Type: application/x-www-form-urlencoded

query=Show me all high-value customers
connection_id=your-db-connection-uuid
```

#### Get Workflow Status

```http
GET /api/v1/workflows/{request_id}/status
```

**Response**:

```json
{
  "status": "running",
  "current": "composer"
}
```

#### Get Detailed Workflow Steps

```http
GET /api/v1/workflows/{request_id}/steps
```

**Response**:

```json
[
  {
    "name": "planner",
    "status": "done",
    "output": {
      "intent": "select",
      "entities": [{ "name": "users", "type": "table" }],
      "filters": [{ "column": "created_at", "operator": ">", "value": "2024-01-01" }]
    },
    "started_at": 1703001600.0,
    "finished_at": 1703001602.0
  },
  {
    "name": "mapper",
    "status": "running",
    "output": null,
    "started_at": 1703001602.0,
    "finished_at": null
  }
]
```

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

## 🎯 Agent System Deep Dive

### Agent Architecture

The workflow system uses four specialized agents in a DAG (Directed Acyclic Graph):

1. **Planner Agent** (`app/agents/planner.py`)

   - **Purpose**: Parse natural language into structured intent
   - **Input**: Raw user query + database schema
   - **Output**: Intent, entities, filters, aggregations
   - **Dependencies**: None (entry point)

2. **Mapper Agent** (`app/agents/mapper.py`)

   - **Purpose**: Map identified entities to actual database schema
   - **Input**: Planner output + database schema
   - **Output**: Validated table/column mappings
   - **Dependencies**: Planner output

3. **Composer Agent** (`app/agents/composer.py`)

   - **Purpose**: Generate SQL query from structured representation
   - **Input**: Mapped entities + planner intent
   - **Output**: Complete SQL query
   - **Dependencies**: Planner + Mapper outputs

4. **Validator Agent** (`app/agents/validator.py`)
   - **Purpose**: Validate and refine generated SQL
   - **Input**: Generated SQL + database schema
   - **Output**: Validation results + refined SQL
   - **Dependencies**: All previous outputs

### Workflow Orchestration

The `WorkflowOrchestrator` (`app/orchestrator.py`) manages:

- **Dependency Resolution**: Ensures agents execute in correct order
- **State Persistence**: Saves workflow state to Redis after each step
- **Error Handling**: Captures and reports agent failures
- **Retry Logic**: Implements feedback loops for validation failures
- **Concurrency**: Supports multiple concurrent workflows

### Feedback Loop System

When the Validator agent identifies issues:

1. **Validation Failure**: Validator returns `is_valid: false` with feedback
2. **Retry Decision**: Orchestrator checks retry count vs. max retries
3. **Targeted Retry**: Re-executes only Composer → Validator path
4. **Iterative Improvement**: Process repeats until valid or max retries reached

## 🧪 Testing

### Automated Tests

Run the test script to verify all functionality:

```bash
# Start the server first
uvicorn app.main:server --host 0.0.0.0 --port 8000

# Run tests in another terminal
python test_api.py
```

### Workflow Testing

Test the agent workflow system:

```bash
python test_workflow.py
```

### Manual Testing

1. **FastAPI Interactive Docs**: `http://localhost:8000/docs`
2. **Web Interface**: `http://localhost:8000/` (includes workflow testing UI)

## 🔒 Security Features

- **Input Validation**: All inputs validated with Pydantic models
- **SQL Injection Protection**: Parameterized queries and input sanitization
- **Connection Isolation**: Each query uses its own connection context
- **Error Handling**: Detailed error messages without exposing sensitive information
- **Password Security**: Passwords not returned in API responses
- **Agent Safety**: LLM outputs validated and sanitized before SQL execution

## 🏆 Production Considerations

### Performance

- Connection pooling for database operations
- Redis for fast metadata and state retrieval
- Async/await throughout for non-blocking operations
- Query execution time monitoring
- Agent execution parallelization where possible

### Reliability

- Comprehensive error handling at all layers
- Connection validation before saving
- Graceful degradation on connection failures
- Workflow state recovery from Redis
- Agent failure isolation and recovery

### Scalability

- Stateless API design (except workflow state in Redis)
- Redis as external state store
- Horizontal scaling ready
- Connection pooling with limits
- Distributed workflow execution capable

### Monitoring

- Execution time tracking for all components
- Agent performance metrics
- Workflow success/failure rates
- Error categorization and alerting
- Logfire integration for observability

## 🚦 Health Checks

```http
GET /health
```

Returns API and dependency status including Redis and database connectivity.

## 📝 Development

### Code Structure

```
app/
├── models.py                 # Pydantic models
├── config.py                # Configuration management
├── orchestrator.py          # Workflow orchestration engine
├── agents/                  # AI agent implementations
│   ├── __init__.py
│   ├── planner.py          # Intent parsing agent
│   ├── mapper.py           # Schema mapping agent
│   ├── composer.py         # SQL generation agent
│   └── validator.py        # SQL validation agent
├── llm_clients/            # LLM integration
│   └── openai_client.py    # OpenAI structured calls
├── services/
│   ├── redis_ops.py        # Generic Redis operations
│   ├── sql_runner.py       # SQL execution logic
│   └── redis.py            # Redis client setup
├── routes/
│   ├── instances.py        # Connection management
│   ├── query.py            # Direct query execution
│   ├── workflow.py         # Agent workflow endpoints
│   ├── frontend.py         # Web interface
│   └── health.py           # Health checks
└── templates/              # HTML templates for web UI
    └── partials/           # HTMX partial templates
```

### Adding New Agents

1. Create agent file in `app/agents/`
2. Implement agent function with signature: `async def agent_name(ctx: Context) -> Context`
3. Define requirements list: `requires = ["dependency1", "dependency2"]`
4. Register in `orchestrator.py` workflow DAG
5. Update `app/agents/__init__.py` exports

### Adding New Database Types

1. Update `DatabaseType` enum in `models.py`
2. Add connection URL generation in `DatabaseConnection.get_connection_url()`
3. Add specific driver to dependencies in `pyproject.toml`
4. Update SQL runner if database-specific optimizations needed

### Redis Key Structure

```
DatabaseConnection:{uuid} → JSON serialized connection data
workflow:{request_id} → JSON serialized workflow context
```

PRIVATE PROJECT DONT COPY WITHOUT PERMISSION
