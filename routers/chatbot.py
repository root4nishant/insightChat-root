from fastapi import APIRouter, Request, Depends, HTTPException
from db import db
from utils import gemini_chatbot_response
from middleware.auth import get_current_user

chatbot_router = APIRouter()

@chatbot_router.post("/chatbot/query")
async def answer_chat_query(request: Request, user_id: str = Depends(get_current_user)):
    data = await request.json()
    query = data.get("query", "")

    # Step 1: Get user's current token count
    user = await db.users.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("tokens", 0) < 2:
        raise HTTPException(status_code=402, detail="Not enough tokens")

    # Step 2: Fetch last analysis
    session = await db.chats.find_one({"user_id": user_id})
    if not session or "analysis" not in session:
        return {"reply": "No recent analysis found to answer your question."}

    # Step 3: Call Gemini to answer the query
    reply = await gemini_chatbot_response(session["messages"], query)

    # Step 4: Deduct 2 tokens
    await db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"tokens": -2}}
    )

    return {"reply": reply}
