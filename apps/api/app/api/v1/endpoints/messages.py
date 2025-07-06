from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from bson import ObjectId

from app.core.database import get_db
from app.models.message import MessageCreate, Message, MessageUpdate, ReactionCreate
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

def transform_message_data(message_data):
    """Transform MongoDB message data to match Message model"""
    message_dict = dict(message_data)
    message_dict["id"] = str(message_dict.pop("_id"))
    return message_dict

@router.get("/channels/{channel_id}/messages", response_model=List[Message])
async def get_messages(
    channel_id: str,
    limit: int = 50,
    skip: int = 0,
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    if not ObjectId.is_valid(channel_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid channel ID"
        )
    
    # Check if channel exists
    channel = await db.channels.find_one({"_id": ObjectId(channel_id)})
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    # Get messages with user data
    messages = []
    cursor = db.messages.find({"channel_id": channel_id}).sort("created_at", -1).skip(skip).limit(limit)
    
    async for message in cursor:
        # Get user data
        user = await db.users.find_one({"_id": message["user_id"]})
        if user:
            message["user"] = {
                "id": str(user["_id"]),
                "username": user["username"],
                "avatar": user.get("avatar")
            }
        
        # Get thread messages if any
        thread_messages = []
        thread_cursor = db.messages.find({"thread_id": message["_id"]}).sort("created_at", 1)
        async for thread_msg in thread_cursor:
            thread_user = await db.users.find_one({"_id": thread_msg["user_id"]})
            if thread_user:
                thread_msg["user"] = {
                    "id": str(thread_user["_id"]),
                    "username": thread_user["username"],
                    "avatar": thread_user.get("avatar")
                }
                thread_messages.append(Message(**transform_message_data(thread_msg)))
        
        message["thread"] = thread_messages
        messages.append(Message(**transform_message_data(message)))
    
    # Reverse to get chronological order
    messages.reverse()
    return messages

@router.post("/channels/{channel_id}/messages", response_model=Message)
async def create_message(
    channel_id: str,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    if not ObjectId.is_valid(channel_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid channel ID"
        )
    
    # Check if channel exists
    channel = await db.channels.find_one({"_id": ObjectId(channel_id)})
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    # Create message
    message_dict = message_data.dict()
    message_dict["channel_id"] = channel_id
    message_dict["user_id"] = ObjectId(current_user.id)
    message_dict["created_at"] = datetime.utcnow()
    message_dict["updated_at"] = datetime.utcnow()
    message_dict["reactions"] = []
    
    result = await db.messages.insert_one(message_dict)
    message_dict["_id"] = result.inserted_id
    message_dict["user"] = {
        "id": current_user.id,
        "username": current_user.username,
        "avatar": current_user.avatar
    }
    message_dict["thread"] = []
    
    return Message(**transform_message_data(message_dict))

@router.post("/messages/{message_id}/reactions", response_model=Message)
async def add_reaction(
    message_id: str,
    reaction_data: ReactionCreate,
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    if not ObjectId.is_valid(message_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid message ID"
        )
    
    # Check if message exists
    message = await db.messages.find_one({"_id": ObjectId(message_id)})
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check if user already reacted with this emoji
    existing_reaction = None
    for reaction in message.get("reactions", []):
        if reaction["emoji"] == reaction_data.emoji:
            existing_reaction = reaction
            break
    
    if existing_reaction:
        # Toggle reaction
        if current_user.id in existing_reaction["users"]:
            # Remove reaction
            existing_reaction["users"].remove(current_user.id)
            existing_reaction["count"] -= 1
            if existing_reaction["count"] == 0:
                message["reactions"].remove(existing_reaction)
        else:
            # Add reaction
            existing_reaction["users"].append(current_user.id)
            existing_reaction["count"] += 1
    else:
        # Create new reaction
        new_reaction = {
            "_id": ObjectId(),
            "emoji": reaction_data.emoji,
            "count": 1,
            "users": [current_user.id]
        }
        if "reactions" not in message:
            message["reactions"] = []
        message["reactions"].append(new_reaction)
    
    # Update message
    await db.messages.update_one(
        {"_id": ObjectId(message_id)},
        {"$set": {"reactions": message["reactions"]}}
    )
    
    # Get updated message with user data
    updated_message = await db.messages.find_one({"_id": ObjectId(message_id)})
    user = await db.users.find_one({"_id": updated_message["user_id"]})
    if user:
        updated_message["user"] = {
            "id": str(user["_id"]),
            "username": user["username"],
            "avatar": user.get("avatar")
        }
    
    updated_message["thread"] = []
    
    return Message(**transform_message_data(updated_message))

@router.put("/messages/{message_id}", response_model=Message)
async def update_message(
    message_id: str,
    message_data: MessageUpdate,
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    if not ObjectId.is_valid(message_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid message ID"
        )
    
    # Check if message exists and user owns it
    message = await db.messages.find_one({"_id": ObjectId(message_id)})
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    if str(message["user_id"]) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only message author can edit message"
        )
    
    # Update message
    update_data = message_data.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    await db.messages.update_one(
        {"_id": ObjectId(message_id)},
        {"$set": update_data}
    )
    
    # Get updated message
    updated_message = await db.messages.find_one({"_id": ObjectId(message_id)})
    user = await db.users.find_one({"_id": updated_message["user_id"]})
    if user:
        updated_message["user"] = {
            "id": str(user["_id"]),
            "username": user["username"],
            "avatar": user.get("avatar")
        }
    
    updated_message["thread"] = []
    
    return Message(**transform_message_data(updated_message))

@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    if not ObjectId.is_valid(message_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid message ID"
        )
    
    # Check if message exists and user owns it
    message = await db.messages.find_one({"_id": ObjectId(message_id)})
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    if str(message["user_id"]) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only message author can delete message"
        )
    
    # Delete message and its thread
    await db.messages.delete_many({
        "$or": [
            {"_id": ObjectId(message_id)},
            {"thread_id": ObjectId(message_id)}
        ]
    })
    
    return {"message": "Message deleted successfully"} 