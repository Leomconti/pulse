from contextlib import asynccontextmanager

import logfire
from fastapi import FastAPI

from app.config import database_config, logfire_config
from app.llm_clients.openai_client import openai_client
from app.routes.frontend import router as frontend_router

# Import routers
from app.routes.health import router as health_router
from app.routes.instances import router as instances_router
from app.routes.mock_data import router as mock_data_router
from app.routes.query import router as query_router
from app.routes.workflow import router as workflow_router
from app.services.database import ping_db, sessionmanager
from app.services.redis import ping_redis

# lifespan = None  # type: ignore

# if init_db:
# Check env for this
sessionmanager.init(database_config.get_db_url())


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ping to ensure they are up and connections open
    await ping_db()
    await ping_redis()
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()


app = FastAPI(title="Pulse - Database Chat API", lifespan=lifespan)

# Include routers
app.include_router(frontend_router, prefix="", tags=["frontend"])
app.include_router(health_router, prefix="", tags=["health"])
app.include_router(instances_router, prefix="/api/v1", tags=["database-connections"])
app.include_router(query_router, prefix="/api/v1", tags=["sql-queries"])
app.include_router(mock_data_router, prefix="/api/v1", tags=["mock-data"])
app.include_router(workflow_router, prefix="/api/v1", tags=["workflows"])


logfire.configure(token=logfire_config.LOGFIRE_TOKEN, environment="local")
logfire.instrument_fastapi(app, excluded_urls=["/api/v1/workflows/*/steps-htmx"])
logfire.instrument_openai(openai_client.client)
