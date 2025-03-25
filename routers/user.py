from fastapi import APIRouter, Depends, Request
from db import db
from middleware.auth import get_current_user
# from utils.clerk_auth import verify_clerk_session

user_router = APIRouter()

@user_router.get("/user_info")
async def get_user_info(user_id: str = Depends(get_current_user)):
    user = await db.users.find_one({"user_id": user_id})
    if not user:
        return {"error": "User not found"}
    
    return {
        "user_id": user["user_id"],
        "tokens": user.get("tokens", 0),
    }


@user_router.post("/init_user")
async def init_user(user_id: str = Depends(get_current_user)):
    existing_user = await db.users.find_one({"user_id": user_id})
    
    if existing_user:
        return {"message": "User already initialized", "tokens": existing_user.get("tokens", 0)}
    
    await db.users.insert_one({
        "user_id": user_id,
        "tokens": 50 
    })

    return {"message": "User initialized", "tokens": 100}

@user_router.post("/confirm_payment")
async def confirm_payment(data: dict):
    user_id = data.get("user_id")
    tokens = data.get("tokens", 0)

    await db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"tokens": tokens}},
        upsert=True
    )
    return {"status": "success"}
