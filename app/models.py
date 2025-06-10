import time
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class DatabaseType(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


class DatabaseConnection(BaseModel):
    """Database connection configuration stored in Redis."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    db_type: DatabaseType
    host: str = Field(..., min_length=1)
    port: int = Field(..., ge=1, le=65535)
    database: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

    @field_validator("port")
    def validate_port(cls, v):
        if v <= 0 or v > 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    def get_connection_url(self) -> str:
        """Generate database connection URL based on type."""
        if self.db_type == DatabaseType.POSTGRESQL:
            return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == DatabaseType.MYSQL:
            return f"mysql+aiomysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == DatabaseType.SQLITE:
            # For SQLite, handle special cases like :memory: and file paths
            if self.database == ":memory:":
                return "sqlite+aiosqlite:///:memory:"
            elif self.database.startswith("/") or self.database.startswith("./"):
                # Absolute or relative path
                return f"sqlite+aiosqlite:///{self.database}"
            else:
                # Relative filename
                return f"sqlite+aiosqlite:///./{self.database}"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")


class QueryResult(BaseModel):
    """Result of a SQL query execution."""

    columns: list[str] = Field(default_factory=list)
    rows: list[list[Any]] = Field(default_factory=list)
    row_count: int = 0
    execution_time_ms: float = 0.0


class QueryRequest(BaseModel):
    """Request payload for SQL query execution."""

    connection_id: str = Field(..., min_length=1)
    sql: str = Field(..., min_length=1)


class QueryResponse(BaseModel):
    """Response for SQL query execution."""

    status: str = Field(..., pattern="^(ok|error)$")
    data: Optional[QueryResult] = None
    error: Optional[str] = None


class DatabaseConnectionCreate(BaseModel):
    """Request payload for creating a database connection."""

    name: str = Field(..., min_length=1, max_length=100)
    db_type: DatabaseType
    host: str = Field(..., min_length=1)
    port: int = Field(..., ge=1, le=65535)
    database: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class DatabaseConnectionUpdate(BaseModel):
    """Request payload for updating a database connection."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    db_type: Optional[DatabaseType] = None
    host: Optional[str] = Field(None, min_length=1)
    port: Optional[int] = Field(None, ge=1, le=65535)
    database: Optional[str] = Field(None, min_length=1)
    username: Optional[str] = Field(None, min_length=1)
    password: Optional[str] = Field(None, min_length=1)


class DatabaseConnectionResponse(BaseModel):
    """Response payload for database connection (without sensitive data)."""

    id: str
    name: str
    db_type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    created_at: float
    updated_at: float

    @classmethod
    def from_connection(cls, connection: DatabaseConnection) -> "DatabaseConnectionResponse":
        """Create response model from database connection, excluding password."""
        return cls(
            id=connection.id,
            name=connection.name,
            db_type=connection.db_type,
            host=connection.host,
            port=connection.port,
            database=connection.database,
            username=connection.username,
            created_at=connection.created_at,
            updated_at=connection.updated_at,
        )


# Agentic Workflow Models


class Entity(BaseModel):
    name: str
    type: str  # e.g., "table", "column", "filter", "aggregation"


class Filter(BaseModel):
    column: str
    operator: str  # e.g., "=", ">", "<", "LIKE"
    value: str


class Aggregation(BaseModel):
    function: str  # e.g., "COUNT", "SUM", "AVG"
    column: str


class PlannerOutput(BaseModel):
    intent: str  # e.g., "select", "aggregate", "filter"
    entities: list[Entity]
    filters: list[Filter]
    aggregations: list[Aggregation]
    limit: Optional[int] = None
    order_by: Optional[str] = None


class MappedEntity(BaseModel):
    entity_name: str
    table: str
    column: Optional[str] = None


class MappedFilter(BaseModel):
    filter: Filter
    mapped_column: str


class MappedAggregation(BaseModel):
    aggregation: Aggregation
    mapped_column: str


class MapperOutput(BaseModel):
    mapped_entities: list[MappedEntity]
    mapped_filters: list[MappedFilter]
    mapped_aggregations: list[MappedAggregation]
    mapped_order_by: Optional[str] = None


class ComposerOutput(BaseModel):
    sql_query: str


class ValidationResult(BaseModel):
    is_valid: bool
    errors: Optional[list[str]] = None
    feedback: Optional[str] = None
    query_output: Optional[str] = None  # Result or error from query execution


class ValidatorOutput(BaseModel):
    validation: ValidationResult


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class Context(BaseModel):
    """Shared context model that holds all workflow state."""

    request_id: UUID = Field(default_factory=uuid4)
    query: str
    schema: dict

    # Agent outputs
    planner_output: Optional[PlannerOutput] = None
    mapper_output: Optional[MapperOutput] = None
    composer_output: Optional[ComposerOutput] = None
    validator_output: Optional[ValidatorOutput] = None

    # Workflow metadata
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: Optional[str] = None
    feedback: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

    # Timestamps
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

    # Optional user metadata
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = time.time()

    def to_dict(self) -> dict:
        """Convert to dictionary for Redis storage."""
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict) -> "Context":
        """Create from dictionary loaded from Redis."""
        return cls.model_validate(data)
