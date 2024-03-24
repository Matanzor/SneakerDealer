# backend/users_service/tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from .main import app  
from .database import user_collection  
from unittest.mock import AsyncMock, patch
from bson.objectid import ObjectId
import bcrypt

client = TestClient(app)

def get_hashed_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


mock_user_data = {
    "_id": ObjectId('507f1f77bcf86cd799439011'),
    "username": "test_user",
    "email": "test@example.com",
    "full_name": "Test User",
    "hashed_password": get_hashed_password("test_password")
}


test_user_create_data = {
    "username": "new_user",
    "email": "new_user@example.com",
    "full_name": "New User",
    "password": "new_password"
}

@pytest.mark.asyncio
@patch("users_service.main.user_collection.find_one", new_callable=AsyncMock)
async def test_get_user(mock_find_one):
    mock_find_one.return_value = mock_user_data
    user_id = '507f1f77bcf86cd799439011'
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["username"] == "test_user"

@pytest.mark.asyncio
@patch("users_service.main.user_collection.insert_one", new_callable=AsyncMock)
@patch("users_service.main.user_collection.find_one", new_callable=AsyncMock)
async def test_create_user(mock_find_one, mock_insert):
    mock_find_one.return_value = None  

    # Simulate the behavior of MongoDB's insert_one operation more accurately
    mock_insert.return_value = AsyncMock(inserted_id=ObjectId('507f1f77bcf86cd799439011'))
    mock_insert.return_value.acknowledged = True

    # Simulate the behavior of find_one after inserting a new document
    mock_user_after_insert = mock_user_data.copy()
    mock_user_after_insert['_id'] = ObjectId('507f1f77bcf86cd799439011')
    mock_find_one.side_effect = [None, mock_user_after_insert]  # None for the first call, mock_user_data for the second

    response = client.post("/users/", json=test_user_create_data)

    mock_insert.assert_called_once()  
    assert response.status_code == 200, response.json()  # Provide response details if assertion fails



@pytest.mark.asyncio
@patch("users_service.main.user_collection.find_one", new_callable=AsyncMock)
async def test_login(mock_find_one):
    mock_find_one.return_value = mock_user_data
    response = client.post("/token", data={"username": "test_user", "password": "test_password"})
    assert response.status_code == 200
    assert response.json()["access_token"] == "test_user"


