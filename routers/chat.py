from fastapi import APIRouter, Depends
from models import ChatPayload
from utils import gemini_analysis  # ✅ new import
from db import db
from middleware.auth import get_current_user

chat_router = APIRouter()

@chat_router.post("/process_chat")
async def process_chat(payload: ChatPayload, user_id: str = Depends(get_current_user)):
    analysis = await gemini_analysis(payload.messages) 

    await db.chats.update_one(
        {"user_id": user_id},
        {"$set": {"messages": payload.messages, "analysis": analysis}},
        upsert=True
    )

    return {"analysis": analysis}


@chat_router.get("/get_analysis")
async def get_analysis(user_id: str = Depends(get_current_user)):
    result = await db.chats.find_one({"user_id": user_id})
    if result:
        return {
            "messages": result.get("messages", []),
            "analysis": result.get("analysis", {})
        }
    return {"messages": [], "analysis": {}}
