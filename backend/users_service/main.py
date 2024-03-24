from pymongo import MongoClient

mongo_uri = "mongodb+srv://admin:admin123123@cluster0.xrhcmq8.mongodb.net/?retryWrites=true&w=majority"

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import user_collection, user_helper
from user_models import UserSchema, UserCreateSchema
# from .database import user_collection, user_helper
# from .user_models import UserSchema, UserCreateSchema
import logging
import bcrypt
from bson import ObjectId 

app = FastAPI()

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
@app.get("/users/{user_id}", response_model=UserSchema)
async def get_user(user_id: str):
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return user_helper(user)
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.post("/users/", response_model=UserSchema)
async def create_user(user: UserCreateSchema):
    logger.info(f"Attempting to create user: {user.username}")
    existing_user = await user_collection.find_one({"username": user.username})
    if existing_user:
        logger.warning(f"Username {user.username} already registered")
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    try:
        new_user = await user_collection.insert_one({
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": hashed_password.decode('utf-8')
        })
        created_user = await user_collection.find_one({"_id": new_user.inserted_id})
        logger.info(f"User {user.username} created successfully")

        # Add this part to return the user's ID in the response
        user_id = str(new_user.inserted_id)
        return {"user_id": user_id, **user_helper(created_user)}

    except Exception as e:
        logger.error(f"Error creating user {user.username}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_collection.find_one({"username": form_data.username})
    if not user or not bcrypt.checkpw(form_data.password.encode('utf-8'), user["hashed_password"].encode('utf-8')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    # The following line should include 'user_id' in the response
    return {"access_token": user["username"], "token_type": "bearer", "user_id": str(user["_id"])}

# Additional endpoints and functions as needed...

