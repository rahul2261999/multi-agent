from fastapi import APIRouter

from src.apis.voice import voice_router
from src.apis.chat import chat_router


# Aggregate all API routers here
api_router = APIRouter()

# Keep websocket under /api/v1/websocket (no sub-prefix)
api_router.include_router(voice_router, prefix="/voice")
api_router.include_router(chat_router, prefix="/chat")

@api_router.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    """Simple health-check endpoint."""
    return {"status": "ok"}




