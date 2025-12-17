from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from src.config import GOOGLE_CLIENT_ID
from src.auth.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
class DevLoginRequest(BaseModel):
    email: str = "demo@matcha.app"

@router.post("/dev-login")
def dev_login(body: DevLoginRequest):
    token = create_access_token(subject=body.email)
    return {"access_token": token, "token_type": "bearer"}

class GoogleLoginRequest(BaseModel):
    id_token: str

@router.post("/google")
def google_login(body: GoogleLoginRequest):
    try:
        info = id_token.verify_oauth2_token(
            body.id_token,
            grequests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google ID token")

    email = info.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Google token missing email")

    api_jwt = create_access_token(subject=email)
    return {"access_token": api_jwt, "token_type": "bearer"}
