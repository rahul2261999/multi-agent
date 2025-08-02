"""Main FastAPI application entrypoint for the multi-agents backend.

Run with:
    uvicorn src.main:app --reload
"""

from fastapi import FastAPI

# Import the Loguru setup helper from our library
from src.libs.logger.manager import setup_logger

# Initialise logging system
logger_manager = setup_logger()
logger = logger_manager.get_logger(__name__)

# Create the FastAPI instance
app = FastAPI(title="Multi-Agents API")


@app.on_event("startup")
async def on_startup() -> None:
    """Actions to perform when the application starts."""
    logger.info("FastAPI application is starting up …")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Actions to perform when the application shuts down."""
    logger.info("FastAPI application is shutting down …")


@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    """Simple health-check endpoint."""
    return {"status": "ok"}


# Development entry-point ----------------------------------------------------
if __name__ == "__main__":  # pragma: no cover — only used for ad-hoc runs
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
