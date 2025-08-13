"""Main FastAPI application entrypoint for the multi-agents backend.

Run with:
    uvicorn src.main:app --reload
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

# Import the Loguru setup helper from our library
from src.libs.logger.manager import get_logger
from src.libs.redis import get_redis_client, init_checkpoint_saver


# Initialise logging system``
logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI application is starting up …")
    # Initialize Redis connection early and verify connectivity
    try:
        redis_client = get_redis_client()
        await redis_client.ping()
        await init_checkpoint_saver()  # ensure checkpoint saver is initialized
        logger.info("Connected to Redis successfully and initialized checkpoint saver")

        # Register routes only AFTER Redis is initialized
        from src.apis.main import api_router
        app.include_router(api_router, prefix="/api/v1")
        

    except Exception as exc:
        logger.error(f"Failed to connect to Redis on startup: {exc}")
        raise

    yield

    logger.info("FastAPI application is shutting down …")

    await redis_client.close()  


# Create the FastAPI instance with lifespan handler
app = FastAPI(title="Multi-Agents API", lifespan=lifespan)

# Development entry-point ----------------------------------------------------
if __name__ == "__main__":  # pragma: no cover — only used for ad-hoc runs
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
