from fastapi import Request, HTTPException, Depends
import os
import requests
from db import db

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

async def get_current_user(request: Request):
    session_id = request.headers.get("X-Clerk-Session-Id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Missing session ID")

    try:
        # Verify session
        res = requests.get(
            f"https://api.clerk.dev/v1/sessions/{session_id}",
            headers={"Authorization": f"Bearer {CLERK_SECRET_KEY}"}
        )
        data = res.json()

        if res.status_code != 200 or data.get("status") != "active":
            raise HTTPException(status_code=403, detail="Invalid or inactive session")

        user_id = data["user_id"]

        # 🆕 Check or insert user in DB with 50 tokens
        existing = await db.users.find_one({"user_id": user_id})
        if not existing:
            await db.users.insert_one({"user_id": user_id, "tokens": 50})
            print("✅ New user added with 50 tokens:", user_id)

        return user_id

    except Exception as e:
        print("❌ Clerk validation error:", str(e))
        raise HTTPException(status_code=403, detail="Failed to validate session")
