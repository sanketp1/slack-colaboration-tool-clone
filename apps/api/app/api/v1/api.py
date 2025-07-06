from fastapi import APIRouter
from app.api.v1.endpoints import auth, channels, messages, files, video

api_router = APIRouter()

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "slack-clone-api"}

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(channels.router, prefix="/channels", tags=["channels"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(video.router, prefix="/video", tags=["video"]) 