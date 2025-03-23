from fastapi import Request, HTTPException, Depends
import os
import requests

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

async def get_current_user(request: Request):
    session_id = request.headers.get("X-Clerk-Session-Id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Missing session ID")

    # 🔍 Debug log
    print("👉 Session ID received from frontend:", session_id)

    # Verify session with Clerk
    try:
        res = requests.get(
            f"https://api.clerk.dev/v1/sessions/{session_id}",
            headers={"Authorization": f"Bearer {CLERK_SECRET_KEY}"},
        )
        print("🔍 Clerk session validation response:", res.status_code, res.json())  # NEW LINE

        if res.status_code != 200 or res.json().get("status") != "active":
            raise HTTPException(status_code=403, detail="Session is not active")

        user_id = res.json().get("user_id")
        return user_id

    except Exception as e:
        print(" Clerk validation error:", str(e))
        raise HTTPException(status_code=403, detail="Failed to validate session")
