from pymongo import MongoClient

mongo_uri = "mongodb+srv://admin:admin123123@cluster0.xrhcmq8.mongodb.net/?retryWrites=true&w=majority"

from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Any, Optional

class PostDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    content: str
    owner_id: PyObjectId

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "title": "Post Title",
                "content": "Post content here...",
                "owner_id": "ObjectId of the user"
            }
        }

