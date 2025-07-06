from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from bson import ObjectId

from app.core.database import get_db
from app.models.channel import ChannelCreate, Channel, ChannelUpdate
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

def transform_channel_data(channel_data):
    """Transform MongoDB channel data to match Channel model"""
    channel_dict = dict(channel_data)
    channel_dict["id"] = str(channel_dict.pop("_id"))
    channel_dict["created_by"] = str(channel_dict["created_by"])
    return channel_dict

@router.get("/", response_model=List[Channel])
async def get_channels(current_user: User = Depends(get_current_user)):
    db = get_db()
    channels = []
    async for channel in db.channels.find():
        # Get message count
        message_count = await db.messages.count_documents({"channel_id": str(channel["_id"])})
        channel["message_count"] = message_count
        channels.append(Channel(**transform_channel_data(channel)))
    return channels

@router.post("/", response_model=Channel)
async def create_channel(
    channel_data: ChannelCreate,
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    # Check if channel name already exists
    existing_channel = await db.channels.find_one({"name": channel_data.name})
    if existing_channel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Channel name already exists"
        )
    
    # Create channel
    channel_dict = channel_data.dict()
    channel_dict["created_by"] = ObjectId(current_user.id)
    channel_dict["created_at"] = datetime.utcnow()
    channel_dict["updated_at"] = datetime.utcnow()
    
    result = await db.channels.insert_one(channel_dict)
    channel_dict["_id"] = result.inserted_id
    channel_dict["message_count"] = 0
    
    return Channel(**transform_channel_data(channel_dict))

@router.get("/{channel_id}", response_model=Channel)
async def get_channel(
    channel_id: str,
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    if not ObjectId.is_valid(channel_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid channel ID"
        )
    
    channel = await db.channels.find_one({"_id": ObjectId(channel_id)})
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    # Get message count
    message_count = await db.messages.count_documents({"channel_id": channel_id})
    channel["message_count"] = message_count
    
    return Channel(**transform_channel_data(channel))

@router.put("/{channel_id}", response_model=Channel)
async def update_channel(
    channel_id: str,
    channel_data: ChannelUpdate,
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    if not ObjectId.is_valid(channel_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid channel ID"
        )
    
    channel = await db.channels.find_one({"_id": ObjectId(channel_id)})
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    # Check if user is the creator
    if str(channel["created_by"]) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only channel creator can update channel"
        )
    
    # Update channel
    update_data = channel_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    await db.channels.update_one(
        {"_id": ObjectId(channel_id)},
        {"$set": update_data}
    )
    
    # Get updated channel
    updated_channel = await db.channels.find_one({"_id": ObjectId(channel_id)})
    message_count = await db.messages.count_documents({"channel_id": channel_id})
    updated_channel["message_count"] = message_count
    
    return Channel(**transform_channel_data(updated_channel))

@router.delete("/{channel_id}")
async def delete_channel(
    channel_id: str,
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    if not ObjectId.is_valid(channel_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid channel ID"
        )
    
    channel = await db.channels.find_one({"_id": ObjectId(channel_id)})
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    # Check if user is the creator
    if str(channel["created_by"]) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only channel creator can delete channel"
        )
    
    # Delete channel and all its messages
    await db.channels.delete_one({"_id": ObjectId(channel_id)})
    await db.messages.delete_many({"channel_id": channel_id})
    
    return {"message": "Channel deleted successfully"} 