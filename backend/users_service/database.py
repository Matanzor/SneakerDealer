from pymongo import MongoClient

from motor.motor_asyncio import AsyncIOMotorClient

# Use the actual MongoDB Atlas URI provided
mongo_uri = "mongodb+srv://admin:admin123123@cluster0.xrhcmq8.mongodb.net/?retryWrites=true&w=majority"

# Initialize the client to connect to your MongoDB cluster
client = AsyncIOMotorClient(mongo_uri)

# Connect to the specific database, you should replace 'your_db_name' with your actual database name
database = client.Users_Database

# Connect to the specific collection, for example 'users_collection' for the users service
user_collection = database.get_collection("users_collection")

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "hashed_password": user["hashed_password"]
    }

