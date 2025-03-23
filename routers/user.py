from fastapi import APIRouter, Request
from utils.clerk_auth import verify_clerk_session

router = APIRouter()

@router.get("/me")
def get_user_info(request: Request):
    session_id = request.headers.get("X-Clerk-Session-Id")
    if not session_id:
        return {"error": "Missing session ID"}

    user_id = verify_clerk_session(session_id)
    return {"message": "Verified!", "user_id": user_id}
