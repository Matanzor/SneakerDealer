# backend/posts_service/tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from .main import app  
from .database import post_collection  
from unittest.mock import AsyncMock, patch, MagicMock
from bson.objectid import ObjectId
from pymongo.results import DeleteResult


client = TestClient(app)

async def mock_find_one(filter):
    # Return a complete post object that matches PostSchema
    return {
        "_id": "mock_id",
        "title": "Test Title",
        "content": "Test Content",
        "user_id": "user123",
    }

# Sample data for testing search posts
test_post_data = [
    {
        "title": "Test Post 1",
        "content": "Content of test post 1",
        "category": "Test Category",
        "user_id": "user123",
        "_id": "post123"
    },
    {
        "title": "Test Post 2",
        "content": "Content of test post 2",
        "category": "Test Category",
        "user_id": "user456",
        "_id": "post456"
    }
]

test_post_delete_data = {
    "_id": "mock_post_id",
    "title": "Test Post for Deletion",
    "content": "This is a test post content for deletion.",
    "user_id": "test_user_id",
}  

# Sample data for creating a post
test_post_create_data = {
    "title": "New Post",
    "content": "Content of the new post",
    "category": "Category of the new post",
    "user_id": "user789"
}

# Sample data for user posts
test_user_posts_data = [
    {
        "title": "User Post 1",
        "content": "Content of user post 1",
        "category": "User Category",
        "user_id": "user123",
        "_id": "userpost123"
    },
    {
        "title": "User Post 2",
        "content": "Content of user post 2",
        "category": "User Category",
        "user_id": "user123",
        "_id": "userpost456"
    }
]  

@pytest.mark.asyncio
@patch("posts_service.main.post_collection.find")
async def test_search_posts(mock_find):
    mock_find.return_value.to_list = AsyncMock(return_value=test_post_data)
    response = client.get("/posts/search?query=test")
    assert response.status_code == 200
    assert len(response.json()) == len(test_post_data)

@pytest.mark.asyncio
@patch("posts_service.main.post_collection.insert_one", new_callable=AsyncMock)
@patch("posts_service.main.post_collection.find_one", new_callable=AsyncMock, side_effect=mock_find_one)
async def test_create_post(mock_find_one, mock_insert):
    mock_insert.return_value.inserted_id = "mock_id"
    response = client.post("/posts/", json=test_post_create_data)
    assert response.status_code == 200

@pytest.mark.asyncio
@patch("posts_service.main.post_collection.find")
async def test_read_user_posts(mock_find):
    mock_find.return_value.to_list = AsyncMock(return_value=test_user_posts_data)
    response = client.get("/posts/user/mock_user_id")
    assert response.status_code == 200
    assert len(response.json()) == len(test_user_posts_data)

def test_delete_post():
    test_post_id = '507f1f77bcf86cd799439011'

    # Mocking the delete_one method to return a valid result
    post_collection.delete_one = AsyncMock()
    post_collection.delete_one.return_value.acknowledged = True
    post_collection.delete_one.return_value.deleted_count = 1

    # Make the delete request to the delete_post endpoint
    response = client.delete(f"/posts/{test_post_id}")

    # Assert the response status code
    assert response.status_code == 204

