from fastapi import APIRouter, Request
from db import db  # Assuming you have a db client here
from ml_chat_analysis import gemini  # Or however you use Gemini API

chatbot_router = APIRouter()

@chatbot_router.post("/chatbot/query")
async def answer_chat_query(request: Request):
    data = await request.json()
    user_id = data["userId"]
    query = data["query"]

    session = db.sessions.find_one(
        {"userId": user_id}, sort=[("timestamp", -1)]
    )

    if not session:
        return {"reply": "No recent session found for this user."}

    prompt = f"""
    You are an AI assistant helping users understand their own chat analysis.

    Summary: {session['summary']}
    Sentiment: {session['sentiment']}
    Tags: {', '.join(session['tags'])}
    Messages: {session['messages'][-10:]}

    User question: {query}
    """

    result = gemini.generate_content(prompt)
    return {"reply": result.text}
