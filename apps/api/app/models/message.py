from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.with_info_plain_validator_function(
            cls.validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class Reaction(BaseModel):
    id: PyObjectId = PyObjectId()
    emoji: str
    count: int = 1
    users: List[str] = []

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)

class MessageInDB(BaseModel):
    id: PyObjectId = PyObjectId()
    content: str
    channel_id: str
    user_id: PyObjectId
    reactions: List[Reaction] = []
    thread_id: Optional[PyObjectId] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

class Message(BaseModel):
    id: str
    content: str
    channel_id: str
    user: dict
    reactions: List[Reaction] = []
    thread: Optional[List['Message']] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

class ReactionCreate(BaseModel):
    emoji: str = Field(..., min_length=1, max_length=10) 