from pymongo import MongoClient

mongo_uri = "mongodb+srv://admin:admin123123@cluster0.xrhcmq8.mongodb.net/?retryWrites=true&w=majority"

from pydantic import BaseModel
from typing import Optional
from uuid import UUID  # Corrected import

class PostBase(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    image_id: Optional[str] = None

class PostCreate(PostBase):
    user_id: str

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_id: Optional[str] = None

class PostSchema(PostBase):
    id: str
    user_id: str
    
class ReplyCreate(BaseModel):
    post_id: str
    user_id: str
    content: str

class ReplySchema(ReplyCreate):
    id: str   

    class Config:
        orm_mode = True