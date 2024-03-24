from pymongo import MongoClient

mongo_uri = "mongodb+srv://admin:admin123123@cluster0.xrhcmq8.mongodb.net/?retryWrites=true&w=majority"
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import FileResponse, StreamingResponse
from fastapi import FastAPI, Depends, HTTPException, Query, Path, File, UploadFile
from typing import List
from database import post_collection, reply_collection, image_collection
from schemas import PostSchema, PostCreate, PostUpdate, ReplyCreate, ReplySchema
# from .database import post_collection, reply_collection, image_collection
# from .schemas import PostSchema, PostCreate, PostUpdate, ReplyCreate, ReplySchema
from bson import ObjectId
import logging
from io import BytesIO
from httpx import AsyncClient
import os

USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://localhost:8000')

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

logging.basicConfig(level=logging.DEBUG)
@app.on_event("startup")
async def create_indexes():
    await post_collection.create_index([
        ('username', 'text'),
        ('title', 'text'),
        ('content', 'text')
    ])
@app.get("/posts/search", response_model=List[PostSchema])
async def search_posts(query: str = Query(None, min_length=3)):
    search_results = post_collection.find({"$text": {"$search": query}})
    results = await search_results.to_list(length=100)
    return [{"id": str(post["_id"]), **post} for post in results]

async def get_current_username(token: str = Depends(oauth2_scheme)):
    async with AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}/users/{token}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        user_data = response.json()
        return user_data["username"] 

@app.delete("/replies/{reply_id}", status_code=204)
async def delete_reply(reply_id: str, user_id: str = Query(...)):
    try:
        reply_id = ObjectId(reply_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid reply_id")

    # Fetch the reply to ensure it exists and belongs to the user attempting to delete it
    reply = await reply_collection.find_one({"_id": reply_id, "user_id": user_id})
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found or access denied")

    delete_result = await reply_collection.delete_one({"_id": reply_id, "user_id": user_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reply not found or access denied")
    return {"ok": True}

@app.get("/posts/user/{user_id}", response_model=List[PostSchema])
async def read_user_posts(user_id: str = Path(..., description="The user ID to filter posts by")):
    user_posts_cursor = post_collection.find({"user_id": user_id})
    user_posts = await user_posts_cursor.to_list(length=100)
    return [{"id": str(post["_id"]), **post} for post in user_posts]

@app.get("/posts/", response_model=List[PostSchema])
async def read_all_posts():
    posts_cursor = post_collection.find({})
    # Create a list of posts with 'id' field included
    posts = await posts_cursor.to_list(length=100)
    # Map '_id' to 'id' for each post
    return [{"id": str(post["_id"]), **post} for post in posts]
    
@app.post("/posts/", response_model=PostSchema)
async def create_post(post: PostCreate):
    post_dict = post.dict()
    new_post = await post_collection.insert_one(post_dict)
    created_post = await post_collection.find_one({"_id": new_post.inserted_id})
    return {**created_post, "id": str(created_post["_id"])}  # Ensure "id" is included in the response


@app.put("/posts/{post_id}", response_model=PostSchema)
async def update_post(post_id: str, post_update: PostUpdate):
    updated_post = await post_collection.find_one_and_update(
        {"_id": ObjectId(post_id)},
        {"$set": post_update.dict(exclude_unset=True)}, 
        return_document=True
    )
    if not updated_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"id": str(updated_post["_id"]), **updated_post}

@app.delete("/posts/{post_id}", status_code=204)
async def delete_post(post_id: str):
    try:
        post_id = ObjectId(post_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid post_id")

    delete_result = await post_collection.delete_one({"_id": post_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"ok": True}

@app.post("/replies/", response_model=ReplySchema)
async def create_reply(reply: ReplyCreate):
    reply_dict = reply.dict()
    new_reply = await reply_collection.insert_one(reply_dict)
    created_reply = await reply_collection.find_one({"_id": new_reply.inserted_id})
    return {**created_reply, "id": str(created_reply["_id"])}

@app.get("/replies/{post_id}", response_model=List[ReplySchema])
async def read_replies_for_post(post_id: str):
    replies_cursor = reply_collection.find({"post_id": post_id})
    replies = await replies_cursor.to_list(length=100)
    return [{"id": str(reply["_id"]), **reply} for reply in replies]

@app.post("/images/")
async def upload_image(file: UploadFile = File(...)):
    # Store the image in the database and return its ID
    contents = await file.read()
    result = await image_collection.insert_one({"image": contents})
    return {"image_id": str(result.inserted_id)}

@app.get("/images/{image_id}")
async def get_image(image_id: str):
    image = await image_collection.find_one({"_id": ObjectId(image_id)})
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return StreamingResponse(BytesIO(image["image"]), media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
