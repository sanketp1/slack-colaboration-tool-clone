from bson import ObjectId
from typing import Optional, Dict, Any

async def get_user_by_email(db, email: str) -> Optional[Dict[str, Any]]:
    return await db.users.find_one({"email": email})

async def get_user_by_username(db, username: str) -> Optional[Dict[str, Any]]:
    return await db.users.find_one({"username": username})

async def get_user_by_id(db, user_id: str) -> Optional[Dict[str, Any]]:
    return await db.users.find_one({"_id": ObjectId(user_id)})

async def create_user(db, user_data: Dict[str, Any]) -> ObjectId:
    result = await db.users.insert_one(user_data)
    return result.inserted_id

async def update_user(db, user_id: str, update_data: Dict[str, Any]) -> bool:
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0

async def delete_user(db, user_id: str) -> bool:
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0 