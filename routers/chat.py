from fastapi import APIRouter, Depends, HTTPException
from models import ChatPayload
from utils import gemini_analysis, estimate_tokens
from db import db
from middleware.auth import get_current_user

chat_router = APIRouter()

@chat_router.post("/process_chat")
async def process_chat(payload: ChatPayload, user_id: str = Depends(get_current_user)):
    # Step 1: Check user token balance
    user = await db.users.find_one({"user_id": user_id})
    if user.get("tokens", 0) <= 5:
        await db.chats.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "messages": payload.messages,
                   "analysis": {"summary": "Insufficient token"}
                }
            },
            upsert=True
        )
        raise HTTPException(status_code=402, detail="Not enough tokens")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_tokens = user.get("tokens", 0)
    estimated_tokens = estimate_tokens(payload.messages)

    # if current_tokens < estimated_tokens:
    #     raise HTTPException(status_code=402, detail="Not enough tokens")

    # Step 2: Run Gemini analysis
    analysis = await gemini_analysis(payload.messages)

    # Step 3: Store analysis and deduct tokens
    await db.chats.update_one(
        {"user_id": user_id},
        {"$set": {"messages": payload.messages, "analysis": analysis}},
        upsert=True
    )

    await db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"tokens": -estimated_tokens}}
    )

    return {
        "analysis": analysis,
        "tokens_used": estimated_tokens,
        "tokens_remaining": current_tokens - estimated_tokens
    }

@chat_router.get("/get_analysis")
async def get_analysis(user_id: str = Depends(get_current_user)):
    result = await db.chats.find_one({"user_id": user_id})
    if result:
        return {
            "messages": result.get("messages", []),
            "analysis": result.get("analysis", {})
        }
    return {"messages": [], "analysis": {}}
