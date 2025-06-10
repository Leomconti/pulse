from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import database_config
from app.services.database import ping_db, sessionmanager
from app.services.redis import ping_redis


def init_app(init_db=True):
    lifespan = None  # type: ignore

    if init_db:
        sessionmanager.init(database_config.get_db_url())

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Ping to ensure they are up and connections open
            await ping_db()
            await ping_redis()
            yield
            if sessionmanager._engine is not None:
                await sessionmanager.close()

    server = FastAPI(title="Pulse - Database Chat API", lifespan=lifespan)

    # Import routers
    from app.routes.health import router as health_router
    from app.routes.instances import router as instances_router
    from app.routes.query import router as query_router

    # Include routers
    server.include_router(health_router, prefix="", tags=["health"])
    server.include_router(instances_router, prefix="/api/v1", tags=["database-connections"])
    server.include_router(query_router, prefix="/api/v1", tags=["sql-queries"])

    return server
