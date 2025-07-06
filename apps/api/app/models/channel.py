from pydantic import BaseModel
from typing import Optional
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

class ChannelBase(BaseModel):
    name: str
    description: Optional[str] = None

class ChannelCreate(ChannelBase):
    pass

class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ChannelInDB(ChannelBase):
    id: PyObjectId = PyObjectId()
    created_by: PyObjectId
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

class Channel(ChannelBase):
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True 