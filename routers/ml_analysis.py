from fastapi import APIRouter, Depends, HTTPException
from ml_chat_analysis import perform_ml_analysis
from middleware.auth import get_current_user
from db import db

ml_router = APIRouter()

@ml_router.get("/ml_analysis")
async def ml_analysis(user_id: str = Depends(get_current_user)):
    user_data = await db.chats.find_one({"user_id": user_id})
    if not user_data or not user_data.get("messages"):
        raise HTTPException(status_code=404, detail="No chat data found.")

    messages = user_data["messages"]
    result = perform_ml_analysis(messages)
    return result
