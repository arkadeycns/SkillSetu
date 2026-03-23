import os
import jwt
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

CLERK_PEM_PUBLIC_KEY = os.getenv("CLERK_PEM_PUBLIC_KEY")
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifies the Clerk JWT token passed in the Authorization header.
    Returns the Clerk user_id.
    """
    token = credentials.credentials
    
    if not CLERK_PEM_PUBLIC_KEY:
        raise HTTPException(status_code=500, detail="Clerk public key not configured.")

    try:
        # Format the key correctly for PyJWT
        public_key = f"-----BEGIN PUBLIC KEY-----\n{CLERK_PEM_PUBLIC_KEY}\n-----END PUBLIC KEY-----"
        
        payload = jwt.decode(
            token, 
            public_key, 
            algorithms=["RS256"]
        )
        return payload.get("sub") # 'sub' is the Clerk User ID
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")