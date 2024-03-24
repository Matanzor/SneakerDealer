from pymongo import MongoClient

mongo_uri = "mongodb+srv://admin:admin123123@cluster0.xrhcmq8.mongodb.net/?retryWrites=true&w=majority"

# schemas.py or user_models.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserSchema(BaseModel):
    id: Optional[str] = None
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreateSchema(UserSchema):
    password: str

