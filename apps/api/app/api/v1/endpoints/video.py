from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import jwt
import time

from app.core.config import settings
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

class TokenRequest(BaseModel):
    channel_id: str
    user_id: str
    username: str

class RoomRequest(BaseModel):
    channel_id: str
    name: str

@router.post("/token")
async def get_video_token(
    token_request: TokenRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate LiveKit access token for video calls"""
    
    # Verify user owns the request
    if token_request.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch"
        )
    
    # Create room name from channel ID
    room_name = f"channel_{token_request.channel_id}"
    
    # Create JWT payload for LiveKit
    now = int(time.time())
    payload = {
        "iss": settings.livekit_api_key,
        "sub": token_request.user_id,
        "nbf": now,
        "exp": now + 3600,  # 1 hour
        "video": {
            "room": room_name,
            "roomJoin": True,
            "canPublish": True,
            "canSubscribe": True,
            "canPublishData": True
        }
    }
    
    # Generate token using PyJWT
    token = jwt.encode(
        payload,
        settings.livekit_api_secret,
        algorithm="HS256"
    )
    
    return {
        "token": token,
        "room_name": room_name,
        "identity": token_request.user_id,
        "name": token_request.username
    }

@router.post("/room")
async def create_room(
    room_request: RoomRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a LiveKit room for a channel"""
    
    room_name = f"channel_{room_request.channel_id}"
    
    # Create room using LiveKit API
    # Note: In a real implementation, you would use the LiveKit API to create rooms
    # For now, we'll just return success as LiveKit creates rooms automatically
    
    return {
        "room_name": room_name,
        "channel_id": room_request.channel_id,
        "created_by": current_user.id,
        "status": "created"
    }

@router.delete("/room/{channel_id}")
async def delete_room(
    channel_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a LiveKit room for a channel"""
    
    room_name = f"channel_{channel_id}"
    
    # Delete room using LiveKit API
    # Note: In a real implementation, you would use the LiveKit API to delete rooms
    
    return {
        "room_name": room_name,
        "channel_id": channel_id,
        "deleted_by": current_user.id,
        "status": "deleted"
    }

@router.get("/room/{channel_id}/participants")
async def get_room_participants(
    channel_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get participants in a LiveKit room"""
    
    room_name = f"channel_{channel_id}"
    
    # Get participants using LiveKit API
    # Note: In a real implementation, you would use the LiveKit API to get participants
    
    return {
        "room_name": room_name,
        "channel_id": channel_id,
        "participants": []  # Placeholder
    } 