from pymongo import MongoClient

mongo_uri = "mongodb+srv://admin:admin123123@cluster0.xrhcmq8.mongodb.net/?retryWrites=true&w=majority"

# posts-service/utils.py
import httpx
import os

USERS_SERVICE_URL = os.getenv('USERS_SERVICE_URL', 'http://users-service:8000')

def get_user(user_id: int):
    try:
        response = httpx.get(f'{USERS_SERVICE_URL}/users/{user_id}')
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError:
        print(f"Failed to fetch user with ID {user_id}")
        return None

