# services/auth.py
from fastapi import Depends, HTTPException, Header
from typing import Optional
from clerk import Clerk  # Make sure Clerk SDK is installed

clerk_client = Clerk(api_key="YOUR_CLERK_API_KEY")  # set env variable in production

def get_current_user(x_clerk_session_id: Optional[str] = Header(None)):
    if not x_clerk_session_id:
        raise HTTPException(status_code=401, detail="Missing Clerk session ID")

    try:
        user = clerk_client.sessions.get_session(x_clerk_session_id).user
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Clerk session")