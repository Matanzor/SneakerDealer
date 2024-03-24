# database.py
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

# MongoDB Atlas URI
mongo_uri = "mongodb+srv://admin:admin123123@cluster0.xrhcmq8.mongodb.net/?retryWrites=true&w=majority"

# For asynchronous operations using Motor
async_client = AsyncIOMotorClient(mongo_uri)
async_db = async_client['Posts_Database']  # Replace with your actual database name if different
post_collection = async_db.posts
reply_collection = async_db.reply
image_collection = async_db.images
